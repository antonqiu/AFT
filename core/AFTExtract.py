from cement.utils import shell
from pathlib import Path
from core.CoreUtil import CoreUtil


class AFTExtract:

    def __init__(self, log, options):
        self.out_dir = './artifact'
        self.log = log
        self.options = options
        if self.options.out_dir:
            self.out_dir = self.options.out_dir
            self.log.debug('out_dir is overwritten: %s' % self.options.out_dir, __name__)

    def execute(self, bundle_name, paths, targets):
        if len(paths) < 1 or len(targets) < 1:
            self.log.error('Invalid rule: paths or targets is empty')
        rt_out_dir = self.out_dir + '/' + bundle_name
        if Path(rt_out_dir).exists():
            print('Output directory exists. Files may be overwritten.')
            shell.Prompt("Press Enter To Continue", default='ENTER')
        else:
            Path(rt_out_dir).mkdir(parents=True)
        for path in paths:
            if not path.endswith('/'):
                path += '/'
            for target in targets:
                target.rstrip('/')
                target_path = path + target
                self.log.debug('extracting: %s' % target_path, __name__)
                self.log.debug('to: %s' % rt_out_dir, __name__)
                cmd = ['adb', 'pull', target_path, rt_out_dir]
                exitcode = shell.exec_cmd2(cmd)
                if exitcode != 0:
                    self.log.warning('extraction module exit unexpectedly: %d.' % exitcode)
