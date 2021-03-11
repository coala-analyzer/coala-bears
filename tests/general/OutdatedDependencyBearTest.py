import unittest.mock
import sarge
from queue import Queue

from bears.general.OutdatedDependencyBear import OutdatedDependencyBear
from coalib.testing.LocalBearTestHelper import LocalBearTestHelper
from coalib.results.Result import Result
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting


test_file = """
foo==1.0
bar==2.0
"""


class OutdatedDependencyBearTest(LocalBearTestHelper):

    def setUp(self):
        self.section = Section('')
        self.uut = OutdatedDependencyBear(self.section, Queue())

    @unittest.mock.patch('bears.general.OutdatedDependencyBear.'
                         'PipRequirement.get_latest_version')
    def test_pip_outdated_requirement(self, _mock):
        self.section.append(Setting('requirement_type', 'pip'))
        _mock.return_value = '3.0'
        with unittest.mock.patch('bears.general.OutdatedDependencyBear.'
                                 'run') as mock:
            patched = unittest.mock.Mock(spec=sarge.Pipeline)
            patched.stdout = unittest.mock.Mock(spec=sarge.Capture)
            patched.stdout.text = 'foo==1.0\nbar==2.0'
            mock.return_value = patched
            message = ('The requirement {} with version {} is not '
                       'pinned to its latest version 3.0.')
            self.check_results(self.uut,
                               test_file.splitlines(True),
                               [Result.from_values(
                                    origin='OutdatedDependencyBear',
                                    message=message.format('foo', '1.0'),
                                    file='default',
                                    line=2, end_line=2,
                                    ),
                                Result.from_values(
                                    origin='OutdatedDependencyBear',
                                    message=message.format('bar', '2.0'),
                                    file='default',
                                    line=3, end_line=3,
                                    )],
                               filename='default',
                               )

    @unittest.mock.patch('bears.general.OutdatedDependencyBear.'
                         'PipRequirement.get_latest_version')
    def test_pip_latest_requirement(self, _mock):
        self.section.append(Setting('requirement_type', 'pip'))
        _mock.return_value = '1.0'
        with unittest.mock.patch('bears.general.OutdatedDependencyBear.'
                                 'run') as mock:
            patched = unittest.mock.Mock(spec=sarge.Pipeline)
            patched.stdout = unittest.mock.Mock(spec=sarge.Capture)
            patched.stdout.text = 'foo==1.0'
            mock.return_value = patched
            self.check_results(self.uut,
                               [test_file.splitlines()[0]],
                               [],
                               filename='default')

    def test_requirement_type_value_error(self):
        self.section.append(Setting('requirement_type', 'blabla'))
        error = ('ValueError: Currently the bear only supports pip as '
                 'requirement_type.')
        with self.assertRaisesRegex(AssertionError, error):
            self.check_validity(self.uut, [], filename='default')
