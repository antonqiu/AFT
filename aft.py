import sys

from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose
from cement.utils import shell

from core.AFTBackup import AFTBackup
from core.AFTExtract import AFTExtract


class AFTSafeHandlingWarning(shell.Prompt):
    class Meta:
        text = '''
The device should be isolated from the network, preventing any possibility of a remote device wipe. 
This can be achieved by:
    1. Removing the SIM card
    2. Turning airplane mode on
    3. Making certain Wi-Fi is disabled
    
The option “USB Debugging” must be allowed in the settings.
(Settings → Developer Options.)

Is your device prepared for data acquisition?
        '''
        options = ['yes', 'no']
        options_separator = '|'
        default = 'no'
        clear = True

    def process_input(self):
        if self.input.lower() == 'yes':
            print()
            pass
        else:
            sys.exit(1)


class AFTBaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = "Android Forensics Toolkit"

    @expose(hide=True)
    def default(self):
        self.app.log.info('Inside MyBaseController.default()')
        if self.app.pargs.foo:
            print("Recieved option: foo => %s" % self.app.pargs.foo)


class AFTBackupController(CementBaseController):
    class Meta:
        label = 'backup'
        description = 'logical acquisition of an Android device via ADB.'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['--apk'],
             dict(action='store_true', help='enables backup of the *.apk files themselves.')),
            (['--all'],
             dict(action='store_true', help='enables backup of all installed applications.')),
            (['--system'],
             dict(action='store_true', help='includes backup of system applications (enabled by default).')),
            (['--obb'],
             dict(action='store_true',
                  help='includes backup of installed apk expansion (.obb) files associated with each application.')),
            (['--shared'],
             dict(action='store_true',
                  help='enables backup of the devices shared storage. This may take long to execute.')),
            (['-f'],
             dict(action='store', dest='filename',
                  help='location of a specified *.ab file.', default='./backup.ab')),
        ]

    @expose(hide=True)
    def default(self):
        AFTSafeHandlingWarning()
        self.app.log.debug('entering backup controller', __name__)
        AFTBackup(log=self.app.log, options=self.app.pargs).execute()


class AFTUnpackController(CementBaseController):
    class Meta:
        label = 'unpack'
        description = 'parse an Android device backup to a tar archive'
        usage = 'usage: aft unpack in_backup out_archive [options...]'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['in_backup'],
             dict(action='store', help='path of input adb backup', nargs=1)),
            (['out_archive'],
             dict(action='store', help='target path for output tar archive', nargs=1)),
        ]

    @expose(hide=True)
    def default(self):
        self.app.log.debug('entering unpack controller', __name__)
        AFTBackup(log=self.app.log, options=self.app.pargs).unpack()


class AFTExtractionController(CementBaseController):
    class Meta:
        label = 'extract'
        description = 'extract specific information from an Android device.'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['--outDir'],
             dict(action='store', dest='out_dir', help='output directory')),
            (['-r', '--rule'],
             dict(action='store', dest='rule', help='custom extracting rule')),
        ]

    @expose(help='extract SMS database.')
    def sms(self):
        default_rule = './conf/bundle/sms.json'
        if self.app.pargs.rule:
            if not self.app.config.parse_file(self.app.pargs.rule):
                self.app.log.warning('Failed to parse specified rule. Roll back to default.')
        else:
            self.app.config.parse_file(default_rule)
        AFTExtract(log=self.app.log, options=self.app.pargs).execute(
            self.app.config.get('extract.sms', 'bundle_name'),
            self.app.config.get('extract.sms', 'paths'),
            self.app.config.get('extract.sms', 'targets'),
        )

    @expose(help='extract call log database.')
    def call(self):
        self.app.log.info('Inside MyBaseController.default()')
        if self.app.pargs.foo:
            print("Recieved option: foo => %s" % self.app.pargs.foo)

    @expose(help='extract device information.')
    def device(self):
        self.app.log.info('Inside MyBaseController.default()')
        if self.app.pargs.foo:
            print("Recieved option: foo => %s" % self.app.pargs.foo)


class MyApp(CementApp):
    class Meta:
        label = 'aft'
        base_controller = 'base'
        extensions = ['json']
        config_handler = 'json'
        config_extension = '.json'
        config_files = [
            './conf/aft.json'
        ]
        handlers = [
            AFTBaseController,
            AFTBackupController,
            AFTUnpackController,
            AFTExtractionController
        ]


with MyApp() as app:
    app.setup()
    app.run()
