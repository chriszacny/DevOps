"""
The devops workflow module provides the foundation for a workflow-based solution that follows a basic sequential running path. It was developed to provide a more structured approach to running operational programs / scripts.

A workflow's primary container is the Sequence. A Sequence contains an OrderedDict in which WorkflowTask items van be added using add_step(). Additional Sequence items can also be added to a parent sequence; as such the resultant structure is a tree.
When the construction of the workflow is complete, it can be executed using the execute() method.
Sequence's subclass, MainSequence, can be used as a "helper" for getting a basic workflow created. It has a few things it does to extend sequence that make it better suited the primary container. However, it is not required to use as the base container.
WorkflowTask is the abstract base class for all workflow-based tasks, including Sequence.
DevOpsTask is a super class for tasks that perform actions, such as the Copy task. As such, most of the tasks being added to a Sequence will likely be DevOpsTask items.
ControlFlowTask is a super class for control flow tasks, such is IfElse.
IfElse is the primary ControlFlowTask WorkflowTask. It is designed to work with workflow to provide basic if else functionality while staying coupled to the workflow.

It is important to note that the goal of this module isn't to enforce strict rules on how scripts, or even workflows should be executed. One should feel free to mix and match standard python variables, if/else constructs, looping constructs, etc with the workflow as necessary.
Rather, the goal is to provide some basic structure in terms of how scripts are executed, allowing many scripts that are functionally different to share several basic operational properties.
"""

import logging
import collections
import sys
import traceback
from .core import get_system_config_value
from abc import ABCMeta, abstractmethod

import colorama


