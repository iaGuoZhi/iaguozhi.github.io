---
title: What's New in VIRTIO 1.1 
date: 2022-05-28
---


# Introduction

Virtio was invented by Rusty Rusell for easy mechanism to provide
virtual devices to guests. Its standard driver means compatibility
across hypervisors and operating systems. Virtio is a major approach to
support emulate devices for virtual machines nowadays, and becomes a
cornerstone for cloud computing. However, as commodity hundreds of Gbps
NICs support more packets per unit time. Virtio queues are becoming a
bottleneck for these kind of physical devices. Virtio queues need to be
accelerated, and this is why VIRTIO 1.1 specification comes up. In this
paper, we will dive into VIRTIO 1.1 new features by analyzing virtio
code in Linux operating system and QEMU hypervisor.

There are mainly two new features in VIRTIO 1.1: Packed virtqueue and In
order completion.

# Packed virtqueue

Classical virtio queues(VIRTIO 1.0) use split virtqueues, it includes
three parts: Available Ring, Used Ring, Descriptor Ring. Split
virtqueues is very straightforward but it has some performance issues.

1.  For software backends, it may leads to bad cache utilization,
    because following reasons:

    1.  virtio queues metadata is scattered into several places.

    2.  descriptor chain is not contiguous in memory.

    3.  cache contention in many places.

2.  For hardware implementation(don't be surprised, virtio backend can
    be implemented in hardware too), split virtqueues will result in
    several PCI transactions per descriptor.

Therefore, a more higher performance approach was proposed, called
packed virtqueue.

Packed virtqueue amends above issues by merging the three rings in just
one location in virtual environment guest memory. While this may seem
complicated at first glance, it's a natural step after the split version
if we realize that the device can discard and overwrite the data it
already has read from the driver, and the same happens the other way
around.

The packed virtqueue has already been implemented in both Linux and
QEMU, and can result in around 30% performance boost.

# In order completion

The VIRTIO 1.1 specification defines a feature bit (VIRTIO_F\_IN_ORDER)
that devices and drivers can negotiate when the device uses descriptors
in the same order in which they were made available by the driver.

This feature can simplify device and driver implementations and increase
performance. For example, when VIRTIO_F\_IN_ORDER is negotiated, it may
be easier to create a batch of buffers and reduce DMA transactions when
the device uses a batch of buffers.

For example, Table[1](#table:in_order_ring_example){reference-type="ref"
reference="table:in_order_ring_example"} shows a descriptor table with 2
descriptor chains, the first chain has a 2000 bytes long buffer that
starts in position 0x8000, the second chain has two descriptors and the
buffer starts at 0x2000 and 0x4000.

::: center
::: {#table:in_order_ring_example}
  ----- -------- ------ ------- ------
   Idx   Buffer   Len    Flags   Next
    0    0x8000   2000     W      0
    1    0x2000   2000     R      2
    2    0x4000   2000     R      0
    3                           
  ----- -------- ------ ------- ------

  : Drivers writes 2 buffers in descriptor ring
:::
:::

According to Table[1](#table:in_order_ring_example){reference-type="ref"
reference="table:in_order_ring_example"}, the driver exposes two chains
of descriptors. The first step to make the buffers available is
allocating the buffer with the memory and filling it, like Figure 1.
After populating the descriptor entry, the driver advises of it using
the avail ring: let's say avail_idx is 0 at begin, driver will update
avail_idx to 2 because it writes 2 buffers to the descriptor table. Then
the driver will notify the device that these buffers are available. The
device employs the used ring to return the used(read or written) buffers
to the driver. Let's say used_idx is 0 at begin, After the device's
processing finished. Instead of returning a chain of descriptors or the
ids of the heads of descriptors to the driver by used_ring, the device
only updates used_idx = 2, as two buffers have been used. The device
also writes out a single used ring entry with the id corresponding to
the head entry of the descriptor chain describing the last buffer in the
batch.

::: center
::: {#table:avail_ring}
  -------
   Avail
    Idx
     2
  -------

  : The avail ring after the device updates
:::
:::

::: center
::: {#table:used_ring}
  ----------
     Used
     Idx
      2
   ring\[\]
      1
  ----------

  : The used ring after the device updates
:::
:::

The in-order completion feature has not been implemented in Linux and
QEMU yet.

# Discussion

## Hardware backend for virtio

As SRIOV has been applied in virtulization, in order to pass through VF
to virtual machine, VF can be implemented according to virtio
specification. Therefore, vm can use VF hardware as a virtio device,
which can enjoy the high performance benefits of virtio.

VIRTIO 1.1 new features can helps hardware implementation, because it
simplified virito queues and reduced PCI transactions when performing an
IO operation.

## vDPA

vDPA offload IO datapath to virtio enhanced hardwares, and support
control path by vhost. vDPA is a popular topic in recent virtulization
studies, and has been merged into Linux in 2020.

# Conclusion

VIRTIO 1.1 is compatible with VIRTIO 1.0. all new extensions are added
as new features which can be achieved by features negotiation. VIRTIO
1.1 raised two approach called packed virtqueues and in order
completion. which will improve performance and help hardware backends
implementation.

# Reference

https://www.dpdk.org/wp-content/uploads/sites/35/2018/09/virtio-1.1_v4.pdf

https://docs.oasis-open.org/virtio/virtio/v1.1/csprd01/virtio-v1.1-csprd01.html

https://www.modb.pro/db/110904

http://blog.chinaunix.net/uid-28541347-id-5819237.html
:::
