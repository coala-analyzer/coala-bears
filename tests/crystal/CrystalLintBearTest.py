import os
from queue import Queue

from coalib.results.Result import Result
from coalib.settings.Section import Section
from coalib.testing.BearTestHelper import generate_skip_decorator
from coalib.testing.LocalBearTestHelper import LocalBearTestHelper

from bears.crystal.CrystalLintBear import CrystalLintBear


def get_testfile_path(name):
    return os.path.join(os.path.dirname(__file__),
                        'ameba_test_files',
                        name)


def load_testfile(name):
    with open(get_testfile_path(name)) as f:
        return f.readlines()


@generate_skip_decorator(CrystalLintBear)
class CrystalLintBearTest(LocalBearTestHelper):

    def setUp(self):
        self.section = Section('name')
        self.uut = CrystalLintBear(self.section, Queue())

    def test_redundant_begin_blank_line(self):
        filename = 'redundant_begin_test.cr'
        file_contents = load_testfile(filename)
        self.check_results(
            self.uut,
            file_contents,
            [Result.from_values('CrystalLintBear (RedundantBegin)',
                                message='Redundant `begin` block detected',
                                file=get_testfile_path(filename),
                                line=2,
                                column=3),
             Result.from_values('CrystalLintBear (TrailingBlankLines)',
                                message='Blank lines detected at the end of '
                                        'the file',
                                file=get_testfile_path(filename),
                                line=13,
                                column=1)],
            filename=get_testfile_path(filename))

    def test_underscore_cased(self):
        filename = 'underscore_cased_test.cr'
        file_contents = load_testfile(filename)
        self.check_results(
            self.uut,
            file_contents,
            [Result.from_values('CrystalLintBear (MethodNames)',
                                message='Method name should be underscore-'
                                        'cased: first_name, not first_Name',
                                file=get_testfile_path(filename),
                                line=1,
                                column=1)],
            filename=get_testfile_path(filename))

    def test_syntax(self):
        filename = 'syntax_test.cr'
        file_contents = load_testfile(filename)
        self.check_results(
            self.uut,
            file_contents,
            [Result.from_values('CrystalLintBear (Syntax)',
                                message="expecting token 'CONST', not "
                                        "'tagDirective'",
                                file=get_testfile_path(filename),
                                line=1,
                                column=8)],
            filename=get_testfile_path(filename))
