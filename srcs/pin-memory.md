---
title: Linux中设备要求pin内存的情况分析
date: 2022-08-08
legacy_url: yes
---

## DMA

DMA使用的是内核kmalloc出来的内存，内核的内存本身就是unmovable的， 不需要额外pin。
尽管在驱动代码中有对dma的地址进行map与unmap，但是没有发现pin内存的代码。

## RDMA

注册MR时会pin住内存，待完成通信之后，用户主动注销这片MR。

## SPDK

SPDK作为一个高性能的NVMe用户态驱动框架，通过轮询NVMe寄存器替代传统的中断来降低时延。
SPDK在用户态使用DMA，需要pin住DMA 内存。
SPDK依靠DPDK库来分配pin住的内存，DPDK在Linux中是通过分配大页来实现pin内存的（Linux不会迁移大页)。

## VFIO

在虚拟机通过VFIO使用直通设备的情况下:
若虚拟机内没有IOMMU支持，直通设备地址空间（其能够访问的所有内存）都需要被pin住。
若虚拟机内有IOMMU支持，qemu可以只pin住需要的页，虚拟机在dma\_map\_page下陷时qemu知道虚拟机访问这个页面，将该页面pin住。

## 参考

https://blog.csdn.net/panzhenjie/article/details/51581063
https://spdk.io/doc/memory.html
https://patchwork.kernel.org/project/kvm/patch/20210125090402.1429-5-lushenming@huawei.com/
https://www.usenix.org/conference/atc20/presentation/tian
