"""
In this example, some basic filesystem tasks are utilized to build the devops distribution package.
"""

import os
from devops.workflow.workflow import *
from devops.workflow.core import *
import devops.workflow.tasks.git
import devops.workflow.tasks.system


def get_configuration_data(variable_config):

    """
    As a future enhancement: I'd like to have this auto parsed into a dictionary; this code feels a little "boiler-plate-ish" to me.
    """

    configuration_data = {}
    configuration_data['current_file_path'] =  os.path.dirname(os.path.abspath(__file__))
    configuration_data['distribution_root_directory'] = os.path.join(configuration_data['current_file_path'], variable_config.config['Default']['distributionRootDirectory'])
    configuration_data['source_distribution_directory'] = os.path.join(configuration_data['current_file_path'], variable_config.config['Default']['sourceDistributionDirectory'])
    configuration_data['remote_git_repo'] = variable_config.config['Default']['remoteGitRepo']
    configuration_data['local_git_repo'] = os.path.join(configuration_data['current_file_path'], variable_config.config['Default']['localGitRepo'])
    configuration_data['python_location'] = variable_config.config['Default']['pythonLocation']
    configuration_data['setup_py_abs_path'] = os.path.join(configuration_data['source_distribution_directory'], 'setup.py')
    return configuration_data


@entry_point
@colorize_output
@basic_logging_configuration_setup('BuildDevOpsPackage.log')
@variable_config
def main(variable_config):
    configuration_data = get_configuration_data(variable_config)

    workflow = MainSequence()
    setup_dir_conditional = IfElse(os.path.exists(configuration_data['distribution_root_directory']))
    setup_dir_conditional.add_true_handler('Clean Distribution Directory.', devops.workflow.tasks.system.Delete(configuration_data['distribution_root_directory'], fail_on_error=True))
    setup_dir_conditional.add_true_handler('Make Distribution Directory.', devops.workflow.tasks.system.MakeDirectory(configuration_data['distribution_root_directory']))
    setup_dir_conditional.add_false_handler('Make Distribution Directory.', devops.workflow.tasks.system.MakeDirectory(configuration_data['distribution_root_directory']))
    workflow.addstep('If Distribution Directory is Not Empty, Clean it. Else, Create Empty Distribution Directory.', setup_dir_conditional)
    workflow.addstep('Get Source Code From Git', devops.workflow.tasks.git.Clone(configuration_data['remote_git_repo'], configuration_data['local_git_repo']))
    workflow.addstep('Build Distribution Using setuptools', devops.workflow.tasks.system.ExecuteCommand([configuration_data['python_location'], configuration_data['setup_py_abs_path'] , 'sdist'], working_directory=configuration_data['source_distribution_directory']))
    workflow.execute()
