---
title: hugepage 论文阅读
date: 2022-07-28
---

组会上读了三篇大页有关的论文，分别是

| 论文 | 会议 |
| ---  | ---  |
| Making Huge Pages Actually  Useful | ASPLOS 18 |
| HawkEye: Efficient Fine-grained OS Support for Huge Pages| ASPLOS 19 |
| CBMM: Financial Advice for Kernel Memory Managers | ATC 22 |

将笔记整理出来。

## 关于大页


### obvious hugepage pros

- 减少TLB miss
- 减少page fault

### Memory reclaim

当内存水位不足时会触发内存回收

### Memory compaction

如果内存碎片化严重，会有一个内核线程进行内存compaction。

### Cons of hugepage

- **hugepage会触发memory reclaim和memory compaction造成应用不可接受的延迟（ms甚至是s级别）**
所以，Redis, MongoDB 和其他应用都建议用户关闭Linux的Transparent Huge Page(THP)特性。

于是有一系列的工作来提升huge page的可用性。

### [ASPLOS 18] Making Huge Pages Actually Useful.

Linux中大页需要进行compaction，来获得连续的地址空间来分配大页。但是存在着unmovable pages(是因为kernel address space是direct mapping，没有页表。因此kernel object所在的页都是unmovable）。

Linux应对这个问题的解决办法是在物理内存层次对内核与用户态进行划分。一个page block(hugepage大小，eg, 2M)要么是movable(分配用户态的页），要么是unmovable(分配内核态的页)。不过尽管如此，Linux中大页在compaction进行时的时延仍然不能够接受。

作者通过分析发现了是由于unmovable page以及当前实现导致的几个问题引起的:

1. polltion, unmovable block如果不够用会向movable block借用page，导致最后都是hybrid，一个block既有movable的page和unmovable的page）。
2. unsuccessful migration, Linux会尝试通过migrate页来进行compaction，但是在compact过程中发现了一个页面中有unmovabel page时，这个block依旧是hybrid，依旧不能够作为大页给分配，导致了这个compaction过程不但没有发挥作用，还浪费了CPU cycles，tlb。
3. RCU的广泛应用导致了unmovable pages数量增加，加重了以上两个问题。

这些问题的背后的核心就是内核没有对hybrid page block 进行处理。在第一个问题，如果内核能够识别hybrid block，就能够在hybrid block中分配空闲页作为unmovable page，而不用pollute 所有的blocks。对于第二个问题，如果内核能够识别hybrid block，就不会在要分配hugepage的时候，对这个hybrid block进行无效的compaction。

因此作者在Linux上实现了Illuminator，能够针对hybrid block进行处理。根据测试，在overall performance测试中，mysql最差情况下的查询延迟从1-4s下降到了0.1s以下。

## [ASPLOS 19] HawkEye: Efficient Fine-grained OS Support for Huge Pages


随着现代硬件的内存越来越大，地址转换的开销变得不可忽视，Hugepage可以有效的减轻MMU压力，但是如何设计高效的大页管理方案，对于开发者而言仍然属于比较头疼的问题；之前的研究论文Ingens通过分析内核的页面访问模式和硬件性能计数器中的数据，发现linux的大页管理策略在**地址转换性能、缺页时延及内存膨胀**（memory bloat）等方面都存在着较大的缺陷。

ASPLOS 19的HawkEye这篇论文提出了一种新型的大页管理方案HawkEye，HawkEye管理算法的主要思想包括：异步页面预清零、全零页面去重、页访问精细化跟踪以及通过硬件性能计数器的地址转换开销测量，研究数据表明，HawkEye拥有更高的性能以及更健全的功能，在各种工作负载下的表现都比linux更加优秀。

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d0d88c7d-d912-4099-a448-86f85d4e6c39/Untitled.png)

上图显示了HawkEye的主要设计思路，HawkEye的整体解决方案基于四个关键因素：

1. 使用异步页面预清零方案来解决大页缺页时的时延过高问题
    异步页面预清零是一种较为常见的机制，通常是通过创建一个cpu使用受限的后台线程来实现，这种方式早在2000年左右就被提出来了，但是linux的开发人员认为这种方案并不能带来性能提升，主要基于以下两个理由：
    0. 异步预清零会对cache造成很大的污染，特别是容易造成多次cache misses，因为它在两个进程空间对连续的大片内存进行两次远距离的访问，第一次是后台线程中的预清零，然后是在应用程序中的实际访问，这种额外的cache miss会导致系统整体性能的下降。但是现在大部分硬件已支持non-temporal指令，预清零通过non-temporal方式进行写入，可以跳过cache直接 写到内存中，可以解决cache污染的问题
    1.     2. 没有实际的经验或数据表明预清零可以带来明显的性能收益。但是如表1中的测试数据表明，尽管预清零对于4k页的收益不够明显，但是对于大页而言，清零的耗时占了缺页异常97%的时长，而目前大页已经在各种操作系统中都被广泛应用，预清零的收益会得到显>著的提升
    2. 2. 识别并删除已分配大页中未使用的重复小页来解决内存膨胀问题。
    3.     
    一般应用的内存主要来自以传统方法（如malloc）申请的全零页，剩下的就是文件缓存或写时拷贝申请的页面，而透明大页通常也只用于匿名页中。HawkEye在第一次缺页异常时优先给进程分配大页，但当系统内存压力过大时，会扫描每个大页中的全零小页，如果全>零小页超过一定的比例，就将该大页拆分成为小页，并且利用写时拷贝技术将所有的全零页面合并为一个。部分场景下这的确会导致缺页异常次数变多，但这种做法对减轻内存膨胀的收益更为明显。
3. 基于对大页区域细粒度的访问跟踪，来选择更优的内存范围进行大页合并，跟踪的指标包括新近度、频率和访问覆盖范围（即在大页内访问过多少小页）。
    当前系统的大页合并机制都是从进程的低地址空间扫描到高地址空间，这种方式效率很低，因为进程的热点内存区域不会都在低地址范围内。
    HawkEye 定义一个叫access-coverage的指标，通过定期对大页中各小页的页表访问位进行扫描统计，可以判断在一定时间范围内其中有多少个小页被访问过，从而选择出hot regison进行合并，这样可以显著提高合并后带来的TLB收益。

## [ATC-22] CBMM: Financial Advice for Kernel Memory Managers

数据中心工作负载对内核内存管理（MM）提出了新的挑战。在一个数据中心中内存管理的性能既需要优越，也需要一致（比如延迟稳定）。但是现在MM的设计大多是inconsistent，性能表现难以复现，解读与修复。并且现在Linux中MM的策略分布于大量文件中，开发者难以debug。作者提出了CBMM来取得MM的consisitent behavior。CBMM中，每一个策略都有一个benefit和overhead，通过计算出收益比来确定某个策略（比如是否分配大页）是否采用。CBMM的性能比起LInux和HawkEye更优越（更快，tail latency更稳定）。

作者认为现在的MM存在下面三个问题

### Low-Quality Information

当前MM的设计依靠于运行时的数据分析，比如页表的access/dirty bit，缺页的频率以及位置。但是这些拿到这些信息很昂贵。HawkEye通过内核态硬件性能计数器的地址转换开销信息来分析，但是当前硬件性能计数器不能够给大多数MM策略提供有效信息。

### Cost-Unaware Policies

以大页操作为例，它带来的延迟是不确定的。

### Problem3: Scattered implementations

### CBMM idea

所有的MM操作都有一个对用户态开销与好处。

以Copy-on-write为例

好处： 处理器不需要浪费cycle来拷贝内存

坏处： 处理器需要浪费cycle处理一次额外的page faults

CBMM通过保证操作的开销<好处，来取得更好与更加稳定的性能

### CBMM overview

### Cost-benefit models

CBMM比起之前的工作更加的cost-aware。所以他会造成更少的错误决策，更少的产生不稳定的延迟。

### Cost-benefit models

CBMM比起之前的工作更加的cost-aware。所以他会造成更少的错误决策，更少的产生不稳定的延迟。

## 参考

