import unittest
import colorama
import sys
from unittest.mock import MagicMock
import os

from ..workflow import Sequence
from ..workflow import MainSequence
from ..workflow import WorkflowTask
from ..workflow import IfElse
from ..tasks.system import Copy


class WorkflowTests(unittest.TestCase):
    """
    Run recursive from top tests package (i.e.): /DevOps/devops-->python -m unittest discover -v
    """

    def setUp(self):
        "Hook method for setting up the test fixture before exercising it."
        pass

    def tearDown(self):
        "Hook method for deconstructing the test fixture after testing it."
        pass

    def test_basic_workflow_structure(self):
        basic_workflow = MainSequence()
        self.assertEqual(basic_workflow._get_indentation_level(), 0)
        self.assertEqual(len(basic_workflow._workflowsteps), 0)

    def test_if_else_true_condition(self):
        sys.stdout = open("unit_test.txt", "w")
        workflow = MainSequence()
        dir = os.path.dirname(__file__)
        t = os.path.join(dir, 'testtrue.dat')
        t1 = os.path.join(dir, 'testtrue.dat1')
        f = os.path.join(dir, 'testfalse.dat')
        f1 = os.path.join(dir, 'testfalse.dat1')
        copytruewf = Copy(t, t1)
        copyfalsewf = Copy(f, f1)
        workflow.addstep('If 1 != 2', IfElse(1 != 2, 'True Statement', copytruewf, 'False Statement', copyfalsewf))
        workflow.execute()
        self.assertEqual(copytruewf.status, WorkflowTask.Status.CompletedOK)
        self.assertEqual(copyfalsewf.status, WorkflowTask.Status.NotYetRun)
        sys.stdout.close()

    def test_if_else_false_condition(self):
        sys.stdout = open("unit_test.txt", "w")
        workflow = MainSequence()
        dir = os.path.dirname(__file__)
        t = os.path.join(dir, 'testtrue.dat')
        t1 = os.path.join(dir, 'testtrue.dat1')
        f = os.path.join(dir, 'testfalse.dat')
        f1 = os.path.join(dir, 'testfalse.dat1')
        copytruewf = Copy(t, t1)
        copyfalsewf = Copy(f, f1)
        workflow.addstep('If 1 == 2', IfElse(1 == 2, 'True Statement', copytruewf, 'False Statement', copyfalsewf))
        workflow.execute()
        self.assertEqual(copyfalsewf.status, WorkflowTask.Status.CompletedOK)
        self.assertEqual(copytruewf.status, WorkflowTask.Status.NotYetRun)
        sys.stdout.close()

    def test_if_else_add_handlers(self):
        copytruewf = Copy(r'c:\true.log', r'c:\true.log')
        copyfalsewf = Copy(r'c:\false.log', r'c:\false.log')
        if_else_task = IfElse(1 != 2)
        if_else_task.add_true_handler("test add true handler", copytruewf)
        if_else_task.add_false_handler("test add false handler", copyfalsewf)
        self.assertEqual(if_else_task._leftsteps._workflowsteps["test add true handler"], copytruewf)
        self.assertEqual(if_else_task._rightsteps._workflowsteps["test add false handler"], copyfalsewf)

    def test_sequence_get(self):
        copytruewf = Copy(r'c:\true.log', r'c:\true.log')
        copyfalsewf = Copy(r'c:\false.log', r'c:\false.log')
        if_else_task = IfElse(1 != 2)
        if_else_task.add_true_handler("test add true handler", copytruewf)
        if_else_task.add_false_handler("test add false handler", copyfalsewf)
        self.assertEqual(if_else_task._leftsteps.get("test add true handler"), copytruewf)
        self.assertEqual(if_else_task._rightsteps.get("test add false handler"), copyfalsewf)

    def test_sequence_addstep(self):
        workflow = MainSequence()
        workflow.addstep('test', Copy('/test1', '/test2'))
        self.assertEqual(len(workflow._workflowsteps), 1)

    def test_sequence_execute(self):
        sys.stdout = open("unit_test.txt", "w")
        workflow = MainSequence()
        copy = Copy('/test1', '/test2')
        copy.execute = MagicMock()
        workflow.addstep('test', copy)
        workflow.execute()
        self.assertEqual(workflow._workflowsteps['test'].status, WorkflowTask.Status.CompletedOK)
        self.assertTrue(workflow.status, WorkflowTask.Status.CompletedOK)
        sys.stdout.close()

    def test_sequence_execute_unexpected_error(self):
        sys.stdout = open("unit_test.txt", "w")
        workflow = MainSequence()
        copy = Copy('/test1', '/test2')
        copy.continue_on_error = True

        def exception_func():
            raise

        copy_mock = MagicMock(side_effect=exception_func)
        copy.execute = copy_mock
        workflow.addstep('test', copy)
        workflow.execute()
        self.assertEqual(workflow._workflowsteps['test'].status, WorkflowTask.Status.CompletedError)
        self.assertEqual(workflow.status, WorkflowTask.Status.CompletedError)
        sys.stdout.close()

    def test_sequence_get_header_style(self):
        test_if = IfElse(1 != 2)
        self.assertEqual(test_if._get_header_style(), colorama.Fore.YELLOW + colorama.Style.DIM)
        test_main_sequence = MainSequence()
        self.assertEqual(test_main_sequence._get_header_style(), colorama.Back.BLUE + colorama.Fore.CYAN)
        test_sequence = Sequence()
        self.assertEqual(test_sequence._get_header_style(), colorama.Back.BLUE + colorama.Fore.CYAN)
        test_copy = Copy('', '')
        self.assertEqual(test_copy._get_header_style(), colorama.Fore.WHITE + colorama.Style.DIM)

    def test_sequence_get_footer_style(self):
        test_if = IfElse(1 != 2)
        self.assertEqual(test_if._get_footer_style(), colorama.Fore.YELLOW)
        test_main_sequence = MainSequence()
        self.assertEqual(test_main_sequence._get_footer_style(), colorama.Back.BLUE + colorama.Fore.CYAN)
        test_sequence = Sequence()
        self.assertEqual(test_sequence._get_footer_style(), colorama.Back.BLUE + colorama.Fore.CYAN)
        test_copy = Copy('', '')
        self.assertEqual(test_copy._get_footer_style(), colorama.Fore.WHITE)

    def test_sequence_get_text_style(self):
        test_if = IfElse(1 != 2)
        self.assertEqual(test_if._get_text_style(), colorama.Fore.YELLOW + colorama.Style.DIM)
        test_main_sequence = MainSequence()
        self.assertEqual(test_main_sequence._get_text_style(), colorama.Fore.CYAN + colorama.Style.DIM)
        test_sequence = Sequence()
        self.assertEqual(test_sequence._get_text_style(), colorama.Fore.CYAN + colorama.Style.DIM)
        test_copy = Copy('', '')
        self.assertEqual(test_copy._get_text_style(), colorama.Fore.GREEN + colorama.Style.DIM)

    def test_basic_sequence_indentation_level(self):
        test_main_sequence = MainSequence()
        self.assertEqual(test_main_sequence._get_indentation(WorkflowTask.TextStyle.Text),  "     " * 1)
        self.assertEqual(test_main_sequence._get_indentation(WorkflowTask.TextStyle.Header),  "     " * 0)

    def test_basic_ifelse_indentation_level(self):
        test_if_else = IfElse(1 != 2)
        self.assertEqual(test_if_else._get_indentation(WorkflowTask.TextStyle.Text),  "     " * 2)
        self.assertEqual(test_if_else._get_indentation(WorkflowTask.TextStyle.Header),  "     " * 1)

        test_copy1 = Copy('', '')
        test_copy2 = Copy('', '')
        test_if_else.add_true_handler('true', test_copy1)
        test_if_else.add_false_handler('false', test_copy2)

        self.assertEqual(test_if_else._leftsteps._workflowsteps["true"]._get_indentation(WorkflowTask.TextStyle.Text), "     " * 4)
        self.assertEqual(test_if_else._leftsteps._workflowsteps["true"]._get_indentation(WorkflowTask.TextStyle.Header), "     " * 3)
        self.assertEqual(test_if_else._rightsteps._workflowsteps["false"]._get_indentation(WorkflowTask.TextStyle.Text), "     " * 4)
        self.assertEqual(test_if_else._rightsteps._workflowsteps["false"]._get_indentation(WorkflowTask.TextStyle.Header), "     " * 3)

        test_main_sequence = MainSequence()
        test_main_sequence.addstep('test_if_else', test_if_else)
        self.assertEqual(test_if_else._get_indentation(WorkflowTask.TextStyle.Text),  "     " * 2)
        self.assertEqual(test_if_else._get_indentation(WorkflowTask.TextStyle.Header),  "     " * 1)

        self.assertEqual(test_if_else._leftsteps._workflowsteps["true"]._get_indentation(WorkflowTask.TextStyle.Text), "     " * 4)
        self.assertEqual(test_if_else._leftsteps._workflowsteps["true"]._get_indentation(WorkflowTask.TextStyle.Header), "     " * 3)
        self.assertEqual(test_if_else._rightsteps._workflowsteps["false"]._get_indentation(WorkflowTask.TextStyle.Text), "     " * 4)
        self.assertEqual(test_if_else._rightsteps._workflowsteps["false"]._get_indentation(WorkflowTask.TextStyle.Header), "     " * 3)

        test_if_else_2 = IfElse(1 != 2)
        test_copy3 = Copy('', '')
        test_copy4 = Copy('', '')
        test_if_else_2.add_true_handler('true3', test_copy3)
        test_if_else_2.add_false_handler('false4', test_copy4)
        test_if_else.add_true_handler('test_if_else_2', test_if_else_2)
        self.assertEqual(test_if_else_2._get_indentation(WorkflowTask.TextStyle.Text),  "     " * 4)
        self.assertEqual(test_if_else_2._get_indentation(WorkflowTask.TextStyle.Header),  "     " * 3)
        self.assertEqual(test_if_else_2._leftsteps._workflowsteps['true3']._get_indentation(WorkflowTask.TextStyle.Text), "     " * 6)
        self.assertEqual(test_if_else_2._leftsteps._workflowsteps['true3']._get_indentation(WorkflowTask.TextStyle.Header), "     " * 5)
        self.assertEqual(test_if_else_2._rightsteps._workflowsteps['false4']._get_indentation(WorkflowTask.TextStyle.Text), "     " * 6)
        self.assertEqual(test_if_else_2._rightsteps._workflowsteps['false4']._get_indentation(WorkflowTask.TextStyle.Header), "     " * 5)

    def test_basic_devopstask_indentation_level(self):
        test_copy = Copy('', '')
        self.assertEqual(test_copy._get_indentation(WorkflowTask.TextStyle.Text),  "     " * 2)
        self.assertEqual(test_copy._get_indentation(WorkflowTask.TextStyle.Header),  "     " * 1)
        self.assertEqual(test_copy._get_indentation(WorkflowTask.TextStyle.Error),  "     " * 2)
        test_main_sequence = MainSequence()
        test_main_sequence.addstep('test_if_else', test_copy)
        self.assertEqual(test_copy._get_indentation(WorkflowTask.TextStyle.Text),  "     " * 2)
        self.assertEqual(test_copy._get_indentation(WorkflowTask.TextStyle.Error),  "     " * 2)
        self.assertEqual(test_copy._get_indentation(WorkflowTask.TextStyle.Header),  "     " * 1)

    def test_error_style(self):
        test_if = IfElse(1 != 2)
        self.assertEqual(test_if._get_error_style(), colorama.Back.RED + colorama.Fore.WHITE)

    #TODO: Allow setting on colorama values only if it has been initialized vs always just setting them
    def test_w_print(self):
        test_if = IfElse(1 != 2)
        sys.stdout = open("unit_test.txt", "w")
        test_if._w_print('testing123', WorkflowTask.TextStyle.Header)
        sys.stdout.close()
        with open("unit_test.txt", 'r') as test_print:
            self.assertEqual(test_print.read(), '%s%s     testing123\n' % (colorama.Fore.YELLOW, colorama.Style.DIM) )

    def test_devops_task_get_header_style(self):
        copy = Copy('','')
        self.assertEqual(copy._get_header_style(), colorama.Fore.WHITE + colorama.Style.DIM)

    def test_devops_task_get_footer_style(self):
        copy = Copy('','')
        self.assertEqual(copy._get_footer_style(), colorama.Fore.WHITE)

    def test_devops_task_get_text_style(self):
        copy = Copy('','')
        self.assertEqual(copy._get_text_style(), colorama.Fore.GREEN + colorama.Style.DIM)

    def test_control_flow_task_get_header_style(self):
        test_if = IfElse(1 != 2)
        self.assertEqual(test_if._get_header_style(), colorama.Fore.YELLOW + colorama.Style.DIM)

    def test_control_flow_task_get_footer_style(self):
        test_if = IfElse(1 != 2)
        self.assertEqual(test_if._get_footer_style(), colorama.Fore.YELLOW)

    def test_control_flow_task_get_text_style(self):
        test_if = IfElse(1 != 2)
        self.assertEqual(test_if._get_text_style(), colorama.Fore.YELLOW + colorama.Style.DIM)

    def test_main_sequence_prehook(self):
        test = MainSequence()
        sys.stdout = open("unit_test.txt", "w")
        test._prehook()
        sys.stdout.close()
        with open("unit_test.txt", 'r') as test_print:
            self.assertEqual(test_print.read(), '%s%sStarting ==> Primary Sequence\n%s%s     Input workflow variables: {}\n' % (colorama.Back.BLUE, colorama.Fore.CYAN, colorama.Fore.CYAN, colorama.Style.DIM) )

    def test_main_sequence_posthook(self):
        test = MainSequence()
        sys.stdout = open("unit_test.txt", "w")
        test._posthook()
        sys.stdout.close()
        with open("unit_test.txt", 'r') as test_print:
            self.assertEqual(test_print.read(), '%s%s     Exhaust workflow variables {}\n%s%sComplete ==> Primary Sequence\n' % (colorama.Fore.CYAN, colorama.Style.DIM, colorama.Back.BLUE, colorama.Fore.CYAN) )

    #TODO: Consider: set workflow name in __init__, not in add_step
    def test_control_flow_task_prehook(self):
        test = IfElse(1 != 2)
        sys.stdout = open("unit_test.txt", "w")
        test._prehook()
        sys.stdout.close()
        with open("unit_test.txt", 'r') as test_print:
            self.assertEqual(test_print.read(), '%s%s     Starting ==> \n%s%s          Input workflow variables: {}\n' % (colorama.Fore.YELLOW, colorama.Style.DIM, colorama.Fore.YELLOW, colorama.Style.DIM) )

    def test_control_flow_task_posthook(self):
        test = IfElse(1 != 2)
        sys.stdout = open("unit_test.txt", "w")
        test._posthook()
        sys.stdout.close()
        with open("unit_test.txt", 'r') as test_print:
            self.assertEqual(test_print.read(), '%s%s          Exhaust workflow variables {}\n%s     Complete ==> \n' % (colorama.Fore.YELLOW, colorama.Style.DIM, colorama.Fore.YELLOW) )

    def test_devops_task_prehook(self):
        test = Copy('', '')
        sys.stdout = open("unit_test.txt", "w")
        test._prehook()
        sys.stdout.close()
        with open("unit_test.txt", 'r') as test_print:
            self.assertEqual(test_print.read(), '%s%s     Starting ==> \n%s%s          Input workflow variables: {}\n' % (colorama.Fore.WHITE, colorama.Style.DIM, colorama.Fore.GREEN, colorama.Style.DIM) )

    def test_devops_task_posthook(self):
        test = Copy('', '')
        sys.stdout = open("unit_test.txt", "w")
        test._posthook()
        sys.stdout.close()
        with open("unit_test.txt", 'r') as test_print:
            self.assertEqual(test_print.read(), '%s%s          Exhaust workflow variables {}\n%s     Complete ==> \n' % (colorama.Fore.GREEN, colorama.Style.DIM, colorama.Fore.WHITE) )


if __name__ == '__main__':
    unittest.main()
