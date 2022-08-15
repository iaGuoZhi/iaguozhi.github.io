---
title: 使用VFIO给虚拟机提供直通设备的步骤
date: 2022-08-08
legacy_url: yes
---

## VFIO 介绍

VFIO 让虚拟机直接使用每个PCI设备，以达到接近native的IO性能。

使用VFIO的场景如下：

* 提升性能(如直通网卡和显卡）
* 减少延迟(避免数据丢失或者丢帧）
* 直接使用bare-metal上设备的驱动

## 使用步骤

### 硬件要求

1. CPU和主板均支持VT-d
2. IO设备（如NVMe）支持SRIOV

### unbind PCI设备

以NVMe设备为例


```
# 加载vfio-pci模块
modprobe vfio-pci
# 查询NVMe设备的(domain,slot,bus,function)和(vendor id, device id )
lspci -D -nn | grep NVM
```

lspci结果如下:

```
0000:5e:00.0 Non-Volatile memory controller [0108]: Intel Corporation NVMe Datacenter SSD [Optane] [8086:2701]
```

然后执行

```
# 将NVMe设备从原来的IOMMU group中unbind
sudo bash -c 'echo 0000:5e:00.0 > /sys/bus/pci/devices/0000:5e:00.0/driver/unbind'
# 将NVMe设备bind到vfio-pci下
sudo bash -c 'echo 8086 2701 > /sys/bus/pci/drivers/vfio-pci/new_id'
```

### 启动虚拟机

```
qemu-system-x86_64 \
    -kernel ./bzImage \
    -initrd ./initramfs.cpio.gz \
    -nographic \
    -append "console=ttyS0 nokaslr" \
    -enable-kvm \
    -device vfio-pci,host=0000:5e:00.0
```

### 使用完成后，bind到host驱动

```
sudo bash -c 'echo 8086 2701 > /sys/bus/pci/drivers/vfio-pci/remove_id'
sudo modprobe -r vfio-pci
sudo bash -c 'echo -n 0000:5e:00.0 > /sys/bus/pci/drivers/nvme/bind
```

## 参考

https://www.cnblogs.com/bhlsheji/p/5317002.html

https://topic.alibabacloud.com/a/linux-drivers-manually-bind-and-unbind_1_16_30158827.html
