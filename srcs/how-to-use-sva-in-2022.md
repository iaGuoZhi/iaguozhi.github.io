---
title: 如何使用sva特性(2022)
date: 2022-05-06
legacy_url: yes
---

SVA特性可以做到设备和进程使用同一套页表。有一篇博客他已经介绍过如何使用Linux SVA特性，但是考虑到他是2021年的，并且有很多细节上的点没有涉及， 并且一些关键信息已经过期，我在结合自身经验的基础上写一个如何使用sva特性2022版。

## 1. 机器

华为 KunPeng920服务器

## 2. License

需要在鲲鹏服务器上开启鲲鹏KAE加速引擎，因此需要在iBMC里面安全对应的许可证，这个许可证可能在服务器买的时候已经配套购买，也可能没有，需要联系经销商，但是经销商对于这种License都不是很了解，最直接的途径是联系华为的开发者，看能不能通过与华为合作的途径拿到License。

安装了License后，压缩解压缩设备应该是可见的:


```
root@ubuntu:~# lspci -s 75:00.0
75:00.0 Processing accelerators: Device 19e5:a250 (rev 21)
```

## 3. 内核配置与编译

目前实现了sva特性的Linux 内核在: https://github.com/Linaro/linux-kernel-uadk/tree/uacce-devel-5.16

下载之后进行如下配置： 

```
make defconfig

make menuconfig

choose follow in menuconfig: 

CONFIG_ARM_SMMU_V3=y
CONFIG_PCI_PASID=y
CONFIG_IOMMU_SVA=y
CONFIG_CRYPTO_DEV_HISI_QM=y
CONFIG_CRYPTO_DEV_HISI_ZIP=y
CONFIG_UACCE=y

```

之后再编译内核。

## 4. uadk 用户态框架安装

从 https://github.com/Linaro/uadk/tree/master 下载uadk。
uadk 编译安装命令:

```
./autogen.sh
./conf.sh
make
```

## 5. 运行uadk测试程序

在uadk编译好之后, 在.libs目录下会出现用户态库:

```
.libs git:(master) ✗ ls *.so
libhisi_hpre.so  libhisi_sec.so  libhisi_zip.so  libwd_comp.so  libwd_crypto.so  libwd.so
```

通过 `export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/path-to-libs`将生成的库加入动态库搜索路径中。

在test目录下有一下测试程序：


```
 ➜  uadk git:(master) ✗ ls test
hisi_hpre_test  hisi_zip_testo hisi_sec_test
```

选择一个比如hisi\_set\_test进行测试，测试命令如下:

```
./test_hisi_sec --perf --async --pktlen 1024 --block 4096 --blknum 100000 --times 200 --multi 1 --ctxnum 1
```

参数可以调节，来控制产生io page fault的速度。

## 6. 验证sva

可以在kernel里面`drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3.c`中的`arm_smmu_handle_evt`中添加打印，来确认io page fault是否被触发已经被处理。

## 参考

https://wangzhou.github.io/2021/06/21/%E5%A6%82%E4%BD%95%E5%B0%9D%E8%AF%95%E4%BD%BF%E7%94%A8Linux-SVA/

https://github.com/Linaro/linux-kernel-uadk/issues/5
