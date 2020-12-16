#!/home/khaberev/.config/rofi/rofi-menu/bin/python
import rofi_menu
import os

FOLDERS = [
    "/workdir/Projects",
    "/workdir/Projects/ETSLT"
]


def get_projects():
    result = []
    for f in FOLDERS:
        with os.scandir(f) as items:
            for i in items:
                if i.is_dir():
                    try:
                        os.stat(f"{i.path}/pom.xml")
                        result.append((f" java {i.name}", f"idea {i.path}"))
                    except:
                        result.append((f" python {i.name}", f"pycharm {i.path}"))

    return result

class ProjectsMenu(rofi_menu.Menu):
    prompt = "Projects"

    def __init__(self, **kwargs):
        items = kwargs.pop("projects", [])
        self.items = []
        super(ProjectsMenu, self).__init__(**kwargs)
        for i in items:
            self.items.append(rofi_menu.ShellItem(i[0], i[1]))


if __name__ == "__main__":
    rofi_menu.run(ProjectsMenu(projects=get_projects()), rofi_version="1.6")