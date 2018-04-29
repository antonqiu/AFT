import sys
from cement.utils import shell
from pathlib import Path


class AFTPackageManager:
    def __init__(self, log, options):
        self.log = log
        self.options = options

    def list(self):
        cmd = ['adb', 'shell', 'pm', 'list', 'packages', '-u', '-f']
        shell.exec_cmd2(cmd)

    def usage(self):
        cmd = ['adb', 'shell', 'cat', 'data/system/package-usage.list']
        shell.exec_cmd2(cmd)