class WorkflowTask(object):

    """
    WorkflowTask is the abstract base class for all workflow-based tasks, including Sequence.

    Noteworthy Methods
    =====================================
    - exceute(): The primary purpose of a WorkflowTask is to be run, or executed. Thus, the execute() abstract method.
    - _w_print(): WorkflowTask has a helper _w_print() method that takes styles and indentations into account, in addition to prining to stdout and logging.
    - _get_header_style(): Should be overridden by subclasses - is used by _w_print() to style output.
    - _get_footer_style(): Should be overridden by subclasses - is used by _w_print() to style output.
    - _get_text_style(): Should be overridden by subclasses - is used by _w_print() to style output.
    - _get_error_style(): Should be overridden by subclasses - is used by _w_print() to style output.
    - _prehook(): Template method hook method that is called by a Sequence when a WorkflowTask is executed. You can extend this method to provide additional pre-processing behavior.
    - _posthook(): Template method hook method that is called by a Sequence after a WorkflowTask is executed. You can extend this method to provide additional post-processing behavior.

    Instance Variables
    =====================================
    - self.input => A dictionary of "variables" that can be passed from one WorkflowTask to another
    - self.exhaust = The "exhaust" from a WorkflowTask as a dictionary, that will be passed into the next WorkflowTask.
    - self.step_name = The name of a WorkflowTask. It should be unique as it is used as the key of workflow steps in Sequence.
    - self.status = The status of the WorkflowTask.
    - self.continue_on_error = If this is true, and WorkflowTask raises an exception, continue to the next WorkflowTask.
    - self.parent = This is set to the parent container of the WorkflowTask. At the moment, this will be a Sequence or IfElse. The current purpose of this variable is for output indentation.
    """

    class TextStyle(object):

        """
        An "enumeration" class, used when determining text styles for WorkflowTask items.
        """

        Header=1
        Footer=2
        Text=3
        Error=4


    class Status(object):

        """
        An "enumeration" class, used when determining statuses for WorkflowTask items.
        """

        NotYetRun = 1
        Running = 2
        CompletedOK = 3
        CompletedError = 4

    __metaclass__ = ABCMeta

    def __init__(self):
        """
        Default constructor of WorkflowItem. It should not be overridden by subclasses; rather, it should be extended and called via super().
        """

        self.input = {}
        self.exhaust = {}
        self.step_name = ''
        self.status = WorkflowTask.Status.NotYetRun
        self.continue_on_error = False
        self.parent = None

    @abstractmethod
    def execute(self, step_name=''):
        """
        This method does the work of a WorkflowTask. It is required to be implemented by subclasses.
        """
        pass

    @abstractmethod
    def _get_header_style(self):
        """
        Sets the output (console, logging, etc) header style of a WorkflowTask. It is required to be implementd by subclasses.
        """

        pass

    @abstractmethod
    def _get_footer_style(self):
        """
        Sets the output (console, logging, etc) footer style of a WorkflowTask. It is required to be implementd by subclasses.
        """

        pass

    @abstractmethod
    def _get_text_style(self):
        """
        Sets the output (console, logging, etc) main text style of a WorkflowTask. It is required to be implementd by subclasses.
        """

        pass

    def _get_default_indentation_level(self):
        """
        The default indentation level of a WorkflowTask. If parent is not set on the WorkflowTask, this level is used when determining output indentation. This can be overridden by subclasses if necessary.
        """

        return 1

    def _get_indentation_level(self):
        """
        Determines the indentation level of the WorkflowTask. If parent is not set, _get_default_indentation_level() is used. Otherwise, the parent nodes are traversed back to the root to determine the
        indentation level of the task.
        """

        if self.parent is None:
            return self._get_default_indentation_level()
        else:
            return self.parent._get_indentation_level() + 1

    #TODO: Consider strategy pattern needed for this and w_print
    def _get_indentation(self, textstyle):
        """
        This relies on the output of _get_indentation_level; the INDENTATION constant is multiplied by the level to determine the actual indentation output string. In WorkflowTask, a TextStyle of Text or Error
        will always have one greater indentation string than it's header and footers.
        """

        if textstyle == WorkflowTask.TextStyle.Text or textstyle == WorkflowTask.TextStyle.Error:
            return eval(get_system_config_value('ConsoleOutput', 'indentation')) * (self._get_indentation_level() + 1)
        else:
            return eval(get_system_config_value('ConsoleOutput', 'indentation')) * self._get_indentation_level()

    def _get_error_style(self):
        """
        Sets the output (console, logging, etc) error style of a WorkflowTask (if Exceptions are raised). It is not required to be implementd by subclasses as it has a default implementation, but feel free to override that.
        """

        return eval(get_system_config_value('ConsoleOutput', 'workflowTaskErrorStyle'))

    def _w_print(self, text, textstyle=TextStyle.Text, loglevel=logging.INFO):
        """
        The primary output printer for a WorkflowTask. It is highly recommended to use this in place of print() or logging.info() or some other output printer as this will take care of logging if it is set up, in addition
        to printing to the console. If additional/different printing behavior is required, please extend this method.

        Because this is a protected method, it should only be called in its containing class.
        """

        w_print_logger = logging.getLogger('w_print_logger')
        w_print_logger.propagate = False

        if textstyle == WorkflowTask.TextStyle.Header:
            print(self._get_header_style() + self._get_indentation(WorkflowTask.TextStyle.Header) + text)
        elif textstyle == WorkflowTask.TextStyle.Footer:
            print(self._get_footer_style() + self._get_indentation(WorkflowTask.TextStyle.Footer) + text)
        elif textstyle == WorkflowTask.TextStyle.Error:
            print(self._get_error_style() + self._get_indentation(WorkflowTask.TextStyle.Error) + text)
        else:
            print(self._get_text_style() + self._get_indentation(WorkflowTask.TextStyle.Text) + text)

        w_print_logger.log(loglevel, text)

    def _prehook(self):
        """
        A hook method that is called before execute() is called. Some examples of what might be here: text indicating a WorkflowTask is starting or printing input workflow variables.
        """

        self._w_print('Input workflow variables: {}'.format(self.input))

    def _posthook(self):
        """
        A hook method that is called after execute() is complete. Some examples of what might be here: text indicating a WorkflowTask is complete or printing exhaust workflow variables.
        """

        self._w_print('Exhaust workflow variables {}'.format(self.exhaust))


class DevOpsTask(WorkflowTask):

    """
    DevOpsTask is a super class for all concrete devops tasks like Copy or Ftp. It has some basic structure set up in terms of its header style, text styles and such.
    """

    def __init__(self):
        super().__init__()

    def _get_header_style(self):
        return eval(get_system_config_value('ConsoleOutput', 'devOpsTaskHeaderStyle'))

    def _get_footer_style(self):
        return eval(get_system_config_value('ConsoleOutput', 'devOpsTaskFooterStyle'))

    def _get_text_style(self):
        return eval(get_system_config_value('ConsoleOutput', 'devOpsTaskTextStyle'))

    def _prehook(self):
        self._w_print('Starting ==> {}'.format(self.step_name), WorkflowTask.TextStyle.Header)
        super()._prehook()

    def _posthook(self):
        super()._posthook()
        self._w_print('Complete ==> {}'.format(self.step_name), WorkflowTask.TextStyle.Footer)


