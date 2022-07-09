---
title: 实用的命令行技巧
date: 2022-07-09
legacy_url: yes
---

# 命令

## 系统

### systemctl

```
sudo systemctl start docker
```

### pidof

```
pidof clash
```


## 文本&文件

### tree

### 重定向

### 软链接

### 在浏览器中查看文件

```
python3 -m http.server 8080
```

## 磁盘

### dd
```
dd if=/dev/zero of=virtio_blk.img bs=1M count=1024\nmkfs.ext4 virtio_blk.img
```

### lsblk

### mount

## 网络

### ssh

反向转发, 用来作跳板机
```
ssh -R 8000:localhost:80 user@REMOTE_MACHINE
```
之后用户访问远程主机的8000端口时，将重定位到本地机器的80端口

### ssh-copy-id

拷贝本地的public key到远程机器，之后登录不再需要输入密码

### ifconfig

查看网络设备以及ip
```
ifconfig -a
sudo ifconfig eth0 up
```

### dhclient

很多网络都使用动态主机配置协议(DHCP)来自动获取IP地址:
```
dhclient eth0
```

### ping

测试网络连通性
```
ping 192.168.16.14
```

### lsof

列出正在使用某个开放端口的进程
```
sudo lsof -i -P -n | grep 7890
```

### ip

ip用来起网桥，网桥用于两个独立的网络中传输数据

```
ip link add br0 type bridge
ip link set dev eth1 master br0
# 配置网桥ip
ifconfig br0 10.0.0.2
# 启用分组转发
echo 1 > /proc/sys/net/ipv4/ip_forward
```

### iptables

防火墙设置

```
sudo iptables --policy FORWARD ACCEPT
```

### tcpdump

### arp

## 调试

### gdb

gdb 添加参数
```
sudo gdb --args ./test --batch=2 --no-indirect
```

### dmesg

```
sudo echo "7" > /proc/sys/kernel/printk
```
### debugfs

### objdump

```
aarch64-linux-gnu-objdump -S --start-address=0x401524 ./user/build/vmm/vmm.bin | awk '{print $0} $3-/ret?/{exit}'
```

### qemu

```
qemu-aarch64 bomb
```

### readelf

## 其他

### docker

```
docker run -it 14a6 /bin/bash
```

### ctags

```
ctags -R .
```

### clang-format

```
clang-format -i -style=./.clang-format ./include/qemu/uri.h
```

# Shell 语法

## for

```
for num in {1..5}; do qemu-aarch64 bomb-${num} < ans-${num}.txt; done
```
# 参考
