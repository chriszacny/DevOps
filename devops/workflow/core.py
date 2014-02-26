"""
The core module provides a set of core classes to be used by workflow. All of these classes are optional for use, with the exception of the colorize_output decorator; please see below for more information about that.

The Singleton class is a classic Singleton, implemented in Python.
The VariableManager is a Singleton. It is setup by the variable_config decorator. It provides simple access to key-value config file values.

The entry_point decorator was adapted from code located at: http://slowchop.com/2011/01/25/automain/. It allows the user to not have to type the standard if __name__ == '__main__' : main()
The colorize_output decorator initializes the colorama module. For Windows users, it is highly recommended that this decorator be used on main(), or at least, initialize colorama yourself. At the moment, the ascii
    color codes will be printed out in place of color if colorama isn't initialized. In the future, it is intended to be an optional feature.
The basic_logging_configuration_setup decorator will setup logging with a "basic" configuration. This means that both file and console logging are setup. To setup the logging directory, it should be set in
    \devops\workflow\appsettings.cfg.
The variable_config decorator sets up VariableManager for use in scripts. Note that it passes the instance of VariableManager to the function it decorates.
"""

import inspect
import colorama
import configparser
import os
import logging
import datetime
import sys
from functools import wraps


class Singleton(type):

    """
    The Singleton class is a classic Singleton, implemented in Python.
    """

    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance


class VariableManager(metaclass=Singleton):

    """
    The VariableManager is a Singleton. It is setup by the variable_config decorator. It provides simple access to key-value config file values. To use it, you should define a workflowvariables.cfg to sit alongside
    whatever python module/script you are creating. In the file, it should look something like:

    [Default]
    remoteXlsUrl = http://www.eurexclearing.com/blob/clearing-en/51554-156220/235238/14/data/marginparametersestimationcircular.xls
    saveLocalXls = MarginParameterEstimationCircular.xls
    xlsToCsvDestination = MarginParameterEstimationCircular.csv

    You can then use it like:

    config['Default']['saveLocalXls']
        Should output => MarginParameterEstimationCircular.xls
    """

    def __init__(self):
        self.config = configparser.ConfigParser()
        pathtoprimary = os.path.join(os.getcwd(), sys.argv[0])
        path = os.path.split(pathtoprimary)
        self.config.read(os.path.join(path[0], r'workflowvariables.cfg'))


def entry_point(func):

    """
    The entry_point decorator was adapted from code located at: http://slowchop.com/2011/01/25/automain/. It allows the user to not have to type the standard if __name__ == '__main__' : main()
    """

    parent = inspect.stack()[1][0]
    name = parent.f_locals.get('__name__', None)
    if name == '__main__':
        func()
    return func


def colorize_output(func):

    """
    The colorize_output decorator initializes the colorama module. For Windows users, it is highly recommended that this decorator be used on main(), or at least, initialize colorama yourself. At the moment, the ascii
        color codes will be printed out in place of color if colorama isn't initialized. In the future, it is intended to be an optional feature.
    """

    def decorate():
        colorama.init(autoreset=True)
        func()
    return decorate


def get_system_config_value(header, key):
    config = configparser.ConfigParser()
    path = os.path.dirname(__file__)
    config.read(os.path.join(path, r'appsettings.cfg'))
    return config[header][key]


def basic_logging_configuration_setup(name=None):

    """
    The basic_logging_configuration_setup decorator will setup logging with a "basic" configuration. This means that both file and console logging are setup. To setup the logging directory, it should be set in
        \devops\workflow\appsettings.cfg.
    """

    def decorate(func):
        logname = name if name else func.__module__ + ".log"

        @wraps(func)
        def wrapper(*args, **kwargs):
            datestring = datetime.datetime.now().strftime('.%Y%m%d.%f')
            if '.' in logname:
                i = logname.rindex('.')
                prefix = logname[0:i]
                suffix = logname[i:]
                prefix += datestring
                customlogname = prefix + suffix
            else:
                customlogname = logname + datestring

            config = configparser.ConfigParser()
            path = os.path.dirname(__file__)
            config.read(os.path.join(path, r'appsettings.cfg'))
            logdir = get_system_config_value('Default', 'logDirectory')

            if not os.path.exists(logdir):
                os.makedirs(logdir)

            # 1. Setup basic logging configuration. This will log to both the console and the specified file
            logging.basicConfig(filename=os.path.join(logdir, customlogname),
                                filemode='w',
                                level=logging.DEBUG,
                                format='%(asctime)s:%(levelname)s: %(message)s',
                                datefmt='%Y/%m/%d %I:%M:%S %p')

            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            logging.getLogger('').addHandler(console)

            # 2. Setup specialized w_print logger. This will only log to a file in order to allow
            # "pretty-printing" of the output to the console - we don't want this "pretty printing"
            # in the log
            w_print_logger = logging.getLogger('w_print_logger')
            w_print_logger.setLevel(logging.DEBUG)
            w_print_fh = logging.FileHandler(os.path.join(logdir, customlogname))
            w_print_fh.setLevel(logging.DEBUG)
            w_print_formatter = logging.Formatter(fmt='%(asctime)s:%(levelname)s: %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p')
            w_print_fh.setFormatter(w_print_formatter)
            w_print_logger.addHandler(w_print_fh)

            return func(*args, **kwargs)
        return wrapper
    return decorate


def variable_config(func):

    """
    The variable_config decorator sets up VariableManager for use in scripts. Note that it passes the instance of VariableManager to the function it decorates.
    """

    def decorate():
        variables = VariableManager()
        func(variables)
    return decorate

