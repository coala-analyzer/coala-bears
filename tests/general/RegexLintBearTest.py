from os.path import abspath
from queue import Queue

from bears.general.AnnotationBear import AnnotationBear
from bears.general.RegexLintBear import RegexLintBear
from coalib.results.Result import Result
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting
from coalib.testing.LocalBearTestHelper import (
    LocalBearTestHelper, execute_bear)


good_py_file = """
some_regex = r'[a-zA-Z]'
"""

bad_py_file = """
some_regex = r'(else|elseif)'
"""

good_cpp_file = """
char some_regex[] = "[a-zA-Z]";
"""

bad_cpp_file = """
char some_regex[13] = "(else|elseif)";
"""

re_error_file = """
some_regex = r'*ab' # This should be skipped
some_other_regex = r'[a-z]'
"""

BAD_MESSAGE = """
E105:argv:root:0: Potential out of order alternation between 'else' and 'elseif'
  '(else|elseif)'
         ^ here
""".lstrip()


class RegexLintBearTest(LocalBearTestHelper):

    def setUp(self):
        self.section = Section('')
        self.uut = RegexLintBear(self.section, Queue())
        self.dep_uut = AnnotationBear(self.section, Queue())

    def test_good_python_file(self):
        valid_file = good_py_file.splitlines()
        self.section.append(Setting('language', 'python'))
        dep_results = {AnnotationBear.name:
                       list(self.dep_uut.execute('file', valid_file))}
        with execute_bear(self.uut, abspath('file'), valid_file,
                          dependency_results=dep_results) as results:
            self.assertEqual(len(results), 0)

    def test_bad_python_file(self):
        invalid_file = bad_py_file.splitlines()
        self.section.append(Setting('language', 'python'))
        dep_results = {AnnotationBear.name:
                       list(self.dep_uut.execute('file', invalid_file))}
        with execute_bear(self.uut, abspath('file'), invalid_file,
                          dependency_results=dep_results) as results:
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0],
                             Result.from_values(origin=self.uut,
                                                message=BAD_MESSAGE,
                                                file='file',
                                                line=2, column=15,
                                                end_line=2, end_column=29))

    def test_good_cpp_file(self):
        valid_file = good_cpp_file.splitlines()
        self.section.append(Setting('language', 'cpp'))
        dep_results = {AnnotationBear.name:
                       list(self.dep_uut.execute('file', valid_file))}
        with execute_bear(self.uut, abspath('file'), valid_file,
                          dependency_results=dep_results) as results:
            self.assertEqual(len(results), 0)

    def test_bad_cpp_file(self):
        invalid_file = bad_cpp_file.splitlines()
        self.section.append(Setting('language', 'cpp'))
        dep_results = {AnnotationBear.name:
                       list(self.dep_uut.execute('file', invalid_file))}
        with execute_bear(self.uut, abspath('file'), invalid_file,
                          dependency_results=dep_results) as results:
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0],
                             Result.from_values(origin=self.uut,
                                                message=BAD_MESSAGE,
                                                file='file',
                                                line=2, column=23,
                                                end_line=2, end_column=37))

    def test_re_error_file(self):
        valid_file = re_error_file.splitlines()
        self.section.append(Setting('language', 'python'))
        dep_results = {AnnotationBear.name:
                       list(self.dep_uut.execute('file', valid_file))}
        with execute_bear(self.uut, abspath('file'), valid_file,
                          dependency_results=dep_results) as results:
            self.assertEqual(len(results), 0)
