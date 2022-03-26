---
title: 虚拟化中设备直通的实现
date: 2022-02-18
legacy_url: yes
---

# 虚拟化中设备直通的实现

设备直通的实现大致分为四个部分，分别是直通设备发现，虚拟PCI配置空间，中断重映射，DMA重映射。

## 直通设备发现

### 如何让虚拟机发现直通设备

操作系统初始化时会进行PCI设备的设备枚举，设备枚举从根节点HOST-PCI桥（Header Type为1的PCI设备），首先探测总线0上的各个设备。每当发现一个桥设备，当将它为根节点往下探测，如此反复直到所有设备都被探测完毕。
探测的方法很直接，从0到PCI_SLOTMAX枚举device number，再结合所在总线的bus number与默认的function number（0）组合成bdf，通过将bdf写入CONFIG_ADDRESS(0xcf8端口），然后向CONFIG_DATA中写入值便可以读该个PCI插槽上的PCI设备。通过读取PCI设备"Vendor ID"和"Device ID"能够知道这个PCI设备是否存在。如果发现该设备一个PCI-PCI桥，则创建一个pci_bus数据结构并且连入到由pci_root_buses指向的pci_bus和pci_dev数据结构组成的树中。

### 直通设备发现的关键步骤

#### 截获操作系统对PCI总线的访问（CONFIG_ADDRESS,CONFIG_DATA)

HV将0xcf8端口与0xcfc端口从VMCS中的IO位图中关闭，操作系统对这两个端口的访问将下陷到hypervisor中。

#### 将直通设备记录在pci_vdevs数组中

HV需要对每个虚拟机模拟对应的PCI总线，记录当前给虚拟机模拟的PCI设备，当给UOS assign一个直通设备时，需要给这个设备建立一个vdev结构体，并将其加入到UOS对应的pci_vdevs数组中，当操作系统对PCI设备进行枚举时，能够发现到这个直通设备。

## 虚拟PCI配置空间

设备直通的一个关键点是让虚拟机能够访问设备的真实IO空间，它的关键是虚拟机对设备PCI配置空间的访问。

### PCI配置空间介绍

CONFIG_ADDRESS

![](../static/config_address.png)

x86平台上操作系统通过IO端口0xCF8-0xCFF访问PCI设备，前32位是CONFIG_ADDRESS,后32位是CONFIG_DATA，CONFIG_ADDRESS中包括BDF和register number，可以索引到PCI设备上的寄存器。

### 预定义头部

![](../static/configuration_space.png)

- Header Type 决定PCI设备类型，共有三种类型：普通PCI设备，PCI桥，CardBus桥，每种PCI设备的配置空间结构都不相同，上图展示的是普通PCI设备的配置空间。
- Base Address Registers，基地址寄存器，它记录PCI寄存器或者设备RAM在I/O端口（或者物理地址空间）的地址。
- Capabilities Pointer，capabilities list的头指针
- Interrupt Pin，Interrupt Line，设备中断引脚与中断线

### 为什么要虚拟PCI配置空间

PCI配置空间包括预定义头部（predefined header region）与设备相关部分（device dependent region）。预定义头部除了包括vendor id，device id，type之外，还包括了六个bar register。PCI设备有自己的板上存储空间，这些存储空间映射的系统软件的地址空间中，它们具体的地址就存在于bar register中。由于虚拟机不能够直接访问物理内存，所以它也不能够直接访问存储了物理地址的bar register。
设备相关部分包括了PCI MSI中断信息，MSI通过在PCI配置空间中存储中断对象与中断号，能够绕过IOAPIC，直接向LAPIC发起中断。如果虚拟机可以直接读写真实设备的设备相关部分，它将有能力向其他核或者其他虚拟机发起中断。这是不可行的。
因此虚拟机监控器需要针对直通设备虚拟出PCI配置空间。

### 如何虚拟PCI配置空间

1. HV 启动时深度优先扫描并记录所有的PCI总线与设备
2. 关闭I/O bitmap让虚拟机对PCI设备的端口访问产生下陷（正如前文介绍，虚拟机通过CONFIG_ADDRSS与CONFIG_DATA两个端口访问PCI设备）。
3. 建立转换表，报告虚拟的PCI BAR给虚拟机，当虚拟机通过IO端口访问PCI设备（操作系统只能通过端口0xCF8，0xCFC访问PCI设备配置空间）时，HV可以截获操äect/minos

PCIE_Base_Specification_Revision_4_0_Version 1_0.pdf
vt-directed-io-spec.pdf
https://zhuanlan.zhihu.com/p/326412992
https://luohao-brian.gitbooks.io/interrupt

