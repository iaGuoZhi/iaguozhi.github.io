---
title: Linux NVMe Commands
date: 2023-04-10
---

## 列出controller

```
# 列出主控制器
nvme id-ctrl /dev/nvme0
# 列出secondary controller
nvme list-secondary /dev/nvme0
```

## 创建namespace

```
# 创建50GB的ns
nvme create-ns /dev/nvme0 -nsze=97656250 --ncap=97656250 --flbas=0 -dps=0
```
返回的是ns的id

## Attach namespace 到 controller
 
```
# attach 到主控制器
nvme attach-ns /dev/nvme0 -n $NSID -c 65
nvme ns-rescan /dev/nvme0
# attach 到secondary controller
nvme attach-ns /dev/nvme0 -c $VIRT_CNTLID -n $NSID
```

## Detach

```
nvme detach-ns /dev/nvme0 -n $NSID -c 65
```

# 完整脚本

## 使用普通NVMe设备的流程

```
NVME_DEV=/dev/nvme0
SIZE_GB=512
BLOCK_SIZE=4096
VFNID=0

# Get the ID of the primary (host) controller
HOST_CNTLID=$(nvme id-ctrl $NVME_DEV -o json | jq .cntlid)

# Get the ID of the secondary (virtual function) controller
VIRT_CNTLID=$(nvme list-secondary $NVME_DEV -o json | jq '."secondary-controllers"[]|select(."virtual-function-number"=='$((VFNID + 1))')."secondary-controller-identifier"')

SIZE_BLOCKS=$((SIZE_GB * 1000000000 / BLOCK_SIZE))

echo "Primary controller ID:   $HOST_CNTLID"
echo "Secondary controller ID: $VIRT_CNTLID"
echo "Creating namespace with $SIZE_BLOCKS $BLOCK_SIZE-byte blocks..."

# Create the new namespace, and capture the output, which should be "create-ns: Success, created nsid:32"
out=$(nvme create-ns $NVME_DEV --nsze=$SIZE_BLOCKS --ncap=$SIZE_BLOCKS --block-size $BLOCK_SIZE)

NSID=${out#*created nsid:}
echo "Created namespace $NSID"

# Attach the namespace to the host
nvme attach-ns $NVME_DEV -n $NSID -c $HOST_CNTLID

# Wait for the namespace to populate
while true; do
    NSDEV=$(nvme list -o json | jq -r ".Devices[]|select(.NameSpace==$NSID).DevicePath")
    if [ -n "$NSDEV" ]; then
        break
    fi

    sleep 1
    nvme ns-rescan $NVME_DEV
done

# Partition/format/image the new namespace
(...)

# Detach the new namespace from the primary controller
nvme detach-ns $NVME_DEV -c $HOST_CNTLID -n $NSID

# Attach it to the secondary controller
nvme attach-ns $NVME_DEV -c $VIRT_CNTLID -n $NSID
```

## 启用支持SR-IOV的NVMe设备的virtual function

```bash
#!/bin/bash

# find device

if [ $# -ne 2 ]; then
    echo "Usage: $0 <nvme_device> <vf_number>"
    echo "Example: $0 nvme2 4"
    exit 1
fi

nvme_dev=$1
vf_num=$2
bdf=$(basename $(readlink /sys/class/nvme/$nvme_dev/device))

if [ $vf_num -gt 32 ]; then
    echo "VF number should be less than 32"
    exit 1
fi

if [ -z "$bdf" ]; then
    echo "Cannot find device $nvme_dev. Exit!"
    exit 1
fi

echo "NVMe dev  : $nvme_dev"
echo "BDF       : $bdf"
echo "VF number : $vf_num"

# enable VF

sudo nvme virt-mgmt /dev/$nvme_dev -c 65 -r 0 -a 1 -n 0  # Deallocate VQ
sudo nvme virt-mgmt /dev/$nvme_dev -c 65 -r 1 -a 1 -n 0  # Dealoocate VI
sudo nvme reset /dev/$nvme_dev

for (( i=1; i<=$vf_num; i++ ))
do
        sudo nvme virt-mgmt /dev/$nvme_dev -c $i -r 0 -n 4 -a 8  # Allocate VQ
        sudo nvme virt-mgmt /dev/$nvme_dev -c $i -r 1 -n 4 -a 8  # Aloocate VI
done

sudo bash -c "sudo echo 0 > /sys/bus/pci/devices/$bdf/sriov_drivers_autoprobe" # no autoprobe
sudo bash -c "sudo echo $vf_num > /sys/class/nvme/$nvme_dev/device/sriov_numvfs" # enable VF

# check

for (( i=1; i<=$vf_num; i++ ))
do
        sudo nvme virt-mgmt /dev/$nvme_dev -c $i -a 9
done

sudo nvme list-secondary /dev/$nvme_dev | grep SC | head -n $(($vf_num*3))
```

## 为NVMe vf绑定vfio驱动

```bash
#!/bin/bash

sudo modprobe vfio-pci

# find device

if [ $# -ne 3 ]; then
    echo "Usage: $0 <nvme_device> <vf_number> <is_vfio>"
    echo "Example: $0 nvme2 4 1"
    exit 1
fi

nvme_dev=$1
vf_num=$2
is_vfio=$3
bdf=$(basename $(readlink /sys/class/nvme/$nvme_dev/device))

if [ $vf_num -gt 32 ]; then
    echo "VF number should be less than 32"
    exit 1
fi

if [ -z "$bdf" ]; then
    echo "Cannot find device $nvme_dev. Exit!"
    exit 1
fi

echo "NVMe dev  : $nvme_dev"
echo "BDF       : $bdf"
echo "VF number : $vf_num"
echo "is_vfio   : $is_vfio"

for (( i=1; i<=$vf_num; i++ ))
do
    vfbdf=$(basename $(readlink /sys/class/nvme/$nvme_dev/device/virtfn$(($i-1))))

    if [ $is_vfio -eq 1 ]; then
        echo "Binding $vfbdf to vfio-pci"
        bash -c "echo $vfbdf > /sys/bus/pci/drivers/nvme/unbind" &> /dev/null
        echo vfio-pci > /sys/bus/pci/devices/$vfbdf/driver_override
        echo $vfbdf > /sys/bus/pci/drivers_probe
    else
        echo "Binding $vfbdf to nvme"
        bash -c "echo $vfbdf > /sys/bus/pci/drivers/vfio-pci/unbind" &> /dev/null
        echo nvme > /sys/bus/pci/devices/$vfbdf/driver_override
        echo $vfbdf > /sys/bus/pci/drivers_probe
    fi
done
```

## 参考

https://github.com/linux-nvme/nvme-cli/issues/1126
