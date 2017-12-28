import unittest
from queue import Queue
from textwrap import dedent

from coalib.results.HiddenResult import HiddenResult, Result
from bears.general.AnnotationBear import AnnotationContent, AnnotationRange
from bears.general.QuotesBear import QuotesBear
from coalib.results.SourceRange import SourceRange
from coalib.settings.Section import Section
from bears.general.AnnotationBear import AnnotationBear
from coalib.testing.LocalBearTestHelper import execute_bear


class QuotesBearDiffTest(unittest.TestCase):

    def setUp(self):
        self.section = Section('')
        self.uut = QuotesBear(self.section, Queue())

        self.double_quote_file = dedent("""
        '''
        Multiline string
        '''
        "a string with double quotes!"
        'A single quoted string with " in it'
        """).splitlines(True)

        self.single_quote_file = dedent("""
        '''
        Multiline string
        '''
        'a string with single quotes!'
        "A double quoted string with ' in it"
        """).splitlines(True)

        self.filename = 'f'
        ranges = []
        ranges.append(
            AnnotationRange(
                'multiline_string', [[], [], [], SourceRange.from_values(
                    self.filename, 2, 1, 4, 3)]))
        ranges.append(AnnotationRange('singleline_string', [
                      [], [], [], SourceRange.from_values(
                        self.filename, 5, 1, 5, 30)]))
        ranges.append(AnnotationRange('singleline_string', [
                      [], [], [], SourceRange.from_values(
                        self.filename, 6, 1, 6, 37)]))
        self.dep_results = {
            AnnotationBear.name:
                HiddenResult(
                    'AnnotationBear',
                    AnnotationContent(ranges)
                )
        }

    def test_error_handling(self):
        dep_results = {AnnotationBear.name: Result('test', 'test')}
        with execute_bear(self.uut, self.filename, self.double_quote_file,
                          dependency_results=dep_results) as results:
            self.assertEqual(len(results), 0)

        dep_results = {AnnotationBear.name: HiddenResult('a', 'error!')}
        with execute_bear(self.uut, self.filename, self.double_quote_file,
                          dependency_results=dep_results) as results:
            self.assertEqual(len(results), 0)

    def test_valid_quotes(self):
        with execute_bear(self.uut, self.filename, self.double_quote_file,
                          dependency_results=self.dep_results) as results:
            self.assertEqual(len(results), 0)

        self.section['preferred_quotation'] = "'"
        with execute_bear(self.uut, self.filename, self.single_quote_file,
                          dependency_results=self.dep_results) as results:
            self.assertEqual(len(results), 0)

    def test_invalid_quotes(self):
        with execute_bear(self.uut, self.filename, self.single_quote_file,
                          dependency_results=self.dep_results) as results:
            res_list = list(results)
            self.assertEqual(len(res_list), 1)
            self.assertEqual(res_list[0].diffs[self.filename].unified_diff,
                             '--- \n'
                             '+++ \n'
                             '@@ -2,5 +2,5 @@\n'
                             " '''\n"
                             ' Multiline string\n'
                             " '''\n"
                             "-'a string with single quotes!'\n"
                             '+"a string with single quotes!"\n'
                             ' "A double quoted string with \' in it"\n')

        self.section['preferred_quotation'] = "'"
        with execute_bear(self.uut, self.filename, self.double_quote_file,
                          dependency_results=self.dep_results) as results:
            res_list = list(results)
            self.assertEqual(len(res_list), 1)
            self.assertEqual(res_list[0].diffs[self.filename].unified_diff,
                             '--- \n'
                             '+++ \n'
                             '@@ -2,5 +2,5 @@\n'
                             " '''\n"
                             ' Multiline string\n'
                             " '''\n"
                             '-"a string with double quotes!"\n'
                             "+'a string with double quotes!'\n"
                             " 'A single quoted string with \" in it'\n")
