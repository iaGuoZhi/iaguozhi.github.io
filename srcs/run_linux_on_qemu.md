---
title: 通过Qemu来运行Linux的多种方法
date: 2022-07-08
legacy_url: yes
---

# 面向服务器

## 通过libvirt(最简单)

使用libvirt提供的cli来起虚拟机, 本质上还是使用qemu来运行虚拟机的，libvirt是一套比较好操作的脚手架。

通过libvirt可以使用已经下载好的kernel镜像文件进行启动，也可以直接从网络中拉取kernel镜像（这个是最方便的，只需要执行命令即可), 这里给出通过网络拉取镜像的一个例子，可以直接复制下面的命令来启动一个虚拟机:

```
virt-install \
--name falcon-1 \
--ram 1024 \
--disk path=/var/lib/libvirt/images/falcon1.img,size=8 \
--vcpus 1 \
--virt-type kvm \
--os-type linux \
--os-variant ubuntu18.04 \
--graphics none \
--location 'http://archive.ubuntu.com/ubuntu/dists/bionic/main/installer-amd64/' \
--extra-args "console=tty0 console=ttyS0,115200n8"
```

通过libvirt启动的虚拟机，在启动成功之后可以通过virsh cli进行管理.
比如:

```
virsh list  // 查看所有虚拟机
virsh domifaddr $domain   // 查看虚拟机的ip
virsh console $domain    // 进入虚拟机的console, 如果console没有输出，是需要虚拟机打开console 服务
virsh destroy $domain    // 关闭虚拟机，并不会删除磁盘文件，能够再次重启
virsh dumpxml $domain > a.xml  // dump出虚拟机的xml文件
virsh define a.xml      // 修改虚拟机参数后，定义虚拟机
virsh start $domain --console    // 启动虚拟机
```

其中dumpxml格外有用，能够帮助我们更改虚拟机的配置再启动。

比如在下面这段xml文件中，如果没有`<driver name="qemu"/>`，虚拟机使用的virtio-net backend就是默认的运行在内核态的vhost，加入了之后就是Qemu。

```
<devices>
      <interface type='network'>
      <mac address='02:ca:fe:fa:ce:01'/>   
      <source network='default' bridge='virbr0'/>                
      <target dev='vnet0'/>   
      <model type='virtio'/>
             <driver name="qemu"/>
      <alias name='net0'/>  
      <address type='pci' domain='0x0000' bus='0x01' slot='0x00' function='0x0'/>
      </interface>                                                                                     
</devices>
```

## 通过qemu-system-x86\_64 

首先下载好虚拟机操作系统的iso文件, 这里使用archlinux的iso文件:

```
./qemu/build/qemu-system-x86_64 \
    -cdrom /path/to/archlinux-2021.07.01-x86_64.iso \
    -cpu host \
    -enable-kvm \
    -m 8G \
    -smp 8 \
    -nographic \
```

## 启动之后

启动之后建议进行几个设置:

1. 在系统安装过程中选中OpenSSH Server进行安装，如此才能够通过ssh进行连接
2. 开启Console, 在虚拟机(Ubuntu)的`/etc/default/grub`中修改`GRUB\_CMDLINE\_LINUX\_DEFAULT`为
   ```
   GRUB_CMDLINE_LINUX_DEFAULT="console=tty0 console=ttyS0,115200n8"
   ```
这样可以使得即使ssh无法连接，依然能够通过console进入虚拟机。
3. 设置grub，依照下面代码修改`/etc/default/grub`可以使得在console中能够选择kernel再启动，对于需要经常修改kernel的时候很方便:

```
GRUB_TIMEOUT_STYLE=menu
GRUB_TIMEOUT=10
```

修改之后需要通过`sudo update-grub`更新grub。

# 面向嵌入式

嵌入式环境比较复杂，需要自己制作intrd(initramfs, 是虚拟机的rootfs，在上面用Ubuntu或者Arch发行版启动虚拟机中，发行版已经准备了非常大的rootfs文件，因此不用自己制作)，并用Linux源码编译kernel.

首先展示一个使用qemu启动bzImage的命令，这个虚拟机拥有一个disk磁盘与网络:

```
../qemu/build/qemu-system-x86_64 \
    -cpu qemu64 -smp 2 -m 2048M \
    -kernel ./linux/arch/x86_64/boot/bzImage \
    -append "console=ttyS0 nokaslr root=/dev/vda rootwait" \
    -initrd ./initramfs/initramfs.cpio.gz -nographic \
    -device virtio-blk,drive=image \
    -drive if=none,id=image,file=virtio_blk.img,format=raw \
    -netdev user,id=net0 -device virtio-net-pci,netdev=net0
```

