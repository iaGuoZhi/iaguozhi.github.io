---
title: vsock 介绍与使用
date: 2022-08-08
legacy_url: yes
---

## vsock介绍

## vsock 使用

### 内核配置

#### 虚拟机kernel

将下面三个选项编译进kernel，而不是编译成模块，原因下面会介绍
```
CONFIG_VSOCKETS=y
CONFIG_VIRTIO_VSOCKETS=y
CONFIG_VIRTIO_VSOCKETS_COMMON=y
```

#### 宿主机kernel

VHOST\_VSOCK 只能够被编译成模块
```
CONFIG_VHOST_VSOCK=m
```

### 使用QEMU启动虚拟机


```
modprobe vhost_vsock
```

### 示例程序

#### Server (运行在宿主机上)

```
#include <sys/socket.h>
#include <linux/vm_sockets.h>
#include <string.h>
#include <stdio.h>

int main()
{
	int s = socket(AF_VSOCK, SOCK_STREAM, 0);

	struct sockaddr_vm addr;
	memset(&addr, 0, sizeof(struct sockaddr_vm));
	addr.svm_family = AF_VSOCK;
	addr.svm_port = 9999;
	addr.svm_cid = VMADDR_CID_HOST;

	bind(s, &addr, sizeof(struct sockaddr_vm));

	listen(s, 0);

	struct sockaddr_vm peer_addr;
	socklen_t peer_addr_size = sizeof(struct sockaddr_vm);
	int peer_fd = accept(s, &peer_addr, &peer_addr_size);

	char buf[64];
	size_t msg_len;
	while ((msg_len = recv(peer_fd, &buf, 64, 0)) > 0) {
		printf("Received %lu bytes: %.*s\n", msg_len, msg_len, buf);
	}

	return 0;
}
```

#### Client (运行在虚拟机上)


```
#include <sys/socket.h>
#include <linux/vm_sockets.h>
#include <string.h>

int main()
{
	int s = socket(AF_VSOCK, SOCK_STREAM, 0);

	struct sockaddr_vm addr;
	memset(&addr, 0, sizeof(struct sockaddr_vm));
	addr.svm_family = AF_VSOCK;
	addr.svm_port = 9999;
	addr.svm_cid = VMADDR_CID_HOST;

	connect(s, &addr, sizeof(struct sockaddr_vm));

	send(s, "Hello, world!", 13, 0);

	close(s);

	return 0;
}
```

## 参考

https://gist.github.com/nrdmn/7971be650919b112343b1cb2757a3fe6

https://wiki.qemu.org/Features/VirtioVsock

https://lwn.net/Articles/556550/
