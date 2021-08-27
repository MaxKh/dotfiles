#!/bin/env python
import rofi_menu
import os

class CommandsMenu(rofi_menu.Menu):
    prompt = "Commands"
    items = [
        rofi_menu.ShellItem("vbox-clipboard", "killall VBoxClient; VBoxClient --clipboard")
    ]

if __name__ == "__main__":
    rofi_menu.run(CommandsMenu(), rofi_version="1.6")