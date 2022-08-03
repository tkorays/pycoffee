from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QMessageBox, QLCDNumber
import click
import sys
import os
import io
from datetime import timedelta, datetime

from Coffee.Core.NtpSync import NtpSync
from Coffee.Core.Utils import web_page_compare


@click.command("nbclock", help="[in] net based clock")
@click.option("--delay", '-d', required=False, default=0, help="render delay(ms)")
def play_nbclock(delay):
    class MYClock(QWidget):
        def __init__(self, delay=0):
            super().__init__()
            self.delay = delay
            self.ntp = NtpSync()
            if not self.ntp.sync():
                click.echo("sync failed!")
                self.ready = False
            else:
                self.ready = True

            self.initUi()
            self.init_timer()

        def update_time(self):
            ts = self.ntp.now() + timedelta(milliseconds=self.delay)
            self.lcd.display(ts.strftime('%H:%M:%S:%f'))

        def init_timer(self):
            self.timer = QTimer()
            self.timer.setInterval(15)
            self.timer.start()
            self.timer.timeout.connect(self.update_time)

        def initUi(self):
            self.resize(550, 150)
            self.setWindowTitle("NetBasedClock")

            # 初始化 调色板
            self.pl = QPalette()
            self.pl.setColor(QPalette.Background, Qt.white)
            self.setAutoFillBackground(True)
            self.setPalette(self.pl)  # 设置顶层布局

            ts = self.ntp.now() + timedelta(milliseconds=self.delay)
            self.lcd = QLCDNumber()
            self.lcd.setDigitCount(15)
            self.lcd.setMode(QLCDNumber.Dec)
            self.lcd.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
            self.lcd.setStyleSheet("border: 2px solid black; color: black;")
            self.lcd.setMinimumWidth(500)
            self.lcd.setMinimumHeight(100)
            self.lcd.display(ts.strftime('%H:%M:%S:%f'))
            # 初始化盒子布局
            self.box_layout = QGridLayout()
            self.box_layout.addWidget(self.lcd)  # 添加LCD组件

            self.box_layout.setAlignment(Qt.AlignCenter)  # 设置组件在布局中间
            self.setLayout(self.box_layout)  # 设置窗体布局

            self.show()

        def init_clock(self):
            print("start init clock")

        def on_click(self):
            print("PyQt5 button click")

        def closeEvent(self, event):
            reply = QMessageBox.question(self, 'Message',
                                         "Are you sure to quit?", QMessageBox.Yes |
                                         QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

    app = QApplication(sys.argv)
    clock = MYClock(delay=delay)
    if not clock.ready:
        return
    app.exec_()


@click.command("split", help="[in] split log to small parts")
@click.option('-f', '--filepath', required=True, help='input log path')
@click.option('-s', '--chunksize', default=100, required=True, help='single file size(MBytes)')
@click.option('-o', '--outdir', default='', required=False, help='output dir')
def play_file_split(filepath, chunksize, outdir):
    if not os.path.exists(filepath):
        click.echo('bad input file')
        return
    input_filename = os.path.basename(filepath)

    chunksize = chunksize * 1024 * 1024

    outdir = outdir if outdir else os.path.join(os.path.dirname(filepath), input_filename + "_split")
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    with io.open(filepath, 'rb') as f:
        idx = 0
        while True:
            idx += 1
            chunk = f.read(chunksize)
            if not chunk:
                break

            filename = os.path.join(outdir, '{}.{}'.format(
                input_filename,
                idx
            ))
            outfile = io.open(filename, 'wb')
            outfile.write(chunk)
            outfile.close()
        click.echo('split success, {} part has been devided!'.format(idx))


@click.command('pcap', help='[in] capture network packet')
@click.option('--filename', '-f', required=False, help='file name of cap file')
@click.option('--interface', '-i', required=True, help='interface name')
def play_pcap(filename, interface):
    if not filename:
        coffee_dir = os.path.join(os.path.expanduser('~'), '.coffee')
        if not os.path.exists(coffee_dir):
            os.mkdir(coffee_dir)
        if not os.path.exists(coffee_dir):
            click.echo("mkdir '%s' failed" % coffee_dir)
            return
        pcap_dir = os.path.join(coffee_dir, 'pcap')
        if not os.path.exists(pcap_dir):
            os.mkdir(pcap_dir)
        if not os.path.exists(pcap_dir):
            click.echo("failed to make pcap dir!")
            return
        now = datetime.now()
        filename = os.path.join(pcap_dir, '{:04d}-{:02d}-{:02d}_{:02d}{:02d}{:02d}.cap'.format(
            now.year, now.month, now.day, now.hour, now.minute, now.second))
    import distutils.spawn
    if not distutils.spawn.find_executable('tcpdump'):
        click.echo('tcpdump is not in PATH!!!')
        return
    os.system('tcpdump -i {} -s0 -C 50 -w "{}"'.format(interface, filename))


@click.command("wc", help="[in] webpage compare")
@click.option("-a", required=True, help="link a")
@click.option("-b", required=True, help="link b")
def play_webpage_compare(a: str, b: str):
    web_page_compare('compare web', a, b)


commands = [play_nbclock, play_file_split, play_pcap, play_webpage_compare]
