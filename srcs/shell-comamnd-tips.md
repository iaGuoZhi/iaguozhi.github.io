---
title: 实用的命令行技巧
date: 2022-07-09
legacy_url: yes
---

# 命令

## 系统

### uname

查看内核版本
```
uname -a 
```

### screenfetch

展示重要的系统信息，有一个发行版的ascii logo

### proc

查看启动参数
```
cat /proc/cmdline
```
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

### crontab

定时任务

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

### uniq

过滤文件的相同行

### mktemp

在当前目录下创建一个临时文件:
```
mktemp -p .
```

### tree

目录与文件树形显示

### 重定向

同时重定位到文件与stdout

```
./prog 2>&1 | tee outfile
```

### 软链接

```
ln -s /run/media/who/113423 ~/link
```

### 在浏览器中查看文件

```
python3 -m http.server 8080
```

### 使用数字切换位置

1切换到上一个使用过的位置, 以此类推

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

查看所有的磁盘

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

利用debugfs能够观测到非常多有用的信息, 比如想要kvm 因为mmio缺页下陷的次数:
```
cat /sys/kernel/debug/kvm/mmio_exists
```

### objdump

objdump用来分析二进制文件, 比如:

```
aarch64-linux-gnu-objdump -S --start-address=0x401524 ./user/build/vmm/vmm.bin | awk '{print $0} $3-/ret?/{exit}'
```

### addr2line

将二进制文件中的地址转换成代码中的行

### qemu

```
qemu-aarch64 bomb
```

### readelf

分析elf文件

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

### 代理

```
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 all_proxy=socks5://127.0.0.1:7890
```

# Shell 语法

### 比较

```
if [ $drivers_results_num -eq $drivers_sources_num ] && [ $normal_results_num -eq $normal_results_num ];
```

### if

```
if [ -e $path ]; then
    echo "File exists";
else
    echo "Does not exist";
fi
```
### for

统计每个目录中的文件数量:
```
for d in `find . -type d`;
    do
    echo `find $d -type t | wc -l ` files in $d;
done
```

### 字符串

对于格式为`drivers/pci/endpoint/built-in.ll`类型的字符串，取出endpoint
```
arr=(${i//\// })
len=${#arr[@]}
label="normal-${arr[len - 2]}"
```

### 日期

```
mv ~/.vimrc ./backup/vimrc.`date + %F-%T`
```

# 参考
