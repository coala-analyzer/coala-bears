import unittest

from bears.python.PycodestyleBear import PycodestyleBear
from coalib.testing.LocalBearTestHelper import verify_local_bear, execute_bear
from coalib.settings.Section import Section
from coala_utils.ContextManagers import prepare_file
from queue import Queue
from coalib.bearlib.aspects.Formatting import LineLength
from coalib.bearlib.aspects import (
    AspectList,
    get as get_aspect,
)


good_file = '''
def hello():
    print("hello world")
'''


bad_file = '''
import something



def hello():
    print("hello world")
'''

multiple_error_file = '''
y = 10;
print( 'hello' )
'''

file_with_very_long_line = ('def ' + 'h' * 1000 + '():\n' +
                            '    print("hello")')

PycodestyleBearTest = verify_local_bear(
    PycodestyleBear,
    valid_files=(good_file,),
    invalid_files=(bad_file,))

PycodestyleBearNoIgnoreTest = verify_local_bear(
    PycodestyleBear,
    valid_files=(good_file,),
    invalid_files=(bad_file,),
    settings={'pycodestyle_ignore': ''})

PycodestyleBearConfigIgnoreTest = verify_local_bear(
    PycodestyleBear,
    valid_files=(good_file, bad_file),
    invalid_files=[],
    settings={'pycodestyle_ignore': 'E303'})

PycodestyleBearConfigSelectTest = verify_local_bear(
    PycodestyleBear,
    valid_files=(good_file, bad_file),
    invalid_files=[],
    settings={'pycodestyle_select': 'E300'})

long_line = 'a = "{0}"'.format('a' * 100)

small_line = 'Small line.'

PycodestyleBearLineLengthTest = verify_local_bear(
    PycodestyleBear,
    valid_files=(),
    invalid_files=(long_line,)
)

PycodestyleBearLineLengthSettingTest = verify_local_bear(
    PycodestyleBear,
    valid_files=(long_line,),
    invalid_files=(),
    settings={'max_line_length': 200}
)

PycodestyleBearInfiniteLineLengthTest = verify_local_bear(
    PycodestyleBear,
    valid_files=(file_with_very_long_line,),
    invalid_files=(),
    settings={'max_line_length': 0})

PycodestyleBearAspectsTest = verify_local_bear(
    PycodestyleBear,
    valid_files=(small_line,),
    invalid_files=(long_line,),
    aspects=AspectList([
        get_aspect('LineLength')('Python', max_line_length=30),
    ]),
)

PycodestyleBearSettingsOverAspectsTest = verify_local_bear(
    PycodestyleBear,
    valid_files=(small_line,),
    invalid_files=(long_line,),
    aspects=AspectList([
        get_aspect('LineLength')('Python', max_line_length=2),
    ]),
    settings={'max_line_length': 30},
)


class PycodestyleBearTest(unittest.TestCase):

    def setUp(self):
        self.section = Section('')
        self.section.aspects = AspectList([
            get_aspect('LineLength')('Python', max_line_length=30),
        ])
        self.uut = PycodestyleBear(self.section, Queue())

    def test_line_length(self):
        content = long_line.splitlines()
        with prepare_file(content, None) as (file, fname):
            with execute_bear(self.uut, fname, file) as results:
                result = results[0]
                self.assertEqual(result.message,
                                 'E501 line too long (106 > 30 characters)')
                self.assertEqual(result.origin, 'PycodestyleBear (E501)')
                self.assertEqual(result.aspect, LineLength('py'))

    def test_multiple_errors(self):
        content = multiple_error_file.splitlines()
        with prepare_file(content, None) as (file, fname):
            with execute_bear(self.uut, fname, file) as results:
                self.assertTrue(len(results) == 3)
