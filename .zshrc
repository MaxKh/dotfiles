# Lines configured by zsh-newuser-install
HISTFILE=~/.histfile
HISTSIZE=1000
SAVEHIST=1000
bindkey -e

setopt hist_ignore_all_dups # remove older duplicate entries from history
setopt hist_reduce_blanks # remove superfluous blanks from history items
setopt inc_append_history # save history entries as soon as they are entered
setopt share_history # share history between different instances of the shell

setopt auto_list # automatically list choices on ambiguous completion
setopt auto_menu # automatically use menu completion
setopt always_to_end # move cursor to end if word had one match


# End of lines configured by zsh-newuser-install
# The following lines were added by compinstall
zstyle :compinstall filename '$HOME/.zshrc'
zstyle ':completion:*' menu select

autoload -Uz compinit
compinit
# End of lines added by compinstall

source <(antibody init)
antibody bundle < ~/.zsh_plugins.txt

WORDCHARS='*?_-.[]~=&;!#$%^(){}<>'

bindkey '^[[1;5A' history-substring-search-up
bindkey '^[[1;5B' history-substring-search-down
bindkey  "^[[H"   beginning-of-line
bindkey  "^[[F"   end-of-line
bindkey '^[[3~' delete-char

bindkey '^[[1;5D' backward-word
bindkey '^[[1;5C' forward-word

SPACESHIP_PROMPT_ORDER=(
  user          # Username section
  dir           # Current directory section
  host          # Hostname section
  git           # Git section (git_branch + git_status)
  hg            # Mercurial section (hg_branch  + hg_status)
#  exec_time     # Execution time
  venv
  line_sep      # Line break
#  vi_mode       # Vi-mode indicator
  jobs          # Background jobs indicator
#  exit_code     # Exit code section
  char          # Prompt character
)
SPACESHIP_USER_SHOW='always'
SPACESHIP_DIR_TRUNC=0
SPACESHIP_DIR_TRUNC_REPO='false'
SPACESHIP_CHAR_SYMBOL='↪ '

typeset -a ealiases
ealiases=()

function ealias()
{
    alias $1
    ealiases+=(${1%%\=*})
}

function expand-ealias()
{
    if [[ $LBUFFER =~ "\<(${(j:|:)ealiases})\$" ]]; then
        zle _expand_alias
        zle expand-word
    fi
    zle magic-space
}

zle -N expand-ealias

bindkey ' ' expand-ealias


alias la='ls --group-directories-first -alh --color=auto'
alias ll='ls --group-directories-first -lh --color=auto'
alias ls='ls --group-directories-first -h --color=auto'
alias dotfiles='git --git-dir ~/.dotfiles --work-tree ~'
alias nano='micro'
alias grep='grep --color=auto'

ealias gc='git commit'
ealias gc='git commit -m'
ealias gca='git commit --amend'
ealias gco='git checkout'
ealias gst='git status'
ealias gstu='git status -uno'
ealias gb='git branch -a'
ealias gd='git diff'
ealias gf='git fetch '
ealias ga='git add'
ealias gdt='git difftool -t meld -d'
ealias gp='git pull'
ealias gpu='git push'
ealias gl='git log'
ealias gcn='git clean -dfxn -e "*.iml" -e ".idea"'
ealias sss='sudo systemctl status'
ealias ssu='sudo systemctl start'
ealias ssd='sudo systemctl stop'
ealias drb='docker run --rm -it --entrypoint /bin/bash'



function psg()
{
  local pids=`pgrep -f -d " " $argv`
  if [[ -n pids ]]; then
    ps -flj -p $pids | grep -E "$argv|" --color=auto
  fi
}
fast-theme -q default
FAST_THEME_NAME='default'
FAST_HIGHLIGHT_STYLES[${FAST_THEME_NAME}path]='fg=cyan'
FAST_HIGHLIGHT_STYLES[${FAST_THEME_NAME}path-to-dir]='fg=cyan,underline'
