---
title: Send patch to QEMU
date: 2022-05-03
legacy_url: yes
---

最近给QEMU提交了几个小patch，整理下步骤，以便之后查阅：

## 1. 寻找issues

在[QEMU](https://gitlab.com/qemu-project/qemu/-/issues)的issues页面可以看到等待解决的issues。 

从中找到自己能够解决的issues，比如我发现了一个[issue](https://gitlab.com/qemu-project/qemu/-/issues/978)很简单，但是还没有人解决。

## 2. 写代码

接下来，写代码来解决这个issue，以上面我发现的issue为例子: 

之所以会出现输入-vga help, QEMU abort是因为代码访问了一个空指针，找到访问空指针的位置，发现是因为`def`指针是null，但是却被取引用。因此我加了一点代码，在对def取引用之前先确定def不为空。更改之后的代码如下:

```
if (vga_interface_available(t) && ti->opt_name) {
    printf("%-20s %s%s\n", ti->opt_name, ti->name ?: "",
            (def && g_str_equal(ti->opt_name, def)) ?
            " (default)" : "");
}
```

## 3. Git commit

对代码进行commit： commit规范是第一行总结修改，空一行，下面再具体描述修改。另外QEMU社区不希望commit行数过多，在vim里面可以通过在普通模式下选中commit信息，按g和w键来将commit信息格式化，从而不会出现有一些行字数过少，导致行数变多的情况。

在上面这个例子中我的commit信息就是

```
vga: avoid crash if no default vga card

QEMU in some arch will crash when executing -vga help command, because
there is no default vga model.  Add check to this case and avoid crash.
```

## 4. 生成patch

通过`git format-patch -s -v 1 -1`来生成patch。其中-s是添加committer的签名，-v 1是将这个patch命名为版本1（patch将会以v1开头)，-1是指使用最近一次commit的代码来生成patch。

## 5. 修改patch

在format-patch生成后，还能够直接用vim来修改patch。比如由于我这个patch解决的是一个issue，那么我可以在patch中commit信息下方加入

```
Resolves: https://gitlab.com/qemu-project/qemu/-/issues/978
```

这可以使得当patch被接收后，对应的issue自动关闭，同时也能够让你的reviewer更加清楚你为什么要提这个patch。

## 6. 检查patch

大型项目一般都会有脚本来检查patch是否规范，QEMU中可以通过`./scripts/checkpatch.pl`来检查patch。在发送邮件之前一定要检查一遍，以免给reviewer带来不必要的工作。

到这一步后，我的patch长下面这个样子:

```
From b0daca5b03c54596758a1b36e91c85a08a747e4d Mon Sep 17 00:00:00 2001
From: Guo Zhi <qtxuning1999@sjtu.edu.cn>
Date: Tue, 3 May 2022 17:08:43 +0800
Subject: [PATCH v2] vga: avoid crash if no default vga card

QEMU in some arch will crash when executing -vga help command, because
there is no default vga model.  Add check to this case and avoid crash.

Resolves: https://gitlab.com/qemu-project/qemu/-/issues/978

Signed-off-by: Guo Zhi <qtxuning1999@sjtu.edu.cn>
---
 softmmu/vl.c | 3 ++-
 1 file changed, 2 insertions(+), 1 deletion(-)

diff --git a/softmmu/vl.c b/softmmu/vl.c
index c2919579fd..a49e29312b 100644
--- a/softmmu/vl.c
+++ b/softmmu/vl.c
@@ -977,7 +977,8 @@ static void select_vgahw(const MachineClass *machine_class, const char *p)
 
             if (vga_interface_available(t) && ti->opt_name) {
                 printf("%-20s %s%s\n", ti->opt_name, ti->name ?: "",
-                       g_str_equal(ti->opt_name, def) ? " (default)" : "");
+                        (def && g_str_equal(ti->opt_name, def)) ?
+                        " (default)" : "");
             }
         }
         exit(0);
-- 
2.35.1
```

## 7. 发送邮件

通过git send-email发送邮件。

邮件发送的对象可以通过`./scripts/get_maintainer.pl`获得，为了方便，推荐使用以下方式直接发送邮件。

在~/.gitconfig中加入以下代码:

```
[sendemail.qemu]
	tocmd ="`pwd`/scripts/get_maintainer.pl --nogit --nogit-fallback --norolestats --nol"
	cccmd ="`pwd`/scripts/get_maintainer.pl --nogit --nogit-fallback --norolestats --nom"
```

之后发送一个patch的命令就是

```
git send-email --identity=qemu v1-0001-vga-crash-if-no-default-vga-card.patch
```

## 8. 参与讨论

patch 发送之后，自己的邮箱也会收到邮件，可以用来确认patch是否发送成功。

patch的审核周期可能是几天到一周不定，耐心等待，及时回复，如果reviewer觉得需要更改，重新发送一个修改后的v2版本的patch。

