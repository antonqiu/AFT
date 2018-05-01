from cement.utils import shell


class AFTPackageManager:
    def __init__(self, log, options):
        self.log = log
        self.options = options
        if options.keyword:
            self.keyword = options.keyword
        else:
            self.keyword = None

    def list(self):
        cmd = ['adb', 'shell', 'pm', 'list', 'packages', '-u', '-f']
        shell.exec_cmd2(cmd)

    def usage(self):
        cmd = ['adb', 'shell', 'dumpsys', 'usagestats']
        stdout, stderr, exitcode = shell.exec_cmd(cmd)
        if exitcode == 0:
            if self.keyword:
                for line in stdout.decode('utf-8').split('\n'):
                    if self.keyword in line:
                        print(line)
            else:
                print(stdout.decode('utf-8'))
        else:
            self.log.warning('package.usage module exits unexpectedly: %d.' % exitcode)
