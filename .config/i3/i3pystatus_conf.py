from i3pystatus import Status
from i3pystatus.cpu_usage import CpuUsage
from i3pystatus.disk import Disk
from i3pystatus.mem import Mem
from i3pystatus.swap import Swap
from i3pystatus.pulseaudio import PulseAudio
from i3pystatus import Module
from i3pystatus.core.util import round_dict
from threading import Thread
import subprocess
import os
import sys
import psutil
import re


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


class MyCpuUsage(CpuUsage, FormatSwitcher):
    settings = (
        ('formats', '')
    )
    color = "#FFFFFF"
    warn_color = "#FFFF00"
    alert_color = "#FF0000"
    warn_percentage = 50
    alert_percentage = 80
    exclude_average = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format=self.formats[0]
        self.on_rightclick="next_format"

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
    regex = re.compile(r'.*Device size:\s*(\d*).*Free \(estimated\):\s*(\d*).*', re.DOTALL)

    settings = (
        ('formats', '')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format=self.formats[0]
        self.on_rightclick="next_format"

    @staticmethod
    def _get_fs_type(path):
        bestMatch = ''
        fsType = ''
        for part in psutil.disk_partitions():
            if path.startswith(part.mountpoint) and len(bestMatch) < len(part.mountpoint):
                fsType = part.fstype
                bestMatch = part.mountpoint
        return fsType

    @staticmethod
    def _get_btrfs_usage(path):
        return str(subprocess.check_output(['btrfs',  'filesystem', 'usage', '-b', path], universal_newlines=True))

    def run(self):
        if os.path.isdir(self.path) and not os.path.ismount(self.path):
            if len(os.listdir(self.path)) == 0:
                self.not_mounted()
                return

        try:
            stat = os.statvfs(self.path)

            if self._get_fs_type(self.path) != 'btrfs':
                available = (stat.f_bsize * stat.f_bavail) / self.divisor
                percentage_avail = stat.f_bavail / stat.f_blocks * 100

                cdict = {
                    "total": (stat.f_bsize * stat.f_blocks) / self.divisor,
                    "free": (stat.f_bsize * stat.f_bfree) / self.divisor,
                    "avail": available,
                    "used": (stat.f_bsize * (stat.f_blocks - stat.f_bfree)) / self.divisor,
                    "percentage_free": stat.f_bfree / stat.f_blocks * 100,
                    "percentage_avail": percentage_avail,
                    "percentage_used": (stat.f_blocks - stat.f_bfree) / stat.f_blocks * 100,
                }

            else:
                btrfs_usage = self._get_btrfs_usage(self.path)
                match = self.regex.findall(btrfs_usage)
                total_bytes = int(match[0][0])
                free_estimated = int(match[0][1])
                available = free_estimated / self.divisor
                percentage_avail = (total_bytes - free_estimated) / total_bytes * 100

                cdict = {
                    "total": total_bytes / self.divisor,
                    "free": 0,
                    "avail": available,
                    "used": (total_bytes - free_estimated) / self.divisor,
                    "percentage_free": 0,
                    "percentage_avail": percentage_avail,
                    "percentage_used": 100 - percentage_avail,
                }

        except Exception as ex:
            self.not_mounted()
            return

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


class MyPulseAudio(PulseAudio):
    def unmute(self):
        subprocess.call(['pactl', '--', 'set-sink-mute', self.current_sink, "0"])

    def increase_volume(self):
        self.unmute()
        super(MyPulseAudio, self).increase_volume()

    def decrease_volume(self):
        self.unmute()
        super(MyPulseAudio, self).decrease_volume()


HINTS = {"separator_block_width": 17}
HINTS_NO_SEP = dict(HINTS, separator=False)

status = Status(interval=1)

status.register(
    PersistOutputModule(
        command='~/.config/i3blocks/kbdd',
        hints=dict(HINTS, min_width='English (US)  '),
        shell=True
    )
)

status.register("clock",
    on_leftclick=["gsimplecal"],
    format=" %a %-d %b %X",
    hints=HINTS)

status.register("network",
    interface="eth0",
    format_up=" {bytes_sent:.2f}   {bytes_recv:.2f} MB/s",
    divisor=1024 ** 2,
    round_size=2,
    color_up="#FFFFFF",
    dynamic_color=False,
    on_leftclick=['wicd-client -n'],
    hints=HINTS)


status.register(
    PersistOutputModule(
        command='~/.config/i3blocks/disk-io -w 2 -M -P 2 -t 1 -s "   "',
        hints=HINTS_NO_SEP,
        format=" {line}",
        shell=True
    )
)

status.register(
    MyCpuUsage(
        # format=" {usage:.2f}%",
        format_all="{usage:.2f} ",
        formats=[" {usage:.2f}%", " {usage_all}"],
        hints=dict(HINTS_NO_SEP, min_width=" 00.00%"),
        on_leftclick=['terminator -e "htop"'],
        interval=1
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

status.register(
    PulseAudio(
        format=" {volume}",
        format_muted=" {volume} MUTE",
        hints=HINTS
    )
)

status.run()