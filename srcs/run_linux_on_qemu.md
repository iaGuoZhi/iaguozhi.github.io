---
title: Run Linux on QEMU
date: 2022-05-29
legacy_url: yes
hidden: yes
---

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

上面代码展示的是通过ubuntu提供的ubuntu18.04启动镜像来起Linux虚拟机。也可以自己制作启动镜像然后通过virt-install启动虚拟机:

## 通过qemu-system- 

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

