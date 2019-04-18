# name: Informative Vcs
# author: Mariusz Smykula <mariuszs at gmail.com>



function fish_prompt --description 'Write out the prompt'
	set -l last_status $status

	if not set -q __fish_git_prompt_show_informative_status
		set -g __fish_git_prompt_show_informative_status 1
	end
	if not set -q __fish_git_prompt_hide_untrackedfiles
		set -g __fish_git_prompt_hide_untrackedfiles 1
	end

	if not set -q __fish_git_prompt_color_branch
		set -g __fish_git_prompt_color_branch magenta --bold
	end
	if not set -q __fish_git_prompt_showupstream
		set -g __fish_git_prompt_showupstream "informative"
	end
	if not set -q __fish_git_prompt_char_upstream_ahead
		set -g __fish_git_prompt_char_upstream_ahead "↑"
	end
	if not set -q __fish_git_prompt_char_upstream_behind
		set -g __fish_git_prompt_char_upstream_behind "↓"
	end
	if not set -q __fish_git_prompt_char_upstream_prefix
		set -g __fish_git_prompt_char_upstream_prefix ""
	end

	if not set -q __fish_git_prompt_char_stagedstate
		set -g __fish_git_prompt_char_stagedstate "*"
	end
	if not set -q __fish_git_prompt_char_dirtystate
		set -g __fish_git_prompt_char_dirtystate "+"
	end
	if not set -q __fish_git_prompt_char_untrackedfiles
		set -g __fish_git_prompt_char_untrackedfiles "…"
	end
	if not set -q __fish_git_prompt_char_conflictedstate
		set -g __fish_git_prompt_char_conflictedstate "✖"
	end
	if not set -q __fish_git_prompt_char_cleanstate
		set -g __fish_git_prompt_char_cleanstate "✔"
	end

	if not set -q __fish_git_prompt_color_dirtystate
		set -g __fish_git_prompt_color_dirtystate blue
	end
	if not set -q __fish_git_prompt_color_stagedstate
		set -g __fish_git_prompt_color_stagedstate yellow
	end
	if not set -q __fish_git_prompt_color_invalidstate
		set -g __fish_git_prompt_color_invalidstate red
	end
	if not set -q __fish_git_prompt_color_untrackedfiles
		set -g __fish_git_prompt_color_untrackedfiles $fish_color_normal
	end
	if not set -q __fish_git_prompt_color_cleanstate
		set -g __fish_git_prompt_color_cleanstate green --bold
	end

	if not set -q __fish_prompt_normal
		set -g __fish_prompt_normal (set_color normal)
	end

	echo
	set_color yellow
	printf '%s' (whoami)
	set_color normal
	printf ' in '
	set_color $fish_color_cwd
	printf '%s' (echo $PWD | sed -e "s|^$HOME|~|")
	set_color normal

	# Line 2
	echo
	set newline 0
	if test $VIRTUAL_ENV
		set_color yellow
		printf "virtualenv:  "
		set_color magenta --bold
		printf "(%s)  " (basename $VIRTUAL_ENV)
		set newline 1
		set_color normal
		printf " "
	end

	set -l vcs (__fish_vcs_prompt)
	if test $vcs
		set_color yellow
		printf "vcs:  "
		set_color normal
		printf '%s' $vcs
		set newline 1
	end

	if not test $last_status -eq 0
		set_color $fish_color_error
	else
		set_color normal
	end

	if test $newline -gt 0
		echo
	end

	printf '↪ '
	set_color normal

	set_color normal
end
