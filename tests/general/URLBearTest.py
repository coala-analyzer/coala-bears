import unittest
import requests_mock

from bears.general.URLBear import URLBear, LINK_CONTEXT, URLResult
from coalib.results.SourceRange import SourceRange
from coalib.testing.LocalBearTestHelper import get_results
from coalib.settings.Section import Section
from queue import Queue

from .InvalidLinkBearTest import custom_matcher


class URLBearTest(unittest.TestCase):
    """
    The tests are mocked (don't actually connect to internet) and
    return the int conversion of the last three chars of
    the URL as status code.

    Check ``custom matcher`` for more info on implementation.
    """

    def setUp(self):
        self.section = Section('')
        self.uut = URLBear(self.section, Queue())

    def test_detect_url_result(self):
        valid_file = """
        http://www.facebook.com/200
        http://www.google.com/404
        """.splitlines()

        result = get_results(self.uut, valid_file)
        self.assertEqual(result[0].contents,
                         [2, 'http://www.facebook.com/200',
                          LINK_CONTEXT.no_context])
        self.assertEqual(result[1].contents,
                         [3, 'http://www.google.com/404',
                          LINK_CONTEXT.no_context])

    def test_invalid_url(self):
        invalid_file = """
        http://(github.com/200
        http://github].com/200
        http://github@.com/200
        http://-github.com/200
        http://github-.com/200
        http://github_.com/200
        http://_github.com/200
        http://1.com/200
        http://.com/200
        """.splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)

            result = get_results(self.uut, invalid_file)
            self.assertEqual(result, [])

    def test_termination_of_url(self):
        valid_file = """
        http://www.facebook.com/200, http://www.google.com/404.
        Check out this awesome site http://www.gmail.com/200!
        Is this url working http://www.gmail.com/404?
        """.splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)

            result = get_results(self.uut, valid_file)
            self.assertEqual(result[0].contents,
                             [2, 'http://www.facebook.com/200',
                              200, LINK_CONTEXT.no_context])
            self.assertEqual(result[1].contents,
                             [2, 'http://www.google.com/404',
                              404, LINK_CONTEXT.no_context])
            self.assertEqual(result[2].contents,
                             [3, 'http://www.gmail.com/200',
                              200, LINK_CONTEXT.no_context])
            self.assertEqual(result[3].contents,
                             [4, 'http://www.gmail.com/404',
                              404, LINK_CONTEXT.no_context])

    def test_precentage_encoded_url(self):
        valid_file = """
        # A url with a precentage-encoded character in path
        https://img.shields.io/badge/Maintained%3F-yes-green.svg/200
        """.splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)

            result = get_results(self.uut, valid_file)
            self.assertEqual(result[0].contents,
                             [3,
                              ('https://img.shields.io/badge/Maintained%3F-'
                               'yes-green.svg/200'),
                              LINK_CONTEXT.no_context])


class URLResultTest(unittest.TestCase):

    def setUp(self):
        self.affected_code = (SourceRange.from_values('filename', 1),)

    def test_urlresult_wrong_type_link(self):
        msg = ('link must be an instance of one of '
               r'\(<class \'str\'>,\) \(provided value: 17072017\)')
        with self.assertRaisesRegex(TypeError, msg):
            URLResult(URLBear, self.affected_code, 17072017,
                      LINK_CONTEXT.no_context)

    def test_urlresult_wrong_type_link_context(self):
        msg = ('link_context must be an instance of one of '
               r'\(<aenum \'LINK_CONTEXT\'>,\)'
               r' \(provided value: \'LINK_CONTEXT\.no_context\'\)')
        with self.assertRaisesRegex(TypeError, msg):
            URLResult(URLBear, self.affected_code, 'url',
                      'LINK_CONTEXT.no_context')

    def test_urlresult_object_repr(self):
        repr_result = repr(URLResult(URLBear, self.affected_code,
                                     'http://google.com',
                                     LINK_CONTEXT.no_context))
        repr_regex = (
            r'<URLResult object\(id=.+, origin=\'bearclass\', '
            r'affected_code=\(<SourceRange object\(start=<SourcePosit'
            r'ion object\(file=\'.+\', line=1, column=None\) at .+>, '
            r'end=<SourcePosition object\(file=\'.+\', line=1, column'
            r'=None\) at .+>\) at .+>,\), message=\'Found '
            r'http://google.com with context: LINK_CONTEXT.no_contex'
            r't\', link=\'http://google.com\', link_context=<LINK_CON'
            r'TEXT.no_context: 0>\) at .+>')
        self.assertRegex(repr_result, repr_regex)
