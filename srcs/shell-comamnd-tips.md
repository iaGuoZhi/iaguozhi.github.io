---
title: 常用的命令行技巧
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

### w

查看当前登录的用户

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

### 动态库

```
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/your/custom/path/
```

## 文本&文件

### cat

制表符显示为^I
```
cat -T file.py
```

### which | whereis

查看软件位置

```
whereis google-chrome-stable
```

### find

找到所有.swp文件并删除
```
find . -type f -name "*.swp" -delete
```

裁剪kernel，删除debug信息（在/boot分区快满了时候是很有必要的)
```
sudo find /lib/modules/4.15.0iommu-v2+ -name *.ko -exec strip --strip-debug {} +  && \
```

### grep

递归替换所有oldtext为newtext
```
grep -rl oldtext . | xargs sed -i 's/oldtext/newtext/g'
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

### chown

将当前目录中所有文件的owner设置为foo:
```
sudo chown -R foo ./
```

### 重定向

同时重定位到文件与stdout

```
./prog 2>&1 | tee outfile
```

### 软链接

```
ln -s /run/media/who/113423 ~/link
```

### vim

直接使用vim查看编辑某函数(需要先使用ctags生成tags文件)
```
vim -t func_name
```

vim 在没有sudo打开文件的情况下强制保存没有权限编辑的文件:

```
w !sudo tee %
```

### 在浏览器中查看文件

在服务器中查看文件很不方便，可以使用这一招，通过静态的Web Server来查看:
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

### fdisk

fdisk 用来给image文件或者磁盘添加分区

以更改虚拟机硬盘大小来介绍使用，假设host想要让vm的磁盘增加至100G, 则host使用qemu-img扩大image大小

```
qemu-img info ./dick1.img # 查看当前磁盘大小
qemu-img resize ./disk1.img 100G # 将磁盘大小设置为100G
```

在vm启动后，需要创建新分区来使用新增加的磁盘部分:

```
sudo fdisk /dev/vda

# 输入n新建一个分区，head offset与end offset使用默认值，占满整个磁盘

# 输入w 将更改写入磁盘

sudo mkfs.ext4 /dev/vda2 # 格式化刚刚新建的磁盘分区

mount /dev/vda2 ./mnt # 挂载新建分区
```

### swap

```
swapon -s # 检查swap文件是否存在，返回空则不存在

df -hal # 查看文件系统，检查空间是否足够创建swap

mkdir /swap # 创建一个swap目录

dd if=/dev/zero of=/tmp/swapfile bs=1024 count=2048000 # 创建并允许swap文件

mkswap -f /tmp/swapfile # 格式化swap文件

swapon /tmp/swapfile # 激活swap

/tmp/swapfile swap swap defaults 0 0 # vim 打开 /etc/fstab 添加这一行设置开机自启动
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

### curl

通过curl 安装pip
```
curl -sS https:# bootstrap.pypa.io/get-pip.py | sudo python3
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

### sysfs

pci设备与驱动绑定:

```
echo 0000:00:19.0 > /sys/bus/pci/drivers/foo/bind
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

看内核代码就能够发现，很多打印的打印级别是debug，默认情况下我们是看不到的，如果我们需要在dmesg中看到内核某个文件中的debug print, 需要:

```
sudo echo 'file drivers/vhost/vhost.c +p' > /sys/kernel/debug/dynamic_debug/control
```

### objdump

objdump用来分析二进制文件, 比如:

```
aarch64-linux-gnu-objdump -S --start-address=0x401524 ./user/build/vmm/vmm.bin | less'
```

### addr2line

将二进制文件中的地址转换成代码中的行

### qemu

运行aarch64格式的可执行文件
```
qemu-aarch64 bomb
```

### readelf

分析elf文件

## 其他

### docker

使用docker运行Latex环境
```
docker run -it --rm -v $(pwd):/paper -w /paper blang/latex /bin/bash
```

### ctags

```
ctags -R .
```

### clang-format

```
clang-format -i -style=./.clang-format ./include/qemu/uri.h
```

格式化目录下所有文件:
```
find ./har -iname "*.h" -o -iname "*.c" | xargs clang-format -style=file -i
```

### 代理

```
export https_proxy=http:# 127.0.0.1:7890 http_proxy=http:# 127.0.0.1:7890 all_proxy=socks5:# 127.0.0.1:7890
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
arr=(${i# \#  })
len=${#arr[@]}
label="normal-${arr[len - 2]}"
```

### 日期

```
mv ~/.vimrc ./backup/vimrc.`date + %F-%T`
```

# 参考