class ControlFlowTask(WorkflowTask):

    """
    ControlFlowTask is a super class for all concrete control flow tasks like IfElse or ForEach (not yet implemented). It has some basic structure set up in terms of its header style, text styles and such.
    """

    def __init__(self):
        super().__init__()

    def _get_header_style(self):
        return eval(get_system_config_value('ConsoleOutput', 'controlFlowTaskHeaderStyle'))

    def _get_footer_style(self):
        return eval(get_system_config_value('ConsoleOutput', 'controlFlowTaskFooterStyle'))

    def _get_text_style(self):
        return eval(get_system_config_value('ConsoleOutput', 'controlFlowTaskTextStyle'))

    def _prehook(self, style=''):
        self._w_print('Starting ==> {}'.format(self.step_name), WorkflowTask.TextStyle.Header)
        super()._prehook()

    def _posthook(self, style=''):
        super()._posthook()
        self._w_print('Complete ==> {}'.format(self.step_name), WorkflowTask.TextStyle.Footer)


class Sequence(WorkflowTask):

    """
    A workflow's primary container is the Sequence. A Sequence contains an OrderedDict in which WorkflowTask items van be added using add_step(). Additional Sequence items can also be added to a parent sequence;
    as such the resultant structure is a tree (if used with a ControlFlowTask). When the construction of the workflow is complete, it can be executed using the execute() method.

    Instance Variables
    =====================================
     -self._workflowsteps - the OrderedDict of WorkflowTask items.
    - self.parent = the parent this sequence. This is an explicit keyword argument of this class (vs just being a property one can set) for convenience - when setting up a Sequence in IfElse for the left and right
    steps, it is easy to just set this constructor parameter; in other cases, it is just set later.
    """

    def __init__(self, parent=None):
        super().__init__()
        self._workflowsteps = collections.OrderedDict()
        self.parent = parent

    def _get_header_style(self):
        return eval(get_system_config_value('ConsoleOutput', 'sequenceHeaderStyle'))

    def _get_footer_style(self):
        return eval(get_system_config_value('ConsoleOutput', 'sequenceFooterStyle'))

    def _get_text_style(self):
        return eval(get_system_config_value('ConsoleOutput', 'sequenceTextStyle'))

    def execute(self, step_name='', existing_variables=None):
        """
        The Sequence implementation of execute is the primary driver of a workflow. It iterates over all of the steps in workflowsteps exceuting each one in order. It also takes care of calling the pre and posthook
        methods of the WorkflowTask, in addition to pushing workflowvariables through the pipeline.
        """

        super().execute(step_name)

        if existing_variables is not None:
            workflowvariables = existing_variables
        else:
            workflowvariables = {}

        print('\n')

        errors_found = False
        for key in self._workflowsteps:
            try:
                self._workflowsteps[key].input = workflowvariables
                self._workflowsteps[key]._prehook()
                self._workflowsteps[key].execute(step_name=key)
                self._workflowsteps[key]._posthook()
                workflowvariables.update(self._workflowsteps[key].exhaust)
                self._workflowsteps[key].status = WorkflowTask.Status.CompletedOK
                print('\n')

            except:
                errors_found = True
                self._workflowsteps[key].status = WorkflowTask.Status.CompletedError
                self._w_print("Unexpected error in workflow step {}.".format(key), WorkflowTask.TextStyle.Error, loglevel=logging.ERROR)
                errorlist = traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                for e in errorlist:
                    self._w_print(e, WorkflowTask.TextStyle.Error)

                if self._workflowsteps[key].continue_on_error is True:
                    continue
                else:
                    raise

        if errors_found is True:
            self.status = WorkflowTask.Status.CompletedError
        else:
            self.status = WorkflowTask.Status.CompletedOK

    def addstep(self, workflowname, workflow):
        """
        addstep() is specific to the Sequence class. It is the primary way to add WorkflowTask items to the Sequence.
        """

        self._workflowsteps[workflowname] = workflow
        self._workflowsteps[workflowname].step_name = workflowname
        self._workflowsteps[workflowname].parent = self

    def get(self, key):
        """
        get() allows access to the Sequence's set of workflow steps.
        """

        return self._workflowsteps[key]


