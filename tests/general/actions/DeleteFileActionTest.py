import os
import unittest
from unittest.mock import patch
from coalib.results.Result import Result
from bears.general.actions.DeleteFileAction import DeleteFileAction
from coala_utils.ContextManagers import retrieve_stdout


def get_path(file):
    return os.path.join(
        os.getcwd(), 'tests', 'general', 'duplicate_test_files', file)


class DeleteFileActionTest(unittest.TestCase):

    def setUp(self):
        self.file1 = 'complexFirst.txt'
        self.file2 = 'complexSecond.txt'
        self.result = Result('origin', 'message')
        self.uut1 = DeleteFileAction(self.file1)
        self.uut2 = DeleteFileAction(self.file2)

    def test_is_applicable(self):
        self.assertTrue(self.uut1.is_applicable(self.result, {}, {}))
        self.assertFalse(self.uut1.is_applicable(
            self.result, {}, {}, applied_actions=('DeleteFileAction')))

    def test_apply(self):
        with retrieve_stdout() as stdout:
            patcher = ('bears.general.actions.DeleteFileAction.'
                       'os.remove')
            with patch(patcher):
                ret = self.uut1.apply(self.result, {}, {'file': 'diff'})
                self.assertEqual(ret, {'file': 'diff'})
                self.assertEqual(stdout.getvalue(), '')
