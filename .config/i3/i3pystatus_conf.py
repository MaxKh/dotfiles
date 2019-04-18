from i3pystatus import Status
from i3pystatus.cpu_usage import CpuUsage
from i3pystatus.disk import Disk
from i3pystatus import Module
from i3pystatus.core.util import round_dict
from threading import Thread
import subprocess
import sys
import os

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



class MyDiskUsage(Disk):
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

        if available > self.display_limit:
            self.output = {}
            return

        critical = available < self.critical_limit

        cdict = {
            "total": (stat.f_bsize * stat.f_blocks) / self.divisor,
            "free": (stat.f_bsize * stat.f_bfree) / self.divisor,
            "avail": available,
            "used": (stat.f_bsize * (stat.f_blocks - stat.f_bfree)) / self.divisor,
            "percentage_free": stat.f_bfree / stat.f_blocks * 100,
            "percentage_avail": stat.f_bavail / stat.f_blocks * 100,
            "percentage_used": (stat.f_blocks - stat.f_bfree) / stat.f_blocks * 100,
        }
        round_dict(cdict, self.round_size)

        self.data = cdict
        self.output = {
            "full_text": self.format.format(**cdict),
            "color": self.critical_color if critical else self.color
        }


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
# HINTS = {}

status = Status(interval=1)

kbdd = PersistOutputModule(command='~/.config/i3blocks/kbdd', hints=dict(HINTS, min_width='English (US)'), shell=True)
status.register(kbdd)

status.register("clock",
    on_leftclick=["gsimplecal"],
    format=" %a %-d %b %X",
    hints=HINTS)

status.register("network",
    interface="eth0",
    format_up="  {bytes_sent}    {bytes_recv} MB/s",
    divisor=1024 ** 2,
    color_up="#FFFFFF",
    dynamic_color=False,
    hints=HINTS)


disk_io = PersistOutputModule(command='~/.config/i3blocks/disk-io -w 3 -M -P 0 -t 1 -s ""', hints=HINTS_NO_SEP, format="  {line}", shell=True)
status.register(disk_io)

my_cpu_usage = MyCpuUsage(format="  {usage:.2f}%",
    hints=dict(HINTS_NO_SEP, min_width=" 100.00%"), on_leftclick=['terminator -e "htop"'], interval=2)
status.register(my_cpu_usage)

status.register(MyDiskUsage(
    path="/home",
    on_leftclick=["pcmanfm-qt ~"],
    critical_limit=2,
    format=" HOME {avail} GB",
    hints=HINTS,
    interval=10))

status.register(MyDiskUsage(
    path="/workdir",
    on_leftclick=["pcmanfm-qt /workdir"],
    critical_limit=2,
    format=" WORKDIR {avail} GB",
    hints=HINTS_NO_SEP,
    interval=10))

status.register(MyDiskUsage(
    path="/",
    on_leftclick=["pcmanfm-qt /"],
    critical_limit=1,
    format=" ROOT {avail} GB",
    hints=HINTS_NO_SEP,
    interval=10))

status.register("swap",
    format=" SWAP {free} GB",
    divisor=1024 ** 3,
    color='#FFFFFF',
    hints=HINTS,
    interval=10)

status.register("mem",
    format=" MEM {avail_mem} GB",
    divisor=1024 ** 3,
    color='#FFFFFF',
    hints=HINTS_NO_SEP,
    interval=10)

status.register("pulseaudio",
    format="♪ {volume}",
    hints=HINTS)

status.run()