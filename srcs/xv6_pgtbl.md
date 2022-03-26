---
title: Xv6 pgtbl lab
date: 2022-03-26
legacy_url: yes
---

## Xv6 页表介绍

页表是操作系统用来给每一个进程独立的地址空间和内存的机制。一般来说，页表以及其提供的虚拟内存机制为操作系统提供了以下功能:

1. 缓存磁盘数据(swap，page cache)。
2. 管理内存:
   a. 简化连接: 允许每个进程的内存映像使用相同的基本格式(ELF). b. 简化加载: 允许操作系统以lazy的策略加载目标文件. c. 简化共享：静态库，动态库，进程fork时候的copy on write. d. 简化内存分配: 以indirection的方式让进程看到连续的地址空间。 
3. 内存保护: 通过页表的pte bit位进行访问控制，从而提供不同进程之间的隔离。

在Xv6中，页表提供了管理内存与保护内存的功能。

Xv6 跑在Sv39 RISC-V上，这意味着虚拟地址的64个bit只使用了0-38这39个bit。
从下面这张图可以看出Xv6上的page table采用三级架构。
每一级页表大小位512\*8=4096 bytes(4k), 每个页表上有512个entry，每个entry里面有PPN和Flags，PPN(44个bits)作为物理地址用来查找下级页表或者最终翻译结果的物理地址,Flags(10个bits）用来设置页表的权限。 
Xv6中用到的权限位包括PTE\_V,PTE\_R,PTE\_W,PTE\_X,PTE\_U。

![](../static/xv6_page_table.png)

Xv6为一个进程提供了一个用户态页表，并且在内核实现了一个公共的内核页表（在这个lab中，我们需要为每个内核实现独立的页表。下图是Xv6 book提供的关于Xv6 虚拟内存到物理内存映射关系图，可以看到，内核态的虚拟地址处于高地址，而每个进程的用户态虚拟地址空间将被映射在低地址（从0开始）。对于QEMU提供的寄存器和内核代码段，数据段，Xv6采用了直接映射的方式。

![](../static/xv6_va_2_pa.png)

## 打印页表(简单）

pgtbl lab的第一个任务是在拿到内核页表基地址后，将整个页表打印为如下格式:
```
page table 0x0000000087f6e000
..0: pte 0x0000000021fda801 pa 0x0000000087f6a000
.. ..0: pte 0x0000000021fda401 pa 0x0000000087f69000
.. .. ..0: pte 0x0000000021fdac1f pa 0x0000000087f6b000
.. .. ..1: pte 0x0000000021fda00f pa 0x0000000087f68000
.. .. ..2: pte 0x0000000021fd9c1f pa 0x0000000087f67000
..255: pte 0x0000000021fdb401 pa 0x0000000087f6d000
.. ..511: pte 0x0000000021fdb001 pa 0x0000000087f6c000
.. .. ..510: pte 0x0000000021fdd807 pa 0x0000000087f76000
.. .. ..511: pte 0x0000000020001c0b pa 0x0000000080007000
```

由于Xv6中已经有递归释放页表的函数进行参考，这个任务比较简单。我实现该任务的主要函数如下：

因为Xv6 每个页表中有512个entry，因此这个函数会遍历512次，访问每个entry。只有entry中PTE\_V为1的时候，才表明当前entry是有效的。由于最有一级页表的flag会设置PTE\_R等权限位(不存在同时不能够读，写，执行的物理页)，因此可以通过这些flag判断当前是否是最后一级页表，如果不是，则递归打印当前页表项所指向的次级页表。

```
void
static print_single_line(int level, int idx, pte_t pte, uint64 pa);

// Recursively print page-table pages
void
static __vmprint(pagetable_t pagetable, int level)
{
  int i;

  // there are 2^9 = 512 page-table pages.
  for(i = 0; i < 512; ++i){
    pte_t pte = pagetable[i];
    uint64 child = PTE2PA(pte);

    if(pte & PTE_V){
      print_single_line(level, i, pte, child);
      if((pte & (PTE_R|PTE_W|PTE_X)) == 0){
         // this PTE points to a lower-level page table. 
         __vmprint((pagetable_t)child, level + 1);
      }
    }
  }
  return;
}
```

## 每个进程一个内核页表(困难)

## 简化copyin/copyinstr(困难)

## 参考

https://pdos.csail.mit.edu/6.828/2020/labs/pgtbl.html
https://pdos.csail.mit.edu/6.828/2020/xv6/book-riscv-rev1.pdf
https://csapp.cs.cmu.edu/
