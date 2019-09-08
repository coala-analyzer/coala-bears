import logging
from queue import Queue

from bears.general.LineContinuationBear import LineContinuationBear
from coalib.testing.LocalBearTestHelper import LocalBearTestHelper
from coalib.testing.LocalBearTestHelper import execute_bear
from coalib.results.Result import Result
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting


good_file = """
a = some_function(
    '1' + '2')

def fun():
    '''
        >>> from math \\
        ...     import pow
    '''
"""


class LineContinuationBearTest(LocalBearTestHelper):

    def setUp(self):
        self.section = Section('name')
        self.uut = LineContinuationBear(self.section, Queue())

    def test_good_file(self):
        self.section.append(Setting('language', 'Python'))
        self.check_validity(self.uut, good_file.splitlines())

    def test_bad_file(self):
        self.section.append(Setting('language', 'Python'))
        self.check_results(
            self.uut, ['a = 1 + \\', '2'],
            [Result.from_values('LineContinuationBear',
                                'Explicit line continuation is not allowed.',
                                line=1, column=9, end_line=1, end_column=10,
                                file='default')],
            filename='default')
        self.check_results(
            self.uut, ["with open ('hey.txt') as \\",
                       'heyfile'],
            [Result.from_values('LineContinuationBear',
                                'Explicit line continuation is not allowed.',
                                line=1, column=26, end_line=1, end_column=27,
                                file='default')],
            filename='default')

    def test_data_ignore_with(self):
        self.section.append(Setting('language', 'Python'))
        self.section.append(Setting('ignore_with', 'true'))
        self.check_results(
            self.uut, ['a = 1 + \\', '2'],
            [Result.from_values('LineContinuationBear',
                                'Explicit line continuation is not allowed.',
                                line=1, column=9, end_line=1, end_column=10,
                                file='default')],
            filename='default')
        self.check_validity(
            self.uut, ["with open('hey.txt') as \\",
                       'heyfile'])

    def test_lang_exception(self):
        self.section.append(Setting('language', 'BlaBlaBla'))
        ERROR_MESSAGE = 'ERROR:root:Language BlaBlaBla is not yet supported.'
        logger = logging.getLogger()

        with self.assertLogs(logger, 'ERROR') as log:
            with execute_bear(self.uut, filename='F', file='') as result:
                self.assertEqual(len(log.output), 1)
                self.assertEqual(log.output[0], ERROR_MESSAGE)
