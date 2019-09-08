import os
import unittest

from queue import Queue

from bears.python.requirements.RequirementsCheckBear import (
    RequirementsCheckBear)
from coalib.results.Result import Result, RESULT_SEVERITY
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting


def get_absolute_test_path(file):
    return os.path.join(os.path.dirname(__file__),
                        'requirements_test_files', file)


def read_file(file):
    with open(file) as _file:
        return _file.read()


class RequirementsCheckBearTest(unittest.TestCase):

    def setUp(self):
        self.section = Section('')
        self.file_dict = {}
        self.queue = Queue()
        self.test_files = [get_absolute_test_path('conflict.txt'),
                           get_absolute_test_path('valid.txt')]
        self.files = [read_file(_file) for _file in self.test_files]

    def test_conflicted_file(self):
        self.section.append(Setting('require_files', self.test_files[0]))
        self.uut = RequirementsCheckBear({}, self.section, self.queue)
        result = list(self.uut.run_bear_from_section([], {}))
        self.assertEqual(result[0],
                         Result(origin='RequirementsCheckBear',
                                message=('Could not find a version that '
                                         'matches six<=1.11.0,==1.12.0'),
                                severity=RESULT_SEVERITY.MAJOR))
        self.assertEqual(read_file(self.test_files[0]), self.files[0])

    def test_valid_file(self):
        self.section.append(Setting('require_files', self.test_files[1]))
        self.uut = RequirementsCheckBear({}, self.section, self.queue)
        result = list(self.uut.run_bear_from_section([], {}))
        self.assertEqual(result, [])
        self.assertEqual(read_file(self.test_files[1]), self.files[1])

    def test_multiple_require_files(self):
        self.section.append(Setting('require_files',
                                    ','.join(file for file in self.test_files)))
        self.uut = RequirementsCheckBear({}, self.section, self.queue)
        result = list(self.uut.run_bear_from_section([], {}))
        self.assertEqual(result[0],
                         Result(origin='RequirementsCheckBear',
                                message=('Could not find a version that '
                                         'matches six<=1.11.0,==1.12.0'),
                                severity=RESULT_SEVERITY.MAJOR))
        self.assertEqual(read_file(self.test_files[0]), self.files[0])
        self.assertEqual(read_file(self.test_files[1]), self.files[1])

    def test_no_existing_file(self):
        invalid_test_file_path = get_absolute_test_path('invalid.txt')
        self.section.append(Setting('require_files', invalid_test_file_path))
        self.uut = RequirementsCheckBear({}, self.section, self.queue)
        error = ('The file \'{}\' doesn\'t exist.'
                 .format(invalid_test_file_path))
        with self.assertRaisesRegex(ValueError, error):
            list(self.uut.run_bear_from_section([], {}))
