"""
The filesystem module offers classes that deal with filesystem tasks.

The Copy class copies a file from one location to another.
"""

import os
import shutil
import subprocess
from ..workflow import DevOpsTask


class Copy(DevOpsTask):

    """
    The Copy class copies an operating system entity from one location to another.
    """

    def __init__(self, source, destination):

        """
        self.source => The source file to copy.
        self.destination => The target (output) file.
        """

        super().__init__()
        self.source = source
        self.destination = destination

    def execute(self, step_name=''):

        """
        Copies a file from one location to another.
        """

        super().execute(step_name)
        self._w_print('Copying {} to {}'.format(self.source, self.destination))
        shutil.copy2(self.source, self.destination)


class MakeDirectory(DevOpsTask):

    """
    The MakeDirectory class makes a directory if it doesn't already exist.
    """

    def __init__(self, directory_to_create):

        """
        self.directory_to_create => The directory to create
        """

        super().__init__()
        self.directory_to_create = directory_to_create

    def execute(self, step_name=''):

        """
        This is basically just a wrapper for os.makedirs()
        """

        super().execute(step_name)
        self._w_print('Making directory {}'.format(self.directory_to_create))
        os.makedirs(self.directory_to_create, exist_ok=True)


class Delete(DevOpsTask):

    """
    The Delete class removes an operating system entity, whether that be file or directory. If the Delete task cannot remove an item for whatever reason, the task will fail.
    """

    def __init__(self, item_to_delete, fail_on_error=False):

        """
        self.item_to_delete => The os item to delete
        """

        super().__init__()
        self.item_to_delete = item_to_delete
        self.fail_on_error = fail_on_error

    def execute(self, step_name=''):

        """
        Will remove a file or directory specified by item_to_delete constructor parameter
        """

        super().execute(step_name)
        try:
            if os.path.exists(self.item_to_delete):
                if os.path.isdir(self.item_to_delete):
                    self._w_print('Removing directory {}'.format(self.item_to_delete))
                    shutil.rmtree(self.item_to_delete, onerror=delete_onerror)
                else:
                    self._w_print('Removing file {}'.format(self.item_to_delete))
                    os.remove(self.item_to_delete)
        except OSError:
            self._w_print('Error removing item {}. Please make sure that the item is not protected / read-only.'.format(self.item_to_delete))
            if self.fail_on_error is True:
                raise


def delete_onerror(func, path, exc_info):
    """
    Original source for this function: http://www.voidspace.org.uk/downloads/pathutils.py

    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


class ExecuteCommand(DevOpsTask):

    """
    Executes a command on the command line.
    """

    def __init__(self, command, working_directory=None):

        """
        self.command => The command to execute. This should be passed in as a list of format: [executable_name, arg1, arg2,...]
        self.working_directory => The working directory to execute the command in. Default is None. If not specified, the current working directory is used.
        """

        super().__init__()
        self.command = command
        self.working_directory = working_directory


    def execute(self, step_name=''):

        """
        Will run the command specified by self.command
        """

        super().execute(step_name)
        self._w_print('Attempting to run command {}'.format(self.command))
        proc = subprocess.Popen(args=self.command, cwd=self.working_directory, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = proc.communicate()
        self._w_print('Result: {}'.format(out))
