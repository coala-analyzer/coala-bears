import io
import logging
from queue import Queue
import requests
import requests_mock
import unittest
import unittest.mock

from bears.general.InvalidLinkBear import InvalidLinkBear
from bears.general.URLHeadBear import URLHeadBear
from coalib.testing.LocalBearTestHelper import LocalBearTestHelper
from coalib.results.Diff import Diff
from coalib.results.RESULT_SEVERITY import RESULT_SEVERITY
from coalib.results.Result import Result
from coalib.settings.Section import Section
from coala_utils.ContextManagers import prepare_file


def custom_matcher(request):
    """
    Mock the status codes for every request by taking the last three characters
    of the request URL.

    For connection checking url, it always passes 200 (prerequisite checking).

    For URLs with no status codes appended, a ``RequestException`` is raised.

    To test for URLs that redirect to URLs with a much larger length, the
    ``redirect_long_url`` is returned.

    :param request: The ``request`` that the mocker recieves.
    :return:        A mocked ``Response`` object.
    """
    redirect_long_url = ('https://confluence.atlassian.com/bitbucket'
                         '/use-the-bitbucket-cloud-rest-apis-222724129.html')
    redirect_urls = ('https://bitbucket.org/api/301',
                     'https://bitbucket.org/api/302')

    change_url = False
    # the connection check url needs to be explicitly
    # set to 200
    if request.url == URLHeadBear.check_connection_url:
        status_code = 200
    else:
        try:
            status_code = int(request.path_url[-3:])
        except ValueError:
            raise requests.exceptions.RequestException
    if status_code in range(300, 400):
        change_url = True
        url = (redirect_long_url if request.url in redirect_urls else
               'http://httpbin.org/get')
    resp = requests.Response()
    if change_url:
        resp.url = url
    resp.raw = io.BytesIO()
    resp.status_code = status_code
    return resp


class InvalidLinkBearTestPrerequisites(unittest.TestCase):

    def test_check_prerequisites(self):
        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)
            self.assertTrue(URLHeadBear.check_prerequisites())

            m.head(URLHeadBear.check_connection_url,
                   exc=requests.exceptions.RequestException)

            self.assertTrue(URLHeadBear.check_prerequisites() ==
                            'You are not connected to the internet.')


