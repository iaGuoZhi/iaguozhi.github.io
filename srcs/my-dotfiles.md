---
title: 我的dotfiles技巧
date: 2022-10-16
legacy_url: yes
---

## Vim

### 技巧

```
map <LEADER>a  <Esc>opr_info("[gz-debug]: %s\t%d\n", __func__, __LINE__);<CR><Esc>
```

```
map <LEADER><LEADER>   <Esc>/TBR<CR>:nohlsearch<CR>
```

```
map <LEADER>sc :set spell!<CR>
```

```
map <LEADER>c  <Esc>o```<CR>
```

```
w !sudo tee %
```

```
" ===
" === Restore Cursor Position
" ===
au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif
```

```
noremap <LEADER><CR> :nohlsearch<CR>
```

```
noremap K 5k
noremap J 5j
```


```
map sl :set splitright<CR>:vsplit<CR>
map sh :set nosplitright<CR>:vsplit<CR>
map sk :set nosplitbelow<CR>:split<CR>
map sj :set splitbelow<CR>:split<CR>

map <LEADER>l <C-w>l
map <LEADER>h <C-w>h
map <LEADER>k <C-w>k
map <LEADER>j <C-w>j
```

### 插件

```
Plug 'Valloric/YouCompleteMe'
Plug 'airblade/vim-gitgutter'
Plug 'iamcco/markdown-preview.nvim', { 'do': 'cd app && yarn install'  }
" Error checking
Plug 'dense-analysis/ale'
" File navigation
Plug 'scrooloose/nerdtree', { 'on': 'NERDTreeToggle' }
Plug 'wakatime/vim-wakatime' " track coding time
```

## Tmux

```
# move across panes
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

bind '"' split-window -c "#{pane_current_path}"
bind % split-window -h -c "#{pane_current_path}"
bind c new-window -c "#{pane_current_path}"
```

```
set -g @continuum-restore 'on' # 启用自动恢复
set -g @continuum-save-interval '360'
```
## Zsh

### 技巧
```
alias start-proxy="export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 all_proxy=socks5://127.0.0.1:7890"
alias close-proxy="unset https_proxy && unset http_proxy && unset all_proxy"
```

```
bindkey '^a' autosuggest-accept
```

```
PROMPT=%{$fg_bold[blue]%}%m\ $PROMPT
```

### 插件

```
plugins=(colored-man-pages common-aliases docker extract git golang kubectl sudo zsh-autosuggestions zsh-syntax-highlighting zsh-history-substring-search)
```

```
source $ZSH/oh-my-zsh.sh
```

## Git

```
[http]
	proxy = http://127.0.0.1:7890
[https]
	proxy = https://127.0.0.1:7890
```

```
[sendemail.linux]
	tocmd ="`pwd`/scripts/get_maintainer.pl --nogit --nogit-fallback --norolestats --nol"
	cccmd ="`pwd`/scripts/get_maintainer.pl --nogit --nogit-fallback --norolestats --nom"
```

## 参考

https://github.com/iaguozhi/dotfiles
