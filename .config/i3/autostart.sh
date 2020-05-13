#!/bin/bash

xrdb ~/.Xresources
setxkbmap -layout us,ru -variant ,winkeys -option grp:caps_toggle,grp_led:scroll &
kbdd &
dbus-update-activation-environment --systemd --all &
pcmanfm-qt -d &
/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
#VBoxClient-all &
sleep 5
feh --bg-fill ~/img/wallhaven-84638.png &
# ~/.config/i3/startup_notifications.py