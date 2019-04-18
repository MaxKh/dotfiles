set -x VIRTUAL_ENV_DISABLE_PROMPT 1

set -U fish_user_abbreviations 'gc=git commit -m ""'
set fish_user_abbreviations $fish_user_abbreviations 'gco=git checkout'
set fish_user_abbreviations $fish_user_abbreviations 'gst=git status'
set fish_user_abbreviations $fish_user_abbreviations 'gstu=git status -uno'
set fish_user_abbreviations $fish_user_abbreviations 'gb=git branch -a'
set fish_user_abbreviations $fish_user_abbreviations 'gd=git diff'
set fish_user_abbreviations $fish_user_abbreviations 'gf=git fetch'
set fish_user_abbreviations $fish_user_abbreviations 'ga=git add'
set fish_user_abbreviations $fish_user_abbreviations 'gdt=git difftool -t meld -d'
set fish_user_abbreviations $fish_user_abbreviations 'gp=git pull'
set fish_user_abbreviations $fish_user_abbreviations 'gpu=git push'
set fish_user_abbreviations $fish_user_abbreviations 'gl=git log'
set fish_user_abbreviations $fish_user_abbreviations 'gcn=git clean -dfxn -e "*.iml" -e ".idea"'
set fish_user_abbreviations $fish_user_abbreviations 'gwl=git worktree list'
set fish_user_abbreviations $fish_user_abbreviations 'gwa=git worktree add'
set fish_user_abbreviations $fish_user_abbreviations 'sss=sudo systemctl status'
set fish_user_abbreviations $fish_user_abbreviations 'ssu=sudo systemctl start'
set fish_user_abbreviations $fish_user_abbreviations 'ssd=sudo systemctl stop'

set fish_color_command 005fd7

function ll --description 'List contents of directory using long format'
  ls --group-directories-first -lh $argv
end

function la --description 'List contents of directory using long format'
  ls --group-directories-first -lah $argv
end

function psg --description 'List processes and grep'
  if set pids (pgrep -f -d " " $argv);
    ps -flj -p $pids | grep -E "$argv|"
  end
end

function ssctl --description 'Alias for sudo systemctl'
  sudo systemctl $argv
end

function ya --description 'Alias for yaourt'
  yaourt $argv
end

function s3 --description 'Alias for subl3'
  subl3 $argv
end

function nano --description 'Alias for nano'
  command nano -c $argv
end

function dotfiles
  git --git-dir ~/.dotfiles --work-tree ~ $argv
end

#set fish_function_path $fish_function_path "/usr/lib/python3.5/site-packages/powerline/bindings/fish/"
#powerline-setup
