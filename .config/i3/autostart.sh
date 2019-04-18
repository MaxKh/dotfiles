#!/bin/bash

xrdb ~/.Xresources
VBoxClient-all &
setxkbmap -layout us,ru -variant ,winkeys -option grp:caps_toggle,grp_led:scroll &
kbdd &
dbus-update-activation-environment --systemd --all &
thunar --daemon &
feh --bg-fill ~/img/wallhaven-84638.png &