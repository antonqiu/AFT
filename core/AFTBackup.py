from cement.utils import shell

from core.CoreUtil import CoreUtil


class AFTBackup:

    def __init__(self, log, options):
        self.log = log
        self.options = options

    def execute(self):
        cmd = ['adb', 'backup']
        if self.options.apk:
            cmd.append('-apk')
        if self.options.all:
            cmd.append('-all')
        if self.options.system:
            cmd.append('-system')
        if self.options.obb:
            cmd.append('-obb')
        if self.options.shared:
            cmd.append('-shared')
        if self.options.filename:
            cmd.append('-f %s' % self.options.filename)
        exitcode = shell.exec_cmd2(cmd)
        self.log.debug('adb backup exit: %d.' % exitcode, __name__)
        if exitcode == 0:
            # self.log.info('Done.')
            # self.log.info('Backup is saved as: %s' % self.options.filename)
            CoreUtil.hash(self.options.filename)
        else:
            self.log.warning('Logical Acquisition module exit unexpectedly: %d.' % exitcode)

    def unpack(self):
        cmd = ['java', '-jar', 'lib/abe.jar', 'unpack', self.options.in_backup[0], self.options.out_archive[0]]
        exitcode = shell.exec_cmd2(cmd)
        self.log.debug('abe exit: %d.' % exitcode, __name__)
        if exitcode == 0:
            # self.log.info('Done.')
            # self.log.info('tar archive is saved as: %s' % self.options.out_archive[0])
            CoreUtil.hash(self.options.out_archive[0])
        else:
            self.log.warning('Backup Unpack module exit unexpectedly: %d.' % exitcode)
