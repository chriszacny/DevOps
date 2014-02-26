"""
In this example, some web and data transformation tasks are used to get an Excel file from a web url, and transform it into a csv file for potential parsing by an arbitrary process.
"""

import os
from devops.workflow.workflow import *
from devops.workflow.core import *
from devops.workflow.tasks import web
from devops.workflow.tasks import datatransformation


@entry_point
@colorize_output
@basic_logging_configuration_setup('EurexMarginScraper.log')
@variable_config
def main(variable_config):
    workflow = MainSequence()

    configuration_data = {}
    configuration_data['current_file_path'] =  os.path.dirname(os.path.abspath(__file__))
    configuration_data['remote_xls_url'] =  variable_config.config['Default']['remoteXlsUrl']
    configuration_data['save_local_xls'] = os.path.join(configuration_data['current_file_path'], variable_config.config['Default']['saveLocalXls'])
    configuration_data['xls_to_csv_destination'] = os.path.join(configuration_data['current_file_path'], variable_config.config['Default']['xlsToCsvDestination'])

    workflow.addstep('Retrieve Remote Eurex Margin Data (XLS)', web.HttpDataRetrieval(configuration_data['remote_xls_url'], configuration_data['save_local_xls']))
    workflow.addstep('Convert XLS Data to CSV', datatransformation.XlsToCsv(configuration_data['save_local_xls'], configuration_data['xls_to_csv_destination']))
    workflow.execute()
