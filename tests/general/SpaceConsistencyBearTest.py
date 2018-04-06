from queue import Queue

from bears.general.SpaceConsistencyBear import (
    SpaceConsistencyBear, SpacingHelper)
from coalib.testing.LocalBearTestHelper import LocalBearTestHelper
from coalib.results.Result import Result
from coalib.results.RESULT_SEVERITY import RESULT_SEVERITY
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting


class SpaceConsistencyBearTest(LocalBearTestHelper):

    def setUp(self):
        self.section = Section('test section')
        self.uut = SpaceConsistencyBear(self.section, Queue())

    def test_needed_settings(self):
        self.section.append(Setting('use_spaces', 'true'))

        needed_settings = self.uut.get_non_optional_settings()
        self.assertEqual(len(needed_settings),
                         1 + len(SpacingHelper.get_non_optional_settings()))
        self.assertIn('use_spaces', needed_settings)

    def test_defaults(self):
        # use_spaces is no default, need to set it explicitly.
        self.section.append(Setting('use_spaces', 'true'))

        self.check_validity(self.uut, ['    t'])
        self.check_invalidity(self.uut, ['\tt'])
        self.check_invalidity(self.uut, ['t \n'])
        self.check_invalidity(self.uut, ['t'],
                              force_linebreaks=False)

    def test_data_sets_spaces(self):
        self.section.append(Setting('use_spaces', 'true'))
        self.section.append(Setting('allow_trailing_whitespace', 'false'))
        self.section.append(Setting('enforce_newline_at_EOF', 'false'))

        self.check_validity(self.uut, ['    t'])
        self.check_invalidity(self.uut, ['t \n'])
        self.check_invalidity(self.uut, ['\tt\n'])

    def test_data_sets_tabs(self):
        self.section.append(Setting('use_spaces', 'false'))
        self.section.append(Setting('allow_trailing_whitespace', 'true'))
        self.section.append(Setting('enforce_newline_at_EOF', 'false'))
        self.section.append(Setting('allow_trailing_blanklines', 'false'))

        self.check_invalidity(self.uut, ['    t'])
        self.check_validity(self.uut, ['t \n'])
        self.check_validity(self.uut, ['\tt\n'])
        self.check_validity(self.uut, [])

    def test_enforce_newline_at_eof(self):
        self.section.append(Setting('use_spaces', 'true'))
        self.section.append(Setting('allow_trailing_whitespace', 'true'))
        self.section.append(Setting('enforce_newline_at_EOF', 'true'))
        self.section.append(Setting('allow_trailing_blanklines', 'true'))

        self.check_validity(self.uut,
                            ['hello world  \n'],
                            force_linebreaks=False)
        self.check_validity(self.uut,
                            ['def somecode():\n',
                             "    print('funny')\n",
                             "    print('funny end.')\n",
                             '  \n',
                             '\n'],
                            force_linebreaks=False)
        self.check_invalidity(self.uut,
                              [' no hello world'],
                              force_linebreaks=False)
        self.check_invalidity(self.uut,
                              ['def unfunny_code():\n',
                               "    print('funny')\n",
                               "    print('the result is not funny...')"],
                              force_linebreaks=False)

    def test_trailing_blanklines(self):

        self.maxDiff = None
        self.section['use_spaces'] = 'true'
        self.section['allow_trailing_whitespace'] = 'false'
        self.section['enforce_newline_at_EOF'] = 'true'
        self.section['allow_trailing_blanklines'] = 'false'
        self.check_results(self.uut,
                           ['  \n'],
                           [Result.from_values('SpaceConsistencyBear',
                                               'Trailing blanklines found.',
                                               file='xyz.py',
                                               line=1,
                                               column=1,
                                               end_line=1,
                                               end_column=3)],
                           filename = 'xyz.py')
#        self.check_results(self.uut,
#                           ['  \n',
#                            '     \n',
#                            '\n'],
#                           [Result.from_values('SpaceConsistencyBear',
#                                               'Trailing blanklines found.',
#                                               file='xyz.py',
#                                               line=1,
#                                               column=1,
#                                               end_line=3,
#                                               end_column=1,
#                                               severity=RESULT_SEVERITY.NORMAL
#                                               )],
#                           filename='xyz.py')