接着结合上面的命令逐个参数进行介绍:

## bzImage

在kernel源码中使用make命令即可编程出来

## initrd

一般来说，桌面，服务器中的Linux都需要使用initrd(initramfs)。部分嵌入式系统也会使用initramfs，有时甚至直接将initramfs作为最后系统运行的rootfs。

initramfs的作用是在系统引导过程中，让内核能够正确驱动rootfs所在的设备。

initramfs可以使用几种方式来制作:

* busybox, [stdrc](https://stdrc.cc/post/2020/09/12/minimal-linux-with-busybox/)中已经有非常详细的介绍。
* buildroot, 比起busybox更加现代。

如果不想制作initrd文件，可以使用发行版提供的image来启动虚拟机:
```
qemu-system-x86_64 -cpu host -enable-kvm -smp 4 \
    -m 1G \
    -kernel ~/repos/linux/arch/x86/boot/bzImage \
    -append "console=ttyS0 root=/dev/sda1" \
    -hda ./debian.img \
```

## block image

用户在initramfs中作的修改并不会被保存下来，如果需要让应用程序能够持久化保存数据，可以添加一个block image。

block image 可以通过`dd`来制作

```
dd if=/dev/zero of=virtio_blk.img bs=1M count=1024
mkfs.ext4 virtio_blk.img
```

kernel启动之后，可以通过`blkid`指令看到这个block设备，通常是`/dev/vda`, 此时可以使用
```
mount /dev/vda /mnt
```
来挂载这个设备。

## netdev

通过这个参数可以为虚拟机添加网络支持。

上面使用到的命令
```
-netdev user,id=net0 -device virtio-net-pci,netdev=net0
```
是使用qemu作为virtio-net的backend，如果想使用vhost则需要使用tap设备:
```
-netdev tap,id=br0,vhost=on,script=no,downscript=no, -device virtio-net-pci,netdev=br0
```

启动的虚拟机并不会默认拥有ip地址，需要使用udhcpc来配置网络，具体可以参考[dhcp](https://blog.csdn.net/lee244868149/article/details/49249887)。

## chroot

有些时候，我们可能觉得initrd中提供的命令不够，此时我们可以使用主流Linux发行版制作的rootfs来作为我们最后的rootfs(此时甚至可以在kernel中使用Ubuntu的apt安装程序):

以Ubuntu为例，首先下载Ubuntu 20.04的[rootfs](http://cdimage.ubuntu.com/ubuntu-base/releases/20.04/release/ubuntu-base-20.04.1-base-amd64.tar.gz) 文件，
接着在制作block image的时候使用以下指令

```
dd if=/dev/zero of=virtio_blk.img bs=1M count=1024
mkfs.ext4 virtio_blk.img
mkdir -p tmpfs
sudo mount -t ext4 virtio_blk.img tmpfs/ -o loop
sudo cp -r ubuntu20-rootfs/* tmpfs/
sudo sync
sudo umount tmpfs
rmdir tmpfs
```

如此在mount `/dev/vda`之后能够使用`chroot`来更改root文件夹位置, 之后就能够直接使用Ubuntu 20.04提供的用户态程序。

## gdb

直接使用一个bzImage来启动Linux有一个好处，就是可以使用[gdb](https://www.kernel.org/doc/Documentation/dev-tools/gdb-kernel-debugging.rst)来对内核进行调试，此时需要使用`nokaslr`启动参数关闭kaslr。

## 启动之后

使用bzImage+initrd启动时，虚拟机默认不会拥有disk和net，需要根据上述说明开启，可以选择在initramfs中的init程序来执行这些需要开启的操作。

以我BusyBox中的init程序为例:

```
#!/bin/sh

mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs devtmpfs /dev

ifconfig eth0 up
udhcpc

echo -e "\nBoot took $(cut -d' ' -f1 /proc/uptime) seconds\n"

exec /bin/sh
```

就在启动过程中，开启了网络并动态获取了ip。

# 参考

https://graspingtech.com/creating-virtual-machine-virt-install/

https://wiki.qemu.org/Hosts/Linux

https://stdrc.cc/post/2020/09/12/minimal-linux-with-busybox/

https://blog.csdn.net/lee244868149/article/details/49249887

https://docs.google.com/document/d/1qBcZrrnuU-ogKE2qcP5NFoccioWZAMST_SDfE6FDugk/edit#
