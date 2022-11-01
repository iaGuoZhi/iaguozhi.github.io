---
title: KVM的ept机制(x86)
date: 2022-11-01
legacy_url: yes
---

## 术语

pfn: 宿主机物理页帧数
hpa: 宿主机物理地址
hva: 宿主机用户态虚拟地址
gfn: 虚拟机物理页帧
gpa: 虚拟机物理地址
gva: 虚拟机虚拟地址
ngpa: 嵌套虚拟机物理地址
ngva: 嵌套虚拟机虚拟地址
pte: 页表项，指向下一级页表的物理地址
gpte: 虚拟机中的页表项，指向gpa
spte: 宿主机中的页表项，指向hpa
tdp: 两阶段页表(Intel称为EPT, AMD称为NPT)

## kvm\_tdp\_page\_fault

在发生tdp violation之后，KVM将执行`kvm_tdp_page_fault`，这个函数将做两个事情，一个是通过函数`kvm_faultin_pfn`用gpa找到需要映射上的pfn，一个是通过函数`kvm_tdp_mmu_map`将gpa到hpa的映射添加进入tdp页表中。

### kvm\_faultin\_pfn

```
kvm_tdp_page_fault
-direct_page_fault
--kvm_fualtin_pfn
---__gfn_to_pfn_memslot
----__gfn_to_hva_many. //拿到hva
----hva_to_pfn         // 映射hva到物理页面
-----hva_to_pfn_fast
------get_user_page_fast_only. // get_user_page的快速实现版本, 不是通过触发page fault拿到物理地址，而是直接走页表
-------get_user_pages_fast_only
--------internal_get_user_pages_fast
---------lockless_pages_from_mm
----------gup_pgd_range. //. 通过走页表的方式找到PTE entry里面的物理页 
--kvm_tdp_mmu_map
---tdp_mmu_map_handle_target_level
```

### kvm\_tdp\_mmu\_map

```
kvm_tdp_page_fault
-direct_page_fault
--kvm_tdp_mmu_map
---tdp_mmu_map_handle_target_level
```

## 参考

1. https://lwn.net/Articles/832835/

2. https://www.cnblogs.com/scu-cjx/p/6878568.html

3. https://www.kernel.org/doc/Documentation/virtual/kvm/mmu.txt
