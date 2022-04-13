---
title: Xv6 lazy lab
date: 2022-04-01
legacy_url: yes
---

## 什么是Lazy

Lazy是操作系统在管理内存时的重要技巧之一。应用程序在分配内存的时候，操作系统并不会立刻分配，而是当进程在使用这块内存时因为没有页表而产生了缺页异常下陷到kenrel中才进行物理内存的分配与页表映射的建立。其背后的原理是应用程序的代码分配这块内存的时间并不是真正需要使用的时间，因此可以使用lazy的策略来延迟物理内存的分配，从而实现节约物理内存的目的。当然lazy并不是one size fits all，因为lazy在使用时需要下陷，影响了性能，在一些场景中（比如RDMA，JVM）都会提前分配好物理内存，避免在应用运行时出现缺页。

## Lazy allocation

### 处理sbrk

lazy的第一步就是在应用分配内存的时候不分配内存:

```
uint64
sys_sbrk(void)
{
  int addr;
  int n;

  if(argint(0, &n) < 0)
    return -1;
  addr = myproc()->sz;
  if(growproc(n) < 0)
    return -1;
  return addr;
}

int
growproc(int n)
{
  struct proc *p = myproc();
  uint64 sz;

  sz = p->sz;
  if(n > 0){
    if(p->sz + n > TRAPFRAME)
      return 0;
    // do nothing because of lazy alloc
  } else if(n < 0){
    sz = uvmdealloc(p->pagetable, sz, sz + n);
  }
  p->sz = p->sz + n;
  return 0;
}
```

在内核中我们只需在应用程序通过sbrk扩大地址空间时进行lazy映射。因为用户程序只能够通过sbrk向kernel申请内存空间，其他申请用户态内存的方式比如malloc，会由用户态内存分配器进行处理，用户态内存分配器的空闲内存不够时会调用sbrk扩大内存空间。

### 处理缺页

发生下陷后，我们可以通过r\_scause()检查scause寄存器，如果它的值是13或者15说明是缺页异常。

```
else if(r_scause() == 13 || r_scause() == 15){
  // handle page fault trap
  if(handle_page_fault(p->pagetable, PGROUNDDOWN(r_stval())) == -1)
    p->killed = 1;
}
```

下面是page fault handler的代码，需要注意的是在处理page fault的过程中，我们要鉴别这个va是否合法，在Linux中可以通过vma来判断，Xv6中现在的设计比较简单，默认是只要小于sbrk申请出的sz的地址都是合法地址，除了要把栈下面的guard page剔除掉。

除了上面这一点需要特殊考虑外，其他的操作都和uvmalloc类似。

```
static int
valid_fault_va(struct proc *p, uint64 va) {
  uint64 sp = PGROUNDUP(p->trapframe->sp);
  return (va < p->sz) &&
    // not in stack guard page
    !(va >= sp - 2 * PGSIZE && va < sp - PGSIZE);
}

uint64
handle_page_fault(pagetable_t pagetable, uint64 va) {
  uint64 pa0;
  char *mem;

  va = PGROUNDDOWN(va);
  if(!valid_fault_va(myproc(), va))
    return -1;

  mem = kalloc();
  if(mem == 0)
  {
    return -1;
  }
  memset(mem, 0, PGSIZE);
  if(mappages(pagetable, va, PGSIZE, (uint64)mem, PTE_W|PTE_X|PTE_R|PTE_U) != 0){
    kfree(mem);
    return -1;
  }
  pa0 = (uint64)mem;
  return pa0;
}

```

## 处理fork

fork在调用uvmcopy将内存拷贝到子进程的时候，之前会检查物理页是否存在，如果不存在则不合法，实现了lazy之后，允许此时物理页不存在。

## 处理内核直接使用没有映射的虚拟地址

内核在拿到用户态va的时候会进行访问，比如在copyin和copyout中会用用户态va走用户态页表拿到pa然后读数据，如果这时候没有映射物理页，则会直接返回，这样肯定是不对的，因此在这个时候我们需要检查出这种情况，并分配页表。

通过分析代码，发现copyin,copyinstr和copyout都会调用walkaddr拿到物理地址，因此我们只需要更改walkaddr让它在没有找到合法物理页的情况下处理缺页就行。

```
uint64
walkaddr(pagetable_t pagetable, uint64 va)
{
  pte_t *pte;
  uint64 pa;

  if(va >= MAXVA)
    return 0;

  pte = walk(pagetable, va, 0);
  if(pte == 0 || (*pte & PTE_V) == 0)
  {
    pa = handle_page_fault(pagetable, va);
    if(pa == -1)
      return 0;
    pte = walk(pagetable, va, 0);
    if(pte == 0 || (*pte & PTE_V) == 0)
      return 0;
  }
  if((*pte & PTE_U) == 0)
    return 0;
  pa = PTE2PA(*pte);
  return pa;
}
```

除了上面这个操作之外，依然有可能在内核态触发缺页异常（原因未知 TBD)。 因此需要在kerneltrap()中也处理缺页异常。


```
if(r_scause() == 13 || r_scause() == 15) {
  if(handle_page_fault(myproc()->pagetable, PGROUNDDOWN(r_stval())) == -1)
    myproc()->killed = 1;

  if(myproc()->killed)
    exit(-1);
}
```

## 现有的不足

1. 没有vma，不能够在软件层面记录哪些页面有映射，哪些没有。

## 总结

![](../static/lazy_time_spend.png)

## 参考

https://pdos.csail.mit.edu/6.828/2020/labs/lazy.html

https://pdos.csail.mit.edu/6.828/2020/xv6/book-riscv-rev1.pdf
