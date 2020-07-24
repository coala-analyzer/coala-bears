import os
from queue import Queue

from bears.general.ShebangBear import ShebangBear
from coalib.settings.Section import Section
from coalib.testing.LocalBearTestHelper import LocalBearTestHelper
from coalib.results.Result import RESULT_SEVERITY, Result


def get_testfile_path(name):
    return os.path.join(os.path.dirname(__file__),
                        'shebang_test_files',
                        name)


def load_testfile(name):
    with open(get_testfile_path(name)) as f:
        file_lines = f.readlines()
    return file_lines


class ShebangBearTest(LocalBearTestHelper):

    def setUp(self):
        self.section = Section('')
        self.uut = ShebangBear(self.section, Queue())

    def test_basic_usage(self):
        self.check_validity(self.uut,
                            ['#!/usr/bin/env python \n print hello world'])
        self.check_validity(self.uut,
                            [''])
        self.check_invalidity(self.uut,
                              ['#!/usr/bin/python \n print hello world'])

    def test_invalid_file(self):
        file_name = 'invalidFile.py'
        file_contents = load_testfile(file_name)
        correct_operator = '#!/usr/bin/env python'
        message_desc = ('This eliminates the limitations caused by systems'
                        ' that have non-standard file system layout')
        self.check_results(
            self.uut,
            file_contents,
            [Result.from_values('ShebangBear',
                                message='Use the {}.\n{}.'.format(
                                    repr(correct_operator),
                                    message_desc),
                                line=1,
                                severity=RESULT_SEVERITY.NORMAL,
                                file=get_testfile_path(file_name))],
            filename=get_testfile_path(file_name))

    def test_valid_file(self):
        file_name = 'validFile.py'
        file_contents = load_testfile(file_name)
        self.check_results(
            self.uut,
            file_contents,
            [],
            filename=get_testfile_path(file_name))
