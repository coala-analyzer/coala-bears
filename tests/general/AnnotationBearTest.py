from queue import Queue
import unittest

from bears.general.AnnotationBear import AnnotationBear, AnnotationResult
from coalib.results.SourceRange import SourceRange
from coalib.results.AbsolutePosition import AbsolutePosition
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting
from coalib.testing.LocalBearTestHelper import execute_bear


class AnnotationBearTest(unittest.TestCase):

    def setUp(self):
        self.section1 = Section('')
        self.section1.append(Setting('language', 'python 3'))
        self.python_uut = AnnotationBear(self.section1, Queue())
        self.section2 = Section('')
        self.section2.append(Setting('language', 'c'))
        self.c_uut = AnnotationBear(self.section2, Queue())

    def test_single_line_string(self):
        text = ["'from start till the end with #comments'\n", ]
        compare = (SourceRange.from_absolute_position(
                                    'F',
                                    AbsolutePosition(text, 0),
                                    AbsolutePosition(text, len(text[0]) - 2)),)
        with execute_bear(self.python_uut, 'F', text) as result:
            self.assertEqual(result[0].contents['strings'], compare)
            self.assertEqual(result[0].contents['comments'], ())

        text = ["a'\n", "b'\n"]
        with execute_bear(self.python_uut, 'F', text) as result:
            self.assertEqual(result[0].message, "' has no closure")

    def test_multiline_string(self):
        text = ["'''multiline string, #comment within it'''\n"]
        compare = (SourceRange.from_absolute_position(
                        'F',
                        AbsolutePosition(text, 0),
                        AbsolutePosition(text, len(text[0])-2)),)
        with execute_bear(self.python_uut, 'F', text) as result:
            self.assertEqual(result[0].contents['strings'], compare)
            self.assertEqual(result[0].contents['comments'], ())

    def test_single_line_comment(self):
        text = ["some #coment with 'string'\n", 'and next line']
        compare = (SourceRange.from_absolute_position(
                                    'F',
                                    AbsolutePosition(text, text[0].find('#')),
                                    AbsolutePosition(text, len(text[0]) - 1)),)
        with execute_bear(self.python_uut, 'F', text) as result:
            self.assertEqual(result[0].contents['strings'], ())
            self.assertEqual(result[0].contents['comments'], compare)

    def test_multiline_comment(self):
        text = ['some string /*within \n', "'multiline comment'*/"]
        compare = (SourceRange.from_absolute_position(
                            'F',
                            AbsolutePosition(text, text[0].find('/*')),
                            AbsolutePosition(text, len(''.join(text)) - 1)),)
        with execute_bear(self.c_uut, 'F', text) as result:
            self.assertEqual(result[0].contents['strings'], ())
            self.assertEqual(result[0].contents['comments'], compare)

        text = ['/*Multiline which does not end']
        with execute_bear(self.c_uut, 'F', text) as result:
            self.assertEqual(result[0].message, '/* has no closure')

    def test_string_with_comments(self):
        text = ['some #comment\n', "with 'string' in  next line"]
        comment_start = text[0].find('#')
        comment_end = len(text[0]) - 1
        string_start = ''.join(text).find("'")
        string_end = ''.join(text).find("'", string_start + 1)
        compare = [(SourceRange.from_absolute_position(
                                'F',
                                AbsolutePosition(text, string_start),
                                AbsolutePosition(text, string_end)),),
                   (SourceRange.from_absolute_position(
                                'F',
                                AbsolutePosition(text, comment_start),
                                AbsolutePosition(text, comment_end)),)]
        with execute_bear(self.python_uut, 'F', text) as result:
            self.assertEqual(result[0].contents['strings'], compare[0])
            self.assertEqual(result[0].contents['comments'], compare[1])

    def test_combined_strings(self):
        file_text = ['"some string #with comment"\n',
                     '"""\n',
                     "now a multiline string ''' <- this one not\n",
                     '"""\n',
                     '"""\n'
                     'another comment # rather harmless\n',
                     '"""\n']
        string1_start = 0
        string1_end = len(file_text[0]) - 2
        string1 = SourceRange.from_absolute_position(
                                    'F',
                                    AbsolutePosition(file_text, string1_start),
                                    AbsolutePosition(file_text, string1_end))
        string2_start = string1_end+2
        text = ''.join(file_text)
        string2_end = text.find('"""', string2_start + 1) + 2
        # +2 for length of """
        string2 = SourceRange.from_absolute_position(
                                    'F',
                                    AbsolutePosition(file_text, string2_start),
                                    AbsolutePosition(file_text, string2_end))
        string3_start = text.find('"""', string2_end + 1)
        string3_end = text.find('"""', string3_start + 1) + 2
        # +2 for length of """
        string3 = SourceRange.from_absolute_position(
                                    'F',
                                    AbsolutePosition(file_text, string3_start),
                                    AbsolutePosition(file_text, string3_end))
        with execute_bear(self.python_uut, 'F', file_text) as results:
            self.assertIn(string1, results[0].contents['strings'])
            self.assertIn(string2, results[0].contents['strings'])
            self.assertIn(string3, results[0].contents['strings'])
            self.assertEqual(results[0].contents['comments'], ())

    def test_no_coalang(self):
        self.section1.append(Setting('language', 'Valyrian'))
        text = ['Valar Morghulis']
        uut = AnnotationBear(self.section1, Queue())
        with execute_bear(uut, 'F', text) as result:
            self.assertEqual(result[0].contents,
                             'coalang specification for Valyrian not found.')

    def test_escape_strings(self):
        text = [r"'I\'ll be back' -T1000"]
        uut = AnnotationBear(self.section1, Queue())
        test_range = SourceRange.from_absolute_position(
            'F',
            AbsolutePosition(text, 0),
            AbsolutePosition(text, text[0].find("'", 4)))
        with execute_bear(uut, 'F', text) as result:
            self.assertEqual(result[0].contents['strings'], (test_range,))

        text = ['''
            """"quoting inside quoting"
            """
            ''']
        uut = AnnotationBear(self.section1, Queue())
        with execute_bear(uut, 'F', text) as results:
            for result in results:
                # The """" was recognized as a string start and end before.
                # That lead to a Result being yielded because of unclosed
                # quotes, this asserts that no such thing happened.
                self.assertEqual(type(result), AnnotationResult)


class AnnotationResultTest(unittest.TestCase):

    def test_create_result_with_string_ranges_and_comment_ranges(self):
        string_ranges = (SourceRange.from_values('filename', 1),)
        comment_ranges = (SourceRange.from_values('filename', 2),)

        result = AnnotationResult(AnnotationBear, string_ranges,
                                  comment_ranges)
        self.assertEqual(result.contents, dict(strings=string_ranges,
                                               comments=comment_ranges))
        self.assertEqual(result.string_ranges, string_ranges)
        self.assertEqual(result.comment_ranges, comment_ranges)
        self.assertEqual(result.exception_msg, None)
        self.assertEqual(result.message, '')

    def test_create_result_with_exception_msg(self):
        exception_msg = 'Exception msg'

        result = AnnotationResult(AnnotationBear,
                                  exception_msg=exception_msg)
        self.assertEqual(result.contents, exception_msg)
        self.assertEqual(result.string_ranges, None)
        self.assertEqual(result.comment_ranges, None)
        self.assertEqual(result.exception_msg, exception_msg)
        self.assertEqual(result.message, exception_msg)
