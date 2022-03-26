---
title: xv6配置gdb
date: 2022-03-26
legacy_url: yes
---

基于ubuntu20.04, xv6版本: mit 2020

## 安装riscv工具链

下载源码

```sh
$ git clone https://github.com/riscv/riscv-gnu-toolchain
```

安装riscv工具链

```sh
./configure --prefix=/opt/riscv
sudo make linux
```

## 使用gdb

1. 在一个窗口输入`make qemu-gdb`
2. 在另一个窗口中输入`riscv64-unknown-elf-gdb`, 进入gdb后，输入`target remote localhost:26000`, 之后正常使用gdb进行调试。
3. 如果需要避免每次重新输入`target remote localhost:26000`,可以在~/.gitinit中加上`add-auto-load-safe-path ~/path-to-lab/.gdbinit`

## gdb推荐命令

1. step (执行一条c指令)
2. disas (打印当前行所在函数的汇编信息)
3. x/NFU ADDR (打印addr附近内存数据)
4. **layout** (分割窗口，一边查看代码，一边测试）

## 参考

https://github.com/riscv-collab/riscv-gnu-toolchain
https://stackoverflow.com/questions/68611071/how-to-install-riscv64-gdb
https://ipads.se.sjtu.edu.cn/courses/ics/tutorials/gdb-ref.txt
