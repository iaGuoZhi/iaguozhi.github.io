---
title: Run Linux on QEMU
date: 2022-06-14
legacy_url: yes
---

# 面向服务器

## 通过virt-install

使用libvirt提供的cli来起虚拟机

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

上面代码展示的是通过在网络拉取Ubuntu提供的Ubuntu18.04启动镜像来起Linux虚拟机。也可以自己制作或者下载启动镜像然后通过virt-install启动虚拟机:

通过libvirt启动的虚拟机，在启动成功之后可以通过virsh cli进行管理.
比如:

```
virsh list  // 查看所有虚拟机
virsh domifaddr $domain   // 查看虚拟机的ip
virsh console $domain    // 进入虚拟机的console, 如果console没有输出，是需要虚拟机打开console 服务
virsh destroy $domain    // 关闭虚拟机，并不会删除磁盘文件，能够再次重启
virsh dumpxml $domain > a.xml  // dump出虚拟机的xml文件
virsh define a.xml      // 修改虚拟机参数后，定义虚拟机
virsh start $domain     // 启动虚拟机
```

## 通过qemu-system-x86\_64 

首先下载好虚拟机操作系统的iso文件。

```
./qemu/build/qemu-system-x86_64 \
    -cdrom /path/to/archlinux-2021.07.01-x86_64.iso \
    -cpu host \
    -enable-kvm \
    -m 8G \
    -smp 8 \
    -nographic \
```

# 面向嵌入式

嵌入式环境比较复杂，需要自己制作intrd(initramfs, 是虚拟机的rootfs，在上面用Ubuntu或者Arch发行版启动虚拟机中，发行版已经准备了非常大的rootfs文件，因此不用自己制作)，并用Linux源码编译kernel.

这里只提供了命令，具体的步骤在[stdrc](https://stdrc.cc/post/2020/09/12/minimal-linux-with-busybox/)中已经有非常详细的介绍了。

```
./qemu-5.0.0/build/aarch64-softmmu/qemu-system-aarch64 \
    -machine virt -cpu cortex-a53 -smp 1 -m 2G \
    -kernel ./linux-5.8.8/build/arch/arm64/boot/Image \
    -append "console=ttyAMA0" \
    -initrd ./busybox-1.32.0/build/initramfs.cpio.gz \
    -nographic
```


## 参考

https://graspingtech.com/creating-virtual-machine-virt-install/

https://wiki.qemu.org/Hosts/Linux

https://stdrc.cc/post/2020/09/12/minimal-linux-with-busybox/

