from queue import Queue

from bears.js.JSONFormatBear import JSONFormatBear
from coalib.testing.LocalBearTestHelper import (verify_local_bear,
                                                LocalBearTestHelper)
from coalib.results.Result import Result
from coalib.results.Diff import Diff
from coalib.settings.Section import Section


test_file1 = """{
    "a": 5,
    "b": 5
}"""


test_file2 = """{
    "b": 5,
    "a": 5
}"""


test_file3 = """{
   "b": 5,
   "a": 5
}"""


unicode_file = """{
    "⌘": 5
}"""


test_file4 = """{
    a: 5
}"""


# This will generate a line with 80 characters
max_line_length_file1 = '{\n    "string": "' + 'a' * 64 + '"\n}'

# This will generate a line with 79 characters
max_line_length_file2 = '{\n    "string": "' + 'a' * 63 + '"\n}'

# This file is for checking the appropriate message displayed
# to the user based on the json_sort value
test_file5 = '{\n', '    "a":   5\n', '}\n'

correct_test_file5 = '{\n', '    "a": 5\n', '}\n'


class JSONTest(LocalBearTestHelper):

    def setUp(self):
        self.section = Section('')
        self.uut = JSONFormatBear(self.section, Queue())

    def test_exception_result(self):
        self.check_results(
            self.uut,
            test_file4.split('\n'),
            [Result.from_values('JSONFormatBear',
                                'This file does not contain parsable JSON. '
                                'Expecting property name enclosed in '
                                'double quotes.',
                                file='default',
                                line=2,
                                column=5)],
            filename='default')

    def test_exception_empty_file(self):
        self.check_results(
            self.uut,
            [],
            [Result.from_values('JSONFormatBear',
                                'This file is empty.',
                                file='default')],
            filename='default')

    def test_format_message_with_sort(self):
        diff = Diff.from_string_arrays(test_file5, correct_test_file5)
        self.check_results(
            self.uut,
            test_file5,
            [Result.from_values('JSONFormatBear',
                                'This file can be reformatted by sorting '
                                'keys and following indentation.',
                                file='default',
                                diffs={'default': diff},
                                line=2)],
            settings={'json_sort': True},
            filename='default')

    def test_format_message_without_sort(self):
        diff = Diff.from_string_arrays(test_file5, correct_test_file5)
        self.check_results(
            self.uut,
            test_file5,
            [Result.from_values('JSONFormatBear',
                                'This file can be reformatted '
                                'by following indentation.',
                                file='default',
                                diffs={'default': diff},
                                line=2)],
            settings={'json_sort': False},
            filename='default')


JSONFormatBearTest = verify_local_bear(JSONFormatBear,
                                       valid_files=(test_file1, test_file2),
                                       invalid_files=(test_file3,
                                                      unicode_file,
                                                      '',
                                                      'random stuff',
                                                      '{"a":5,"b":5}'))


JSONFormatBearSortTest = verify_local_bear(JSONFormatBear,
                                           valid_files=(test_file1,),
                                           invalid_files=(test_file2,),
                                           settings={'json_sort': 'true'})


JSONFormatBearTabWidthTest = verify_local_bear(JSONFormatBear,
                                               valid_files=(test_file3,),
                                               invalid_files=(test_file2,),
                                               settings={
                                                   'indent_size': '3'})


JSONFormatBearUnicodeTest = verify_local_bear(JSONFormatBear,
                                              valid_files=(unicode_file,),
                                              invalid_files=(),
                                              settings={'escape_unicode':
                                                        'false'})


JSONFormatBearInfLineLengthTest = verify_local_bear(JSONFormatBear,
                                                    valid_files=(
                                                        max_line_length_file1,
                                                        max_line_length_file2),
                                                    invalid_files=())


JSONFormatBearLineLengthTest = verify_local_bear(JSONFormatBear,
                                                 valid_files=(
                                                     max_line_length_file2,),
                                                 invalid_files=(
                                                     max_line_length_file1,),
                                                 settings={'max_line_length':
                                                           '79'})
