import autopep8
import sys

from coalib.bearlib import deprecate_settings
from coalib.bearlib.spacing.SpacingHelper import SpacingHelper
from coalib.bears.LocalBear import LocalBear
from dependency_management.requirements.PipRequirement import PipRequirement
from coalib.results.Diff import Diff
from coalib.results.Result import Result
from coalib.settings.Setting import typed_list
from coalib.bearlib.aspects import map_setting_to_aspect
from coalib.bearlib.aspects.Formatting import (
    Formatting,
    LineLength,
)


class PEP8Bear(
        LocalBear,
        aspects={
            'detect': [
                LineLength,
            ]},
        languages=['Python'],
        ):
    LANGUAGES = {'Python', 'Python 2', 'Python 3'}
    REQUIREMENTS = {PipRequirement('autopep8', '1.2')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_FIX = {'Formatting'}
    ASCIINEMA_URL = 'https://asciinema.org/a/165394'

    @map_setting_to_aspect(
        max_line_length=LineLength.max_line_length,
        )
    @deprecate_settings(indent_size='tab_width')
    def run(self, filename, file,
            max_line_length: int = 79,
            indent_size: int = SpacingHelper.DEFAULT_TAB_WIDTH,
            pep_ignore: typed_list(str) = (),
            pep_select: typed_list(str) = (),
            local_pep8_config: bool = False,
            ):
        """
        Detects and fixes PEP8 incompliant code. This bear will not change
        functionality of the code in any way.

        :param max_line_length:
            Maximum number of characters for a line.
            When set to 0 allows infinite line length.
        :param indent_size:
            Number of spaces per indentation level.
        :param pep_ignore:
            A list of errors/warnings to ignore.
        :param pep_select:
            A list of errors/warnings to exclusively apply.
        :param local_pep8_config:
            Set to true if autopep8 should use a config file as if run normally
            from this directory.
        """
        if not max_line_length:
            max_line_length = sys.maxsize

        options = {'ignore': pep_ignore,
                   'select': pep_select,
                   'max_line_length': max_line_length,
                   'indent_size': indent_size}

        corrected = autopep8.fix_code(''.join(file),
                                      apply_config=local_pep8_config,
                                      options=options).splitlines(True)

        diffs = Diff.from_string_arrays(file, corrected).split_diff()

        for diff in diffs:
            yield Result(self,
                         'The code does not comply to PEP8.',
                         affected_code=(diff.range(filename),),
                         diffs={filename: diff},
                         aspect=Formatting('py'),
                         )