class MainSequence(Sequence):

    """
    MainSequence is a helper class that is intended to serve as the main or primary Sequence of a workflow. It takes care of setting the default indentation level,
    in addition to outputting the start and complete messages of a standard workflow.
    """

    def __init__(self):
        super().__init__()

    def execute(self, step_name='', existing_variables=None):
        self._prehook()
        super().execute(step_name)
        self._posthook()

    def _prehook(self):
        self._w_print('Starting ==> Primary Sequence', WorkflowTask.TextStyle.Header)
        super()._prehook()

    def _posthook(self):
        super()._posthook()
        self._w_print('Complete ==> Primary Sequence', WorkflowTask.TextStyle.Footer)

    def _get_default_indentation_level(self):
        return 0


class IfElse(ControlFlowTask):

    """
    IfElse is a concrete control flow task that behaves like any if else conditional statement found in standard language grammars. To use:
    test = IfElse( 1 != 2 )
    test.add_true_handler(some_workflow_task)
    test.add_false_handler(some_workflow_task1)

    OR:

    test = IfElse( 1 != 2, ifworkflowname='some_workflow', ifworkflow=some_workflow_task, elseworkflowname='some_else_workflow', elseworkflow=some_workflow_task1 )

    Noteworthy Methods
    =====================================
    - exceute(): This will evaluate the condition property set in the constructor. If it is true, the workflow task set in add_true_handler (or the if portion of the constructor) is called. Otherwise the
    workflow task set in add_false_handler (or the false portion of the constructor) is called.
    - add_true_handler(): Can be called multiple times for multiple workflow tasks. All tasks set via this method will execute if the true condition evaluates to true.
    - add_false_handler(): Can be called multiple times for multiple workflow tasks. All tasks set via this method will execute if the true condition evaluates to false.

    Instance Variables
    =====================================
    - self.condition: The condition that must be satisfied for the tasks in self._leftsteps to be executed.
    - self._leftsteps: If self.condition evaluates to true, these steps will be executed.
    - self._rightsteps: If self.condition evaluates to false, these steps will be executed.
    """

    def __init__(self, condition, ifworkflowname=None, ifworkflow=None, elseworkflowname=None, elseworkflow=None):
        """
        Sets up IfElse; if all arguments are passed in (including keyword args) it will take care of adding a true and false handler. If multiple true and false handlers are needed, condition should be supplied,
        and then add_true_handler() and add_false_handler() should be called multiple times after IfElse is constructed.
        """

        super().__init__()
        self.condition = condition
        self._leftsteps = Sequence(parent=self)
        self._rightsteps = Sequence(parent=self)
        if ifworkflow is not None and ifworkflowname is not None:
            self.add_true_handler(ifworkflowname, ifworkflow)
        if elseworkflowname is not None and elseworkflow is not None:
            self.add_false_handler(elseworkflowname, elseworkflow)

    def execute(self, step_name=''):
        """
        This will evaluate the condition property set in the constructor. If it is true, the workflow task set in add_true_handler (or the if portion of the constructor) is called. Otherwise the
        workflow task set in add_false_handler (or the false portion of the constructor) is called.
        """

        super().execute(step_name)
        if self.condition is True:
            self._w_print('Conditional evaluates to True.')
            self._leftsteps.execute(existing_variables=self.input)
        else:
            self._w_print('Conditional evaluates to False.')
            self._rightsteps.execute(existing_variables=self.input)

    def add_true_handler(self, workflowname, workflow):
        """
        Can be called multiple times for multiple workflow tasks. All tasks set via this method will execute if the true condition evaluates to true.
        """

        self._leftsteps.addstep(workflowname, workflow)

    def add_false_handler(self, workflowname, workflow):
        """
        Can be called multiple times for multiple workflow tasks. All tasks set via this method will execute if the true condition evaluates to false.
        """

        self._rightsteps.addstep(workflowname, workflow)
