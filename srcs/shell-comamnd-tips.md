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

### pidstat

查看每秒中CPU使用最多的10个进程
```
pidstat -u | sort -nr -k 4 | head -5
```

### lspci

显示所有PCI设备的设备名字(出厂型号)
```
lspci -nn
```


## 文本&文件

### cat

制表符显示为^I
```
cat -T file.py
```
### find

找到所有.swp文件并删除
```
find . -type f -name "*.swp" -delete
```

### xargs

将args.txt中的每一行作为参数执行一次exec.sh
```
cat args.txt | xargs -n 1 ./exec.sh
```

### tree

### 重定向

### 软链接

### 在浏览器中查看文件

```
python3 -m http.server 8080
```

## 磁盘

### du

查看各个当前各个目录中文件的总大小
```
du -sh ./*
```

### dd
```
sudo dd if=/dev/zero of=./virtio_blk.img bs=1M count=1024
sudo mkfs.ext3 ./virtio_blk.img
sudo sync
```

### lsblk

### mount
```
mount -o loop=/dev/loop0 ./image ./mnt
```

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

嗅探50个包，并保存
```
tcpdump -w /tmp/tcpdump.raw -c 50
```
查看对应包的头部
```
tcpdump -X -r /tmp/tcpdump.raw host google.com and port http
```

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

挂载debugfs
```
sudo mount -t debugfs none /sys/kernel/debug
```

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

### if

```
if [ -e $path ]; then
    echo "File exists";
else
    echo "Does not exist";
fi
```
### for

```
for num in {1..5}; do qemu-aarch64 bomb-${num} < ans-${num}.txt; done
```
# 参考