class InvalidLinkBearTest(LocalBearTestHelper):
    """
    The tests are mocked (don't actually connect to internet) and
    return the int conversion of the last three chars of
    the URL as status code.

    Check ``custom matcher`` for more info on implementation.
    """

    def setUp(self):
        self.ub_check_prerequisites = URLHeadBear.check_prerequisites
        self.section = Section('')
        URLHeadBear.check_prerequisites = lambda *args: True
        self.uut = InvalidLinkBear(self.section, Queue())

    def tearDown(self):
        URLHeadBear.check_prerequisites = self.ub_check_prerequisites

    def assertSeverity(self, file, severity, settings={}):
        """
        Test the warnings in each line of the file to match the
        given severity.
        :param file: The ``file`` to be checked.
        :param severity: The severity level of the warnings in each
                         line of the file.
        """
        severity_tag = RESULT_SEVERITY.reverse[severity]
        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)
            dep_bear = URLHeadBear(self.section, Queue())
            deps_results = dict(URLHeadBear=list(dep_bear.run('testfile',
                                                              file,
                                                              **settings)))

            outputs = list(self.uut.run('testfile', file, deps_results,
                                        **settings))
            for out in outputs:
                out_dict = out.to_string_dict()
                self.assertEqual(severity_tag, out_dict['severity'])

    def test_valid_url(self):
        valid_file = """
        http://httpbin.org/status/200
        http://httpbin.org/status/201
        http://httpbin.org/status/401  # Unauthorized
        """.splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)
            self.check_validity(self.uut, valid_file)

    def test_parentheses_url(self):
        valid_file = """
        # Parentheses
        https://en.wikipedia.org/wiki/Hello_(Adele_song)/200
        """.splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)
            self.check_validity(self.uut, valid_file)

    def test_quoted_url(self):
        valid_file = """
        # Quotes
        "https://github.com/coala/coala-bears/issues/200"
        'http://httpbin.org/status/203'
        ('http://httpbin.org/status/200').install_command()
        `https://coala.io/200`
        """.splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)
            self.check_validity(self.uut, valid_file)

    def test_in_markdown_url(self):
        valid_file = """
        # Markup/down stuff
        <http://httpbin.org/status/202>
        http://httpbin.org/status/204.....
        [httpbin](http://httpbin.org/status/200)
        [http://httpbin.org/status/200](http://httpbin.org/status/200)
        |http://httpbin.org/status/200|
        <h3>Something http://httpbin.org/status/200</h3>
        repo=\\"http://httpbin.org/status/200\\"
        """.splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)
            self.check_validity(self.uut, valid_file)

    def test_template_url(self):
        valid_file = """
        # Templated URLs can't be checked
        "http://httpbin.org/{status}/404".format(...)
        "http://httpbin.org/$status/404"
        """.splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)
            self.check_validity(self.uut, valid_file)

    def test_not_an_url(self):
        valid_file = """
        # Not a link
        http://not a link dot com
        http://www.%s.com
        http://www.%d.com
        http://www.%f.com
        """.splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)
            self.check_validity(self.uut, valid_file)

    def test_redirect_url(self):
        valid_file = """
        # Redirect
        http://httpbin.org/status/301
        http://httpbin.org/status/302
        """.splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)
            self.check_validity(self.uut, valid_file)

    def test_example_url(self):
        valid_file = """
        # Example.com URLs should be ignored
        http://sub.example.com/404
        """.splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)
            self.check_validity(self.uut, valid_file)

    def test_invalid_url(self):
        invalid_file = """
        http://coalaisthebest.com/
        http://httpbin.org/status/404
        http://httpbin.org/status/410
        http://httpbin.org/status/500
        http://httpbin.org/status/503
        """.splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)
            self.check_line_result_count(self.uut,
                                         invalid_file, [1, 1, 1, 1, 1])

    def test_severity(self):
        normal_severity_file = """
        http://httpbin.org/status/404
        http://httpbin.org/status/410
        http://httpbin.org/status/500
        http://httpbin.org/status/503
        http://httpbin.org/status/301
        http://httpbin.org/status/302
        """.splitlines()

        self.assertSeverity(normal_severity_file, RESULT_SEVERITY.NORMAL)

        major_severity_file = """
        http://coalaisthebest.com
        """.splitlines()

        self.assertSeverity(major_severity_file, RESULT_SEVERITY.MAJOR)

    def test_redirect_threshold(self):
        long_url_redirect = """
        https://bitbucket.org/api/301
        https://bitbucket.org/api/302
        """.splitlines()

        short_url_redirect = """
        http://httpbin.org/status/301
        """.splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)

            self.check_validity(self.uut, long_url_redirect,
                                settings={'follow_redirects': 'true'})

            with prepare_file(short_url_redirect, None,
                              create_tempfile=False) as (lines, _):
                diff = Diff(lines)
                diff.modify_line(2,
                                 '        http://httpbin.org/get\n')

            self.check_results(
                self.uut,
                short_url_redirect,
                [Result.from_values(
                    'InvalidLinkBear',
                    'This link redirects to http://httpbin.org/get',
                    severity=RESULT_SEVERITY.NORMAL,
                    line=2,
                    file='short_url_redirect_text',
                    diffs={'short_url_redirect_text': diff},
                )],
                settings={'follow_redirects': 'true'},
                filename='short_url_redirect_text')

    def test_multiple_results_per_line(self):
        test_file = """
        http://httpbin.org/status/410
        http://httpbin.org/status/200
        http://httpbin.org/status/404 http://httpbin.org/status/410
        http://httpbin.org/status/200 http://httpbin.org/status/404
        http://httpbin.org/status/200 http://httpbin.org/status/201
        """.splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)

            expected_num_results = [1, 0, 2, 1, 0]
            self.check_line_result_count(self.uut, test_file,
                                         expected_num_results)

    def test_pip_vcs_url(self):
        with_at = """
        git+http://httpbin.org/status/200@master
        svn+http://httpbin.org/status/200@master
        hg+http://httpbin.org/status/200@master
        bzr+http://httpbin.org/status/200@master
        """.splitlines()

        with_hash = """
        git+http://httpbin.org/status/200#egg=coala-bears
        svn+http://httpbin.org/status/200#egg=coala-bears
        hg+http://httpbin.org/status/200#egg=coala-bears
        bzr+http://httpbin.org/status/200#egg=coala-bears
        """.splitlines()

        with_at_hash = """
        git+http://httpbin.org/status/200@master#egg=coala-bears
        svn+http://httpbin.org/status/200@master#egg=coala-bears
        hg+http://httpbin.org/status/200@master#egg=coala-bears
        bzr+http://httpbin.org/status/200@master#egg=coala-bears
        """.splitlines()

        brokenlink_at = """git+http://httpbin.org/status/404@master
        svn+http://httpbin.org/status/404@master
        hg+http://httpbin.org/status/404@master
        bzr+http://httpbin.org/status/404@master
        """.splitlines()

        brokenlink_hash = """git+http://httpbin.org/status/404#egg=coala-bears
        svn+http://httpbin.org/status/404#egg=coala-bears
        hg+http://httpbin.org/status/404#egg=coala-bears
        bzr+http://httpbin.org/status/404#egg=coala-bears
        """.splitlines()

        brokenlink_at_hash = """
        git+http://httpbin.org/status/404@master#egg=coala-bears
        svn+http://httpbin.org/status/404@master#egg=coala-bears
        hg+http://httpbin.org/status/404@master#egg=coala-bears
        bzr+http://httpbin.org/status/404@master#egg=coala-bears
        """.splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)

            self.check_validity(self.uut, with_at)
            self.check_validity(self.uut, with_hash)
            self.check_validity(self.uut, with_at_hash)

            self.check_line_result_count(self.uut, brokenlink_at,
                                         [1, 1, 1, 1])

            self.check_line_result_count(self.uut, brokenlink_hash,
                                         [1, 1, 1, 1])

            self.check_line_result_count(self.uut, brokenlink_at_hash,
                                         [1, 1, 1, 1])

    def test_xml_namespaces(self):
        valid_file = """
        #Namespace and also a valid link
        <ruleset name="test" xmlns="http://httpbin.org/status/200">

        # xml where xmlns: and xsi:schema are valid links
        <ruleset name="test" xmlns="http://xmlnamespace.org/status/200"
        xmlns:xsi="http://xmlnamespace.org/status/200"
        xsi:schemaLocation="http://xmlnamespace.org/status/200">
        """.splitlines()

        invalid_file = """
        <ruleset name="test" xmlns="http://this.isa.namespace/ruleset/7.0.0"
        xmlns:xsi="http://this.is.another/kindof/namespace"
        xsi:schemaLocation="http://this.namespace.dosent/exists/7.0.0"
        xsi:schemaLocation="http://httpbin.com/404">""".splitlines()

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)

            self.check_validity(self.uut, valid_file)

            self.check_line_result_count(self.uut, invalid_file,
                                         [1, 1, 1, 1])

        info_severity_file = """
        <ruleset name="test" xmlns="http://this.is.a.namespace/ruleset/7.0.0"
        xmlns:xsi="http://this.is.another/kindof/namespace"
        xsi:schemaLocation="http://this.is.a.namespace/ruleset/7.0.0"/>

        <ruleset name="test" xmlns="http://a.new.namespace/ruleset/7.0.0"
        xmlns:xsi="http://another.namespace/ruleset/7.0.0"
        xsi:schemaLocation="http://another.namespace/ruleset/7.0.0"/>

        <layer-list xmlns:android="http://schema.android.com/apk/res/android"/>

        # Multiple ocurrences of namespaces
        <stylesheet xmlns="http://one.more.namespace/xsl/transform"
        xmlns:html="http://httpbin.com/200"
        xsi:schemaLocation="http://this.is.a.namespace/ruleset/7.0.0
                            http://another.namespace/ruleset/7.0.0
                            http://one.more.namespace/xsl/transform"/>
        """.splitlines()

        self.assertSeverity(info_severity_file, RESULT_SEVERITY.INFO)

        normal_severity_file = """
        xsi:schemaLocation="http://httpbin.com/404"
        """.splitlines()

        self.assertSeverity(normal_severity_file, RESULT_SEVERITY.NORMAL)

    def test_links_to_ignore(self):
        valid_file = """http://httpbin.org/status/200
        http://httpbin.org/status/201
        http://coalaisthebest.com/
        http://httpbin.org/status/404
        http://httpbin.org/status/410
        http://httpbin.org/status/500/
        http://httpbin.org/status/503/
        http://www.notexample.com/404
        http://exampe.com/404
        http://example.co.in/404""".splitlines()

        link_ignore_list = [
                           'http://coalaisthebest.com/',
                           'http://httpbin.org/status/4[0-9][0-9]',
                           'http://httpbin.org/status/410/',
                           'http://httpbin.org/status/5[0-9][0-9]/',
                           'http://httpbin.org/status/503/',
                           'http://www.notexample.com/404',
                           '//exampe.com/404',
                           'http://example.co.in/404'
                          ]

        with requests_mock.Mocker() as m:
            m.add_matcher(custom_matcher)
            self.check_validity(self.uut, valid_file,
                                settings={'link_ignore_list': link_ignore_list}
                                )

    def test_variable_timeouts(self):
        nt = {
            'https://google.com/timeout/test/2/3/4/5/something': 10,
            'https://facebook.com/timeout': 2,
            '*': 25
        }

        file_contents = """
        https://facebook.com/
        https://google.com/
        https://coala.io/som/thingg/page/123
        """.splitlines()

        def response(status_code, *args, **kwargs):
            res = requests.Response()
            res.status_code = status_code
            return res

        with unittest.mock.patch(
                'tests.general.InvalidLinkBearTest.requests.head',
                return_value=response(status_code=200)) as mock:
            self.check_validity(self.uut, file_contents,
                                settings={'network_timeout': nt})

            with self.assertLogs(logging.getLogger()) as log:
                self.check_validity(self.uut, file_contents,
                                    settings={'timeout': 20})
                self.assertEqual(log.output,
                                 ['WARNING:root:The setting `timeout` is '
                                  'deprecated. Please use `network_timeout` '
                                  'instead.'])

            self.check_validity(self.uut, ['https://gitmate.io'])
            mock.assert_has_calls([
                unittest.mock.call('https://facebook.com/', timeout=2,
                                   allow_redirects=False),
                unittest.mock.call('https://google.com/',
                                   timeout=10, allow_redirects=False),
                unittest.mock.call('https://coala.io/som/thingg/page/123',
                                   timeout=25, allow_redirects=False),
                unittest.mock.call('https://facebook.com/', timeout=20,
                                   allow_redirects=False),
                unittest.mock.call('https://google.com/',
                                   timeout=20, allow_redirects=False),
                unittest.mock.call('https://coala.io/som/thingg/page/123',
                                   timeout=20, allow_redirects=False),
                unittest.mock.call('https://gitmate.io',
                                   timeout=15, allow_redirects=False)])
