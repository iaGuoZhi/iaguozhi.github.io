---
title: 实用的Git技巧
date: 2022-07-07
legacy_url: yes
---

使用git已经有四年了，但是发现自己大多数的时候都只会使用add, commit, push, pull, checkout这几个指令，不愿意去学习新的命令。但其实git是个宝藏，里面充满着大佬们几十年编程经验中对版本管理，工作流悟出来的智慧。于是我整理下自己发现的好用的git技巧，以便经常查阅使用。

## 常规

### clone

clone并更名为linux:

```
git clone https://github.com/openeuler-mirror/kernel.git linux
```

### branch

列出所有分支(本地和远程)

```
git branch -a
```

### add

分块添加进暂存区，而不是添加整个文件

```
git add -p
```

### pull

仅仅pull最近的一个commit:
```
git pull origin master --depth=1
```

### commit

增加签名:

```
gc --signoff
```

commit为fixup!, 在rebase squash中将被合并

```
gc --fixup SHA1
```

### reset

重置到某个commit，不保留之后的修改
```
git reset --hard SHA1
```

重置到某个commit，保留之后的修改到工作区
```
git reset --soft SHA1
```

### cherry-pick

挑选某个commit到当前分支

```
git cherry-pick SHA1
```

### rebase

通过rebase可以非常方便的修改已经commit的代码, 比如要修改commit HEAD^^，可以通过

```
git rebase -i HEAD^^^
```
在rebase的编辑界面，将目标commit从pick改成edit，即可修改

此外能够在编辑界面修改keyword实现删除某个commit，合并commit，更改commit message

rebase非常好用，我经常使用的指令还有这个:
```
git rebase -i --autosquash master
```
它能合并需要被squash的commit, 需要与git commit --fixup搭配使用

通过rebase还能够为commit添加签名，比如为最近的四个commit增加签名
```
git rebase --signoff HEAD~4
```

### revert

更加安全的删除某个commit, 目标commit仍存在，只是新增加一个revert commit删除目标commit添加的代码:

```
git revert SHA1
```

### stash

贮藏脏工作区的修改

```
git stash
```

恢复脏工作区的修改

```
git stash pop
```

### diff

查看与某个commit对比的overview
```
git diff SHA1 --stat
```

查看已经添加到工作区的修改
```
git diff --staged
```

### log

```
git log --oneline
```

### bitsect

二分查找来发现引入bug的commit
```
git bisect
```

### submodules

更新所有的submodule

```
git submodule update --init --recursive
```

### help

git最常见的用法示例
```
git help everyday
```

## 与 Patch 相关 

### commit 规范

1. commit信息不能够每一行不能够过长也不能够过短，在vim中选中后按g,w自动format commit信息
2. 在patch新版本对上一个版本增加了修改可以在commit中直接标记, 例如
```
---
v3:
- Use C style comment
```

### format-patch

使用最近的4个commit制作版本为1的4个patch，并且添加签名, 添加patch来介绍这个series
```
git format-patch --cover-letter -s -v 1 -4
```

### checkpatch

使用checkpatch.pl来检查最近一个commit是否有style上面的问题
```
./scripts/checkpatch.pl -g --strict HEAD~1..HEAD
```

### send-email

通过email发送patch的一个例子:
```
git send-email 0001-acpi-processor_idle.c-Fix-kernel-pointer-leak.patch --to rafael@kernel.org,lenb@kernel.org --cc linux-acpi@vger.kernel.org,linux-kernel@vger.kernel.org
```

发送邮件来提交patch, 但是查找邮件的发送对象很麻烦，而且还需要抄写，难免会出现错误，可以使用这个技巧来自动填充email
首先在gitconfig中设置:
```
[sendemail.linux]
        tocmd ="`pwd`/scripts/get_maintainer.pl --nogit --nogit-fallback --norolestats --nol"
        cccmd ="`pwd`/scripts/get_maintainer.pl --nogit --nogit-fallback --norolestats --nom"
```

然后在项目Linux的根目录使用以下命令发送patch
```
# 自动填充email
git send-email --identity=linux ***.patch
```

### publish

一个内核大佬们写的工具，能够帮助自动整理并发送patch（自动化patch以及cover letter生成，patch的版本管理，邮件管理)，发送patch只需要一个命令即可，非常方便:

https://github.com/stefanha/git-publish

### apply

合并邮箱中的patch:

```
git apply xxx.patch
```

## 与 Vim 相关

### vim-fugitive

通过Gdiffsplit和diffput在vim中添加修改

### vim-gitgutter

diff 当前chunk很方便，而且能够用快捷键在chunk之间跳转

## 参考

https://fle.github.io/git-tip-keep-your-branch-clean-with-fixup-and-autosquash.html

https://github.com/git-tips/tips

https://zhuanlan.zhihu.com/p/530896668
