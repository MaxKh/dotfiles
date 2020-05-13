set -x VIRTUAL_ENV_DISABLE_PROMPT 1

abbr -a -g gc git commit -m
abbr -a -g gca git commit --amend
abbr -a -g gco git checkout
abbr -a -g gst git status
abbr -a -g gstu git status -uno
abbr -a -g gb git branch -a
abbr -a -g gd git diff
abbr -a -g gf git fetch 
abbr -a -g ga git add
abbr -a -g gdt git difftool -t meld -d
abbr -a -g gp git pull
abbr -a -g gpu git push
abbr -a -g gl git log
abbr -a -g gcn git clean -dfxn -e "*.iml" -e ".idea"
# abbr -a -g gbs git for-each-ref --sort=committerdate --format="%(HEAD) %(color:yellow)%(refname:short)%(color:reset) - %(color:red)%(objectname:short)%(color:reset) - %(contents:subject) - %(authorname) (%(color:green)%(committerdate:relative)%(color:reset))"
abbr -a -g sss sudo systemctl status
abbr -a -g ssu sudo systemctl start
abbr -a -g ssd sudo systemctl stop
abbr -a -g drb docker run --rm -it --entrypoint /bin/bash

set fish_color_command 005fd7

function ll --description 'List contents of directory using long format'
  set -lx EXA_COLORS da=36
  exa -lhg --group-directories-first --time-style=long-iso $argv
end

function la --description 'List contents of directory using long format'
  set -lx EXA_COLORS da=36
  exa -lahg --group-directories-first --time-style=long-iso $argv
end

function psg --description 'List processes and grep'
  if set pids (pgrep -f -d " " $argv);
    ps -flj -p $pids | grep -E "$argv|"
  end
end

function nano --description 'Alias for nano'
  command nano -c $argv
end

function dotfiles
  git --git-dir ~/.dotfiles --work-tree ~ $argv
end

function __fish_describe_command
  return
end

function gbs
  if count $argv > /dev/null
    git for-each-ref --sort=committerdate --format="%(HEAD) %(color:yellow)%(refname:short)%(color:reset) - %(color:red)%(objectname:short)%(color:reset) - %(contents:subject) - %(authorname) (%(color:green)%(committerdate:relative)%(color:reset))" $argv
  else
    git for-each-ref --sort=committerdate --format="%(HEAD) %(color:yellow)%(refname:short)%(color:reset) - %(color:red)%(objectname:short)%(color:reset) - %(contents:subject) - %(authorname) (%(color:green)%(committerdate:relative)%(color:reset))" refs/heads
  end
end

function ocl
  oc logs -f --since=1s $argv | tee -a $argv.log
end