from collections import namedtuple
from queue import Queue
import unittest
import logging

from bears.general.KeywordBear import KeywordBear
from coalib.results.HiddenResult import HiddenResult
from coalib.results.SourceRange import SourceRange
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting
from coalib.testing.LocalBearTestHelper import verify_local_bear, execute_bear

test_file = """
test line fix me
to do
error fixme
"""


KeywordBearTest = verify_local_bear(
    KeywordBear,
    valid_files=(test_file,),
    invalid_files=('test line todo',
                   'test line warNING'),
    settings={'keywords': 'todo, warning',
              'language': 'c'})
# Language setting is used to generate the diff correctly and doesn't influence
# where the keyword may appear.


class KeywordBearDiffTest(unittest.TestCase):

    def setUp(self):
        self.section = Section('')
        self.section.append(Setting('language', 'python3'))
        self.section.append(Setting('keywords', 'TODO'))
        self.uut = KeywordBear(self.section, Queue())

        self.annotation_bear_result_type = namedtuple('result', ['contents'])
        self.dep_results = {'AnnotationBear': HiddenResult(
            'AnnotationBear', {'comments': ()})}

    def test_empty_keyword(self):
        text = ['a == b']

        with execute_bear(self.uut, filename='F', file=text,
                          dependency_results=self.dep_results) as result:
            self.assertEqual(result, [])

    def test_keyword_in_comment(self):
        dep_results = {
            'AnnotationBear': {}
        }
        text = ['# todo 123']
        with execute_bear(self.uut, filename='F', file=text,
                          dependency_results=dep_results) as result:
            self.assertEqual(result[0].diffs, {})
            self.assertEqual(result[0].affected_code[0].start.line, 1)
            self.assertEqual(len(result), 1)

        dep_results = {'AnnotationBear': HiddenResult(
            'AnnotationBear', {'comments': 123})}
        with execute_bear(self.uut, filename='F', file=text,
                          dependency_results=dep_results) as result:
            self.assertEqual(result[0].diffs, {})
            self.assertEqual(result[0].affected_code[0].start.line, 1)
            self.assertEqual(len(result), 1)

        dep_results = {'AnnotationBear': HiddenResult(
            'AnnotationBear', 123)}
        with execute_bear(self.uut, filename='F', file=text,
                          dependency_results=dep_results) as result:
            self.assertEqual(result[0].diffs, {})
            self.assertEqual(result[0].affected_code[0].start.line, 1)
            self.assertEqual(len(result), 1)

    def test_keyword_not_in_comment(self):
        text = ['# comment 123\n', 'a = "TODO"\n']
        comments = [SourceRange.from_values('F', 1, 1, 1, 40)]
        dep_results = {
            'AnnotationBear': [
                self.annotation_bear_result_type({'comments': comments})
            ]
        }

        with execute_bear(self.uut, filename='F', file=text,
                          dependency_results=dep_results) as result:
            self.assertEqual(len(result[0].diffs), 0)

    def test_keyword_diff(self):
        text = ['# todo 123\n']
        comments = [SourceRange.from_values('F', 1, 1, 1, 10)]
        dep_results = {
            'AnnotationBear': [
                self.annotation_bear_result_type({'comments': comments})
            ]
        }

        with execute_bear(self.uut, filename='F', file=text,
                          dependency_results=dep_results) as result:
            self.assertEqual(result[0].diffs['F'].unified_diff,
                             '--- \n'
                             '+++ \n'
                             '@@ -1 +0,0 @@\n'
                             '-# todo 123\n')

        text = ['test = 55 # todo 123\n']
        comments = [SourceRange.from_values('F', 1, 11, 1, 23)]
        dep_results = {
            'AnnotationBear': [
                self.annotation_bear_result_type({'comments': comments})
            ]
        }
        with execute_bear(self.uut, filename='F', file=text,
                          dependency_results=dep_results) as result:
            self.assertEqual(result[0].diffs['F'].unified_diff,
                             '--- \n'
                             '+++ \n'
                             '@@ -1 +1 @@\n'
                             '-test = 55 # todo 123\n'
                             '+test = 55\n')

    def test_keyword_outside_of_comment(self):
        text = ['todo = 123\n']
        with execute_bear(self.uut, filename='F', file=text,
                          dependency_results=self.dep_results) as result:
            self.assertEqual(result[0].diffs, {})

    def test_keyword_between_code(self):
        self.section.append(Setting('language', 'c'))
        self.section.append(Setting('keywords', 'todo'))

        text = ['int a=0; /* TODO: Test */ int b=1;\n']

        comments = [SourceRange.from_values('F', 1, 10, 1, 25)]
        dep_results = {
            'AnnotationBear': [
                self.annotation_bear_result_type({'comments': comments})
            ]
        }

        with execute_bear(self.uut, filename='F', file=text,
                          dependency_results=dep_results) as result:
            self.assertEqual(result[0].diffs['F'].unified_diff,
                             '--- \n'
                             '+++ \n'
                             '@@ -1 +1 @@\n'
                             '-int a=0; /* TODO: Test */ int b=1;\n'
                             '+int a=0; int b=1;\n')

        text = ['int a = 0; /* TODO test\n',
                'another test\n',
                '*/\n']
        comments = [SourceRange.from_values('F', 1, 12, 3, 2)]
        dep_results = {
            'AnnotationBear': [
                self.annotation_bear_result_type({'comments': comments})
            ]
        }

        with execute_bear(self.uut, filename='F', file=text,
                          dependency_results=dep_results) as result:
            self.assertEqual(result[0].diffs['F'].unified_diff,
                             '--- \n'
                             '+++ \n'
                             '@@ -1,3 +1,3 @@\n'
                             '-int a = 0; /* TODO test\n'
                             '+int a = 0; /*\n'
                             ' another test\n'
                             ' */\n')

        text = ['/* TODO\n',
                'test\n',
                '*/\n']
        comments = [SourceRange.from_values('F', 1, 1, 3, 2)]
        dep_results = {
            'AnnotationBear': [
                self.annotation_bear_result_type({'comments': comments})
            ]
        }

        with execute_bear(self.uut, filename='F', file=text,
                          dependency_results=dep_results) as result:
            self.assertEqual(result[0].diffs['F'].unified_diff,
                             '--- \n'
                             '+++ \n'
                             '@@ -1,3 +1,3 @@\n'
                             '-/* TODO\n'
                             '+/*\n'
                             ' test\n'
                             ' */\n')

    def test_keyword_regex(self):
        text = ['# add two given values and result the result\n',
                'def add(a, b):',
                '    return a+b\n',
                '               \n',
                'print(add(2, 3))\n']

        regex_keyword = 'r.s.l.'

        with execute_bear(self.uut, filename='F', file=text,
                          regex_keyword=regex_keyword,
                          dependency_results=self.dep_results) as result:
            self.assertEqual(result[0].message, 'The line contains the keyword'
                                                " 'result' which resulted in a"
                                                ' match with given regex.')

        text = ['# bla bla bla',
                'Issue #123',
                'bla bla bla']

        regex_keyword = '[iI]ssue #[1-9][0-9]*'

        with execute_bear(self.uut, filename='F', file=text,
                          regex_keyword=regex_keyword,
                          dependency_results=self.dep_results) as result:
            self.assertEqual(result[0].message, 'The line contains the keyword'
                                                " 'Issue #123' which resulted "
                                                'in a match with given regex.')

    def test_wrong_language(self):
        self.section.append(Setting('language', 'anything'))
        logger = logging.getLogger()
        annotation_bear_result_type = namedtuple('result', 'contents')
        dep_results = {
            'AnnotationBear': [
                annotation_bear_result_type(
                  'coalang specification for anything not found.')
            ]
        }

        text = ['# todo 123']

        with self.assertLogs(logger, 'ERROR') as log:
            with execute_bear(self.uut, filename='F', file=text,
                              dependency_results=dep_results) as result:
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].diffs, {})
                self.assertEqual(result[0].affected_code[0].start.line, 1)
                self.assertEqual(len(log.output), 1)
                self.assertIn(log.output[0],
                              'ERROR:root:coalang specification'
                              ' for anything not found.')

    def test_empty_keywords_list(self):
        self.section.append(Setting('keywords', ''))

        text = ['bears = KeywordBear\n']

        with execute_bear(self.uut, filename='F', file=text,
                          dependency_results=self.dep_results) as result:
            self.assertEqual(len(result), 0)

    def test_multiple_patches(self):
        self.section.append(Setting('language', 'c'))
        self.section.append(Setting('keywords', 'warning'))

        text = ["//warning Don't use foo/bar in every example\n",
                "int warning = 0; //Now I won't give warning\n",
                '//Hacked, sorry that was your last warning']

        comments = [SourceRange.from_values('F', 1, 1, 1, 44),
                    SourceRange.from_values('F', 2, 18, 2, 47),
                    SourceRange.from_values('F', 3, 1, 3, 42)]

        dep_results = {
            'AnnotationBear': [
                self.annotation_bear_result_type({'comments': comments})
            ]
        }

        with execute_bear(self.uut, filename='F', file=text,
                          dependency_results=dep_results) as result:
            self.assertEqual(len(result), 4)
            self.assertEqual(result[0].diffs['F'].unified_diff,
                             '--- \n'
                             '+++ \n'
                             '@@ -1,3 +1,2 @@\n'
                             "-//warning Don't use foo/bar in every example\n"
                             " int warning = 0; //Now I won't give warning\n"
                             ' //Hacked, sorry that was your last warning')
            self.assertEqual(result[1].diffs, {})
            self.assertEqual(result[2].diffs['F'].unified_diff,
                             '--- \n'
                             '+++ \n'
                             '@@ -1,3 +1,3 @@\n'
                             " //warning Don't use foo/bar in every example\n"
                             "-int warning = 0; //Now I won't give warning\n"
                             '+int warning = 0;\n'
                             ' //Hacked, sorry that was your last warning')
            self.assertEqual(result[3].diffs['F'].unified_diff,
                             '--- \n'
                             '+++ \n'
                             '@@ -1,3 +1,2 @@\n'
                             " //warning Don't use foo/bar in every example\n"
                             " int warning = 0; //Now I won't give warning\n"
                             '-//Hacked, sorry that was your last warning')
