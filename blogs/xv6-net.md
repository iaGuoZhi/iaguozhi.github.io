---
title: Xv6 net lab
date: 2022-05-12
---

## 驱动介绍

操作系统中的驱动代码的作用是:

1. 配置硬件设备
2. 操作硬件设备进行具体操作
3. 处理硬件产生的中断
4. 与等待设备结果的进程交互

## Xv6 net 介绍

Xv6 目前实现了arp，ip，tcp这三个网络协议。
基于的网络设备驱动是e1000。

## e1000 收发包实现

### 发包

因为可能有多个进程同时发包，所以需要在操作设备寄存器的时候拿锁。

```
int
e1000_transmit(struct mbuf *m)
{
  // the mbuf contains an ethernet frame; program it into
  // the TX descriptor ring so that the e1000 sends it. Stash
  // a pointer so that it can be freed after sending.
  //
  struct tx_desc *desc;
  struct mbuf *free_mbuf;

  // regs[E1000_TDT] access should be protected
  acquire(&e1000_lock);
  
  int desc_idx = regs[E1000_TDT];
  if(desc_idx < 0 || desc_idx >= TX_RING_SIZE)
  {
    release(&e1000_lock);
    panic("e1000_transmit");
  }

  desc = &(tx_ring[desc_idx]);
  if(!(desc->status & E1000_TXD_STAT_DD))
  {
    release(&e1000_lock);
    return -1;
  }

  free_mbuf = tx_mbufs[desc_idx];
  while(free_mbuf) {
   struct mbuf *t = free_mbuf; 
   free_mbuf = free_mbuf->next;
   mbuffree(t);
  }

  desc->addr = (uint64)m->head;
  desc->length = m->len;
  desc->cmd = E1000_TXD_CMD_EOP | E1000_TXD_CMD_RS;
  tx_mbufs[desc_idx] = m;

  // Commit point
  regs[E1000_TDT] = (regs[E1000_TDT] + 1) % TX_RING_SIZE;
  __sync_synchronize();

  release(&e1000_lock);

  return 0;
}
```

### 收包

考虑到有多个网络包同时到来，需要在一次收包过程中处理所有到来的网络包。

```
static void
e1000_recv(void)
{
  // Check for packets that have arrived from the e1000
  // Create and deliver an mbuf for each packet (using net_rx()).
  //
  struct rx_desc *desc;
  int desc_idx;

  desc_idx = (regs[E1000_RDT] + 1) % RX_RING_SIZE;
  desc= &(rx_ring[desc_idx]);
  while(desc->status & E1000_RXD_STAT_DD){
    rx_mbufs[desc_idx]->len = desc->length;
    net_rx(rx_mbufs[desc_idx]);

    rx_mbufs[desc_idx] = mbufalloc(0);
    desc->addr = (uint64)rx_mbufs[desc_idx]->head;
    desc->length = rx_mbufs[desc_idx]->len;
    desc->status = 0;

    desc_idx = (desc_idx + 1) % RX_RING_SIZE;
    desc= &(rx_ring[desc_idx]);
  }

  // Software adds receive descriptors by writing the tail pointer 
  // with the index of the entry beyond the last valid descriptor
  regs[E1000_RDT] = (desc_idx - 1) % RX_RING_SIZE;
  __sync_synchronize();
}
```

## 总结

比较简单

![](./static/net_time_spend.png)

## 参考

https://pdos.csail.mit.edu/6.828/2020/labs/net.html

https://pdos.csail.mit.edu/6.828/2020/xv6/book-riscv-rev1.pdf

https://csapp.cs.cmu.edu/

https://pdos.csail.mit.edu/6.828/2020/readings/8254x_GBe_SDM.pdf
