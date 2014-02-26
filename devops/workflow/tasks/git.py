"""
The git module offers classes that deal with git source control tasks.
"""

from .system import ExecuteCommand
from ..workflow import DevOpsTask
from ..core import get_system_config_value

class Clone(DevOpsTask):

    """
    Clones a remote repo into a local one.
    """

    def __init__(self, remote_repo_url, local_repo):

        """
        self.remote_repo_url => The url of the remote repository.
        self.local_repo => The location of the local repository.
        """

        super().__init__()
        self.local_repo = local_repo
        self.remote_repo_url = remote_repo_url

    def execute(self, step_name=''):

        """
        Executes a 'git clone self.remote_repo_url self.local_repo'
        """

        super().execute(step_name)
        self._w_print('Attempting to run git clone {} {}'.format(self.remote_repo_url, self.local_repo))
        command_execution = ExecuteCommand([get_system_config_value('SourceControl', 'git'), 'clone', self.remote_repo_url, self.local_repo])
        command_execution.execute()