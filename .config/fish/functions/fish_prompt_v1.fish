function fish_prompt
    #Save the return status of the previous command
    set stat $status

    function _git_branch_name
        echo (git symbolic-ref HEAD ^/dev/null | sed -e 's|^refs/heads/||')
    end

    function _is_git_dirty
        echo (git status -s -uno --ignore-submodules=dirty ^/dev/null)
    end

    echo
    set_color yellow
    printf '%s' (whoami)

#    set_color normal
#    printf ' at '
#    set_color magenta
#    printf '%s' (hostname|cut -d . -f 1)

    set_color normal
    printf ' in '
    set_color $fish_color_cwd
    printf '%s' (echo $PWD | sed -e "s|^$HOME|~|")

    set_color normal
    # Line 2
    echo
#    printf (date "+$c2%H$c0:$c2%M$c0:$c2%S, ")
    set newline 0
    if test $VIRTUAL_ENV
       set_color yellow
       printf "virtualenv: "
       set_color -b blue normal
       printf "(%s)" (basename $VIRTUAL_ENV)
       set newline 1
       set_color normal
       printf " "
    end
    if [ (_git_branch_name) ]
        set_color yellow
        printf "git: "
        if [ (_is_git_dirty) ]
            set_color -b red normal
        else
            set_color -b green normal
        end
        printf "(%s)" (_git_branch_name)
        set newline 1
        set_color normal
    end

    # line 3
    if test $newline -gt 0
        echo
    end
    if test $stat -gt 0
        set_color -o red
    else
        set_color normal
    end
    printf '↪ '
    set_color normal
end
