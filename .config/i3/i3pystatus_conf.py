from i3pystatus import Status
from i3pystatus.cpu_usage import CpuUsage
from i3pystatus.disk import Disk
from i3pystatus.mem import Mem
from i3pystatus.swap import Swap
from i3pystatus import Module
from i3pystatus.core.util import round_dict
from threading import Thread
import subprocess
import os
import sys

class MyCpuUsage(CpuUsage):
    color = "#FFFFFF"
    warn_color = "#FFFF00"
    alert_color = "#FF0000"
    warn_percentage = 50
    alert_percentage = 80

    def run(self):
        usage = self.get_usage()
        usage['usage_all'] = self.gen_format_all(usage)

        if usage['usage'] > self.alert_percentage:
            c = self.alert_color
        elif usage['usage'] > self.warn_percentage:
            c = self.warn_color
        else:
            c = self.color

        self.data = usage
        self.output = {
            "full_text": self.format.format_map(usage),
            "color": c
        }

    def calculate_usage(self, cpu, total, busy):
        """
        calculates usage
        """
        diff_total = total - self.prev_total[cpu]
        diff_busy = busy - self.prev_busy[cpu]

        self.prev_total[cpu] = total
        self.prev_busy[cpu] = busy

        if diff_total == 0:
            return 0.0
        else:
            return diff_busy / diff_total * 100


class FormatSwitcher(object):
    formats = [""]
    indx = 0

    def next_format(self):
        self.indx = (self.indx + 1) % len(self.formats)
        self.format = self.formats[self.indx]
        try:
            self.send_output()
        except Exception as ex:
            pass


class MyMemUsage(Mem, FormatSwitcher):
    settings = (
        ('formats', '')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format=self.formats[0]
        self.on_rightclick="next_format"


class MyDiskUsage(Disk, FormatSwitcher):
    warn_color = "#FFFF00"
    alert_color = "#FF0000"
    percentage_alert_limit = 30
    percentage_critical_limit = 10

    settings = (
        ('formats', '')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format=self.formats[0]
        self.on_rightclick="next_format"

    def run(self):
        if os.path.isdir(self.path) and not os.path.ismount(self.path):
            if len(os.listdir(self.path)) == 0:
                self.not_mounted()
                return

        try:
            stat = os.statvfs(self.path)
        except Exception:
            self.not_mounted()
            return

        available = (stat.f_bsize * stat.f_bavail) / self.divisor
        percentage_avail = stat.f_bavail / stat.f_blocks * 100

        if available > self.display_limit:
            self.output = {}
            return

        if self.critical_limit:
            color = self.alert_color if available < self.critical_limit else self.color
        else:
            if percentage_avail < self.percentage_critical_limit:
                color = self.alert_color
            elif percentage_avail < self.percentage_alert_limit:
                color = self.warn_color
            else:
                color = self.color

        cdict = {
            "total": (stat.f_bsize * stat.f_blocks) / self.divisor,
            "free": (stat.f_bsize * stat.f_bfree) / self.divisor,
            "avail": available,
            "used": (stat.f_bsize * (stat.f_blocks - stat.f_bfree)) / self.divisor,
            "percentage_free": stat.f_bfree / stat.f_blocks * 100,
            "percentage_avail": percentage_avail,
            "percentage_used": (stat.f_blocks - stat.f_bfree) / stat.f_blocks * 100,
        }
        round_dict(cdict, self.round_size)

        self.data = cdict
        self.output = {
            "full_text": self.format.format(**cdict),
            "color": color
        }


class MySwapUsage(Swap, FormatSwitcher):
    settings = (
        ('formats', '')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format=self.formats[0]
        self.on_rightclick="next_format"


class PersistOutputModule(Module):
    settings = (
        ('command', 'Command to execute'),
        ('color', 'color'),
        ('format', 'Format'),
        ('shell', 'Shell')
    )

    color = "#FFFFFF"
    line = ''
    format = '{line}'
    shell=False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._update_output()
        t = Thread(target=self._loop)
        t.start()

    def _update_output(self):
        self.output = {
            "full_text": self.format.format(line=self.line),
            "color": self.color,
        }
        try:
            self.send_output()
        except Exception as ex:
            pass

    def _loop(self):
        popen = subprocess.Popen(self.command, shell=True, text=True, stdout=subprocess.PIPE)
        while True:
            output = popen.stdout.readline()
            if output == '' and popen.poll() is not None:
                break
            if output:
                o = output.strip()
                if self.line != o:
                    self.line = o
                    self._update_output()
        rc = popen.wait()
        return rc


HINTS = {"separator_block_width": 17}
HINTS_NO_SEP = dict(HINTS, separator=False)

status = Status(interval=1)

status.register(
    PersistOutputModule(
        command='~/.config/i3blocks/kbdd',
        hints=dict(HINTS, min_width='English (US)'),
        shell=True
    )
)

status.register("clock",
    on_leftclick=["gsimplecal"],
    format=" %a %-d %b %X",
    hints=HINTS)

status.register("network",
    interface="eth0",
    format_up=" {bytes_sent}   {bytes_recv} MB/s",
    divisor=1024 ** 2,
    color_up="#FFFFFF",
    dynamic_color=False,
    hints=HINTS)


status.register(
    PersistOutputModule(
        command='~/.config/i3blocks/disk-io -w 2 -M -P 0 -t 1 -s " "',
        hints=HINTS_NO_SEP,
        format=" {line}",
        shell=True
    )
)

status.register(
    MyCpuUsage(
        format=" {usage:.2f}%",
        hints=dict(HINTS_NO_SEP, min_width=" 00.00%"),
        on_leftclick=['terminator -e "htop"'],
        interval=2
    )
)

status.register(
    MyDiskUsage(
        path="/home",
        on_leftclick=["pcmanfm-qt ~"],
        hints=HINTS,
        interval=10,
        formats=[" HOME {avail} GB", " HOME {avail} GB free of {total} GB"]
    )
)

status.register(
    MyDiskUsage(
        path="/workdir",
        on_leftclick=["pcmanfm-qt /workdir"],
        hints=HINTS_NO_SEP,
        interval=10,
        formats=[" WORKDIR {avail} GB", " WORKDIR {avail} GB free of {total} GB"]
    )
)

status.register(
    MyDiskUsage(
        path="/",
        on_leftclick=["pcmanfm-qt /"],
        hints=HINTS_NO_SEP,
        interval=10,
        formats=[" ROOT {avail} GB", " ROOT {avail} GB free of {total} GB"]
    )
)

status.register(
    MySwapUsage(
        formats=[" SWAP {free} GB", " SWAP {free} GB free of {total} GB"],
        divisor=1024 ** 3,
        color='#FFFFFF',
        hints=HINTS,
        interval=10
    )
)

status.register(
    MyMemUsage(
        color='#FFFFFF',
        hints=HINTS_NO_SEP,
        interval=10,
        formats=[" MEM {avail_mem} GB", " MEM {avail_mem} GB free of {total_mem} GB"],
        divisor=1024**3
    )
)

status.register("pulseaudio",
    format="♪ {volume}",
    hints=HINTS)

status.run()