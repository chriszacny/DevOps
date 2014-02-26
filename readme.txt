Overview
============================
This is a pre-alpha version of the DevOps package with a start on workflow and workflow.tasks. All APIs are subject to change.

Please visit www.chriszacny.com for updates and more information.


Installation
============================
The only requirement for this package is Python 3. Specifically, it was developed using version 3.3.3.

To install:

%PYTHON_PATH%\python %PATH_TO_EXTRACTION_DIRECTORY%\setup.py install

where:
%PYTHON_PATH% is the directory path to the python binary.
%PATH_TO_EXTRACTION_DIRECTORY% is the directory path to where the pacakge was extracted.


Post Install
============================
Configure the log output directory in appsettings.cfg. If installed via setup.py, this should be in something like:

\site-packages\devops-0.0.1-py3.3.egg\devops\workflow\


Usage
=============================
Please see the examples directory for some usage examples. Before attempting to run the examples, please install the package to your python instance. Then configure the
.cfg files for the examples accordingly. Also, be sure to make any appropriate changes to the workflow configuration file, mentioned in the Post Install section above.

