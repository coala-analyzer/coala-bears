import os
from queue import Queue

from bears.general.TextLintBear import TextLintBear
from coalib.results.Result import Result
from coalib.results.RESULT_SEVERITY import RESULT_SEVERITY
from coalib.settings.Section import Section
from coalib.testing.BearTestHelper import generate_skip_decorator
from coalib.testing.LocalBearTestHelper import LocalBearTestHelper


def get_testfile_path(name):
    return os.path.join(os.path.dirname(__file__),
                        'textlint_test_files',
                        name)


def load_testfile(name):
    with open(get_testfile_path(name)) as fl:
        return fl.readlines()


@generate_skip_decorator(TextLintBear)
class TextLintBearTest(LocalBearTestHelper):

    def setUp(self):
        self.uut = TextLintBear(Section('name'), Queue())

    def test_bad_ginger(self):
        file_name = 'bad_ginger.rst'
        file_contents = load_testfile(file_name)
        self.check_results(
            self.uut,
            file_contents,
            [Result.from_values('TextLintBear',
                                message='mistaek -> mistake',
                                line=1,
                                column=20,
                                severity=RESULT_SEVERITY.MAJOR,
                                file=get_testfile_path(file_name))],
            filename=get_testfile_path(file_name))

    def test_bad_no_start_duplicated_conjunction(self):
        file_name = 'bad_no_start_duplicated_conjunction.txt'
        file_contents = load_testfile(file_name)
        self.check_results(
            self.uut,
            file_contents,
            [Result.from_values('TextLintBear',
                                message='Don\'t repeat "But" in 2 phrases',
                                line=2,
                                column=1,
                                severity=RESULT_SEVERITY.MAJOR,
                                file=get_testfile_path(file_name))],
            filename=get_testfile_path(file_name))

    def test_bad_no_empty_section(self):
        file_name = 'bad_no_empty_section.md'
        file_contents = load_testfile(file_name)
        self.check_results(
            self.uut,
            file_contents,
            [Result.from_values('TextLintBear',
                                message='Found empty section: `# Header B`',
                                line=5,
                                column=1,
                                severity=RESULT_SEVERITY.MAJOR,
                                file=get_testfile_path(file_name))],
            filename=get_testfile_path(file_name))

    def test_bad_date_weekday_mismatch(self):
        file_name = 'bad_date_weekday_mismatch.txt'
        file_contents = load_testfile(file_name)
        self.check_results(
            self.uut,
            file_contents,
            [Result.from_values('TextLintBear',
                                message='2016-12-29 (Friday) '
                                        'mismatch weekday.',
                                line=1,
                                column=13,
                                severity=RESULT_SEVERITY.MAJOR,
                                file=get_testfile_path(file_name))],
            filename=get_testfile_path(file_name))

    def test_bad_max_comma(self):
        file_name = 'bad_max_comma.re'
        file_contents = load_testfile(file_name)
        self.check_results(
            self.uut,
            file_contents,
            [Result.from_values('TextLintBear',
                                message='This sentence exceeds the maximum '
                                        'count of comma. Maximum is 4',
                                line=1,
                                column=1,
                                severity=RESULT_SEVERITY.MAJOR,
                                file=get_testfile_path(file_name))],
            filename=get_testfile_path(file_name))

    def test_bad_unexpanded_acronym(self):
        file_name = 'bad_ng_word_unexpanded_acronym.md'
        file_contents = load_testfile(file_name)
        self.check_results(
            self.uut,
            file_contents,
            [Result.from_values('TextLintBear',
                                message='"PSF" is unexpanded acronym. What '
                                        'does "PSF" stand for?',
                                line=1,
                                column=1,
                                severity=RESULT_SEVERITY.MAJOR,
                                file=get_testfile_path(file_name))],
            filename=get_testfile_path(file_name))

    def test_bad_write_good_common_misspellings(self):
        file_name = 'bad_write_good_common_misspellings.html'
        file_contents = load_testfile(file_name)
        self.check_results(
            self.uut,
            file_contents,
            [Result.from_values('TextLintBear',
                                message='This is a commonly misspelled word. '
                                        'Correct it to abbreviate',
                                line=8,
                                column=1,
                                severity=RESULT_SEVERITY.MAJOR,
                                file=get_testfile_path(file_name)),
             Result.from_values('TextLintBear',
                                message='"So" adds no meaning',
                                line=9,
                                column=1,
                                severity=RESULT_SEVERITY.MAJOR,
                                file=get_testfile_path(file_name))],
            filename=get_testfile_path(file_name))

    def test_bad_alex_no_dead_link(self):
        file_name = 'bad_alex_no_dead_link.md'
        file_contents = load_testfile(file_name)
        self.check_results(
            self.uut,
            file_contents,
            [
             Result.from_values('TextLintBear',
                                message='https://google.com/teapot is dead. '
                                        '(301 Moved Permanently)',
                                line=2,
                                column=5,
                                severity=RESULT_SEVERITY.MAJOR,
                                file=get_testfile_path(file_name))],
            filename=get_testfile_path(file_name))

    def test_bad_ng_words_acronym_list_item(self):
        file_name = 'bad_ng_words_acronym_list_item.md'
        file_contents = load_testfile(file_name)
        self.check_results(
            self.uut,
            file_contents,
            [Result.from_values('TextLintBear',
                                message='Document contains NG word "shit"',
                                line=1,
                                column=1,
                                severity=RESULT_SEVERITY.MAJOR,
                                file=get_testfile_path(file_name)),
             Result.from_values('TextLintBear',
                                message='"PSF" is unexpanded acronym. '
                                        'What does "PSF" stand for?',
                                line=1,
                                column=1,
                                severity=RESULT_SEVERITY.MAJOR,
                                file=get_testfile_path(file_name))],
            filename=get_testfile_path(file_name),
            settings={'textlint_config': get_testfile_path('.textlintrc')})

    def test_good_file(self):
        file_contents = load_testfile('good_file.md')
        self.check_results(
            self.uut,
            file_contents,
            [],
            filename=get_testfile_path('good_file.md'))
