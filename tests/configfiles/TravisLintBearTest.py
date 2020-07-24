import os
import requests
import requests_mock
from queue import Queue
from unittest.mock import patch

from coalib.results.Result import Result
from coalib.results.RESULT_SEVERITY import RESULT_SEVERITY
from coalib.settings.Section import Section
from coalib.testing.LocalBearTestHelper import LocalBearTestHelper
from coalib.testing.BearTestHelper import generate_skip_decorator

from bears.configfiles.TravisLintBear import TravisLintBear


def get_testfile_path(name):
    return os.path.join(os.path.dirname(__file__),
                        'travislint_test_files',
                        name)


def load_testfile(name):
    with open(get_testfile_path(name)) as fl:
        return fl.readlines()


@generate_skip_decorator(TravisLintBear)
class TravisLintBearTest(LocalBearTestHelper):

    def setUp(self):
        self.uut = TravisLintBear(Section('name'), Queue())

    def test_good_file(self):
        file_name = '.good_travis.yml'
        file_contents = load_testfile(file_name)
        self.check_results(
            self.uut,
            file_contents,
            [],
            filename=get_testfile_path(file_name))

    def test_bad_file(self):
        file_name = '.bad_travis.yml'
        file_contents = load_testfile(file_name)
        self.check_results(
            self.uut,
            file_contents,
            [Result.from_values('TravisLintBear',
                                message='in matrix.exclude section: '
                                        'specified ruby, but setting is '
                                        'not relevant for python',
                                file=get_testfile_path(file_name),
                                severity=RESULT_SEVERITY.NORMAL),
             Result.from_values('TravisLintBear',
                                message='in os section: dropping osx, does'
                                        ' not support python',
                                file=get_testfile_path(file_name),
                                severity=RESULT_SEVERITY.NORMAL),
             Result.from_values('TravisLintBear',
                                message='specified ruby, but setting is '
                                        'not relevant for python',
                                file=get_testfile_path(file_name),
                                severity=RESULT_SEVERITY.NORMAL)],
            filename=get_testfile_path(file_name))

    def test_empty_file(self):
        file_name = '.empty_travis.yml'
        file_contents = load_testfile(file_name)
        self.check_results(
            self.uut,
            file_contents,
            [Result.from_values('TravisLintBear',
                                message='missing key language, defaulting '
                                        'to ruby',
                                file=get_testfile_path(file_name),
                                severity=RESULT_SEVERITY.NORMAL)],
            filename=get_testfile_path(file_name))

    def test_check_prerequisites(self):
        with requests_mock.Mocker() as m:
            check_connection_url = 'https://travis-ci.org/'
            m.head(check_connection_url,
                   status_code=200)
            self.assertEqual(TravisLintBear.check_prerequisites(), True)

            m.head(check_connection_url,
                   exc=requests.exceptions.RequestException)
            self.assertEqual(TravisLintBear.check_prerequisites(),
                             'You are not connected to the internet.')

            m.head(check_connection_url,
                   status_code=404)
            self.assertEqual(TravisLintBear.check_prerequisites(),
                             'Failed to establish a connection to '
                             'https://travis-ci.org/.')

        # The primary base class is not the `LinterBase` inside `@linter`,
        # but the class the user writes because of this mixin-technique
        # `@linter` uses.
        with patch.object(TravisLintBear.__bases__[1],
                          'check_prerequisites') as mock_method:
            base_check_fail_message = 'travis is not installed.'
            mock_method.return_value = base_check_fail_message
            self.assertEqual(base_check_fail_message,
                             TravisLintBear.check_prerequisites())
