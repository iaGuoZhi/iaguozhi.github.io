---
title: 实用的Git技巧
date: 2022-07-07
legacy_url: yes
---

使用git已经有四年了，但是发现自己大多数的时候都只会使用add, commit, push, pull, checkout这几个指令，不愿意去学习新的命令。但其实git是个宝藏，里面充满着大佬们几十年编程经验中对版本管理，工作流悟出来的智慧。于是我整理下自己发现的好用的git技巧，以便经常查阅使用。

## 常规

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

通过rebase可以修改commit信息, 还能够合并fixup!的commit
```
git rebase -i --autosquash master
```

为最近的四个commit增加签名
```
git rebase --signoff HEAD~4
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

## 与 Patch 相关 

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

一个内核大佬们写的工具，能够帮助自动整理并发送patch，非常方便:

https://github.com/stefanha/git-publish

## 参考

https://fle.github.io/git-tip-keep-your-branch-clean-with-fixup-and-autosquash.html
