"""
In this example, some basic filesystem tasks are utilized to build the devops distribution package.
"""

import os
from devops.workflow.workflow import *
from devops.workflow.core import *
from devops.workflow.tasks.git import *
from devops.workflow.tasks.system import *


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


def get_setup_dir_conditional(config):
    setup_dir_conditional = IfElse(os.path.exists(config['distribution_root_directory']))
    make_dist_dir = 'Make Distribution Directory.', MakeDirectory(config['distribution_root_directory'])

    setup_dir_conditional.add_true_handler('Clean Distribution Directory.',
                                           Delete(config['distribution_root_directory'],
                                                  fail_on_error=True))
    setup_dir_conditional.add_true_handler(make_dist_dir[0], make_dist_dir[1])
    setup_dir_conditional.add_false_handler(make_dist_dir[0], make_dist_dir[1])

    return setup_dir_conditional


@entry_point
@colorize_output
@basic_logging_configuration_setup('BuildDevOpsPackage.log')
@variable_config
def main(variable_config):
    config = get_configuration_data(variable_config)
    setup_dir_conditional = get_setup_dir_conditional(config)

    workflow = MainSequence()

    workflow.addstep('If Distribution Directory is Not Empty, Clean it. Else, Create Empty Distribution Directory.', setup_dir_conditional)
    workflow.addstep('Get Source Code From Git', Clone(config['remote_git_repo'], config['local_git_repo']))
    workflow.addstep('Build Distribution Using setuptools',
                     ExecuteCommand([config['python_location'],
                                     config['setup_py_abs_path'], 'sdist'],
                                    working_directory=config['source_distribution_directory']))

    workflow.execute()
