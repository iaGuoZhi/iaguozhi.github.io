---
title: zram 的使用
date: 2023-05-08
---

## zram vs zswap

zram 是将swap out的页面压缩保存在内存中, 内存是swap出的工作集最终存放的位置，而zswap是将swap out的页面先压缩再swap到磁盘设备,磁盘是最终保存swap出的工作集的位置。

## zram 安装

首先检查Linux kernel的config中有没有打开zram(在Block目录下)和对应的压缩算法，例如lz4(在Cryptographic API目录下).

### Arch

```
sudo pacman -S zram
```

编辑zram-generator.conf

```
# /etc/systemd/zram-generator.conf
[zram0]
zram-size = (ram / 2)
ptions = X-mount.mode=1777
```

重启后，能够使用zram来做swap

### Ubuntu

直接安装
```
sudo apt install zram-config
```

重启即可

### Fedora

Fedora 33以及以上的版本默认开启了zram. 在32以及一下需要以下操作

安装相关包:
```
sudo dnf install zram # 安装后，能够通过systemctl status zram-swap 看到这个服务的状态
sudo dnf install zram-generator
```

编辑zram-generator.conf

```
# /etc/systemd/zram-generator.conf
[zram0]
zram-size = (ram / 2)
ptions = X-mount.mode=1777
```

无需重启，直接运行

```
systemctl enable zram-swap.service
systemctl start zram-swap.service
```

此时zram就出现在了/dev目录下，并作为swap的后端

## Zram和磁盘上的swap文件性能对比

## 参考

https://www.reddit.com/r/linux/comments/11dkhz7/zswap_vs_zram_in_2023_whats_the_actual_practical/

https://superuser.com/questions/1727160/zram-vs-zswap-for-lower-end-hardware#:~:text=Unlike%20ZSWAP%2C%20what%20ZRAM%20does,it%20tries%20to%20compress%20data.

https://fosspost.org/enable-zram-on-linux-better-system-performance/

https://opensource.com/article/22/11/zram-swap-linux
