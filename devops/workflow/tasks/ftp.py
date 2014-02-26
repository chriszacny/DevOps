"""
The ftp module offers classes that deal with ftp'ing files.

The Ftp class is currently a "shim" and will be fully fleshed-out in coming versions.
"""

from workflow.workflow import DevOpsTask


class Ftp(DevOpsTask):
    class FtpOperation:
        SendFiles = 1
        ReceiveFiles = 2
        ListFiles = 3

    def __init__(self, operation, config_name, source, destination):
        super().__init__()
        self.source = source
        self.destination = destination
        self.operation = operation
        self.config_name = config_name

    def execute(self, step_name=''):
        super().execute(step_name)
        self._w_print('Uploading {} to {}'.format(self.source, self.destination))