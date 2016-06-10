import autopep8

from coalib.bearlib.spacing.SpacingHelper import SpacingHelper
from coalib.bears.LocalBear import LocalBear
from coalib.results.Diff import Diff
from coalib.results.Result import Result
from coalib.settings.Setting import typed_list


class PEP8Bear(LocalBear):
    LANGUAGES = ("Python", "Python 2", "Python 3")

    def run(self, filename, file,
            max_line_length: int=80,
            tab_width: int=SpacingHelper.DEFAULT_TAB_WIDTH,
            pep_ignore: typed_list(str)=(),
            pep_select: typed_list(str)=(),
            local_pep8_config: bool=False):
        """
        Detects and fixes PEP8 incompliant code. This bear will not change
        functionality of the code in any way.

        :param max_line_length:   Maximum number of characters for a line.
        :param tab_width:         Number of spaces per indent level.
        :param pep_ignore:        A list of errors/warnings to ignore.
        :param pep_select:        A list of errors/warnings to exclusively
                                  apply.
        :param local_pep8_config: Set to true if autopep8 should use a config
                                  file as if run normally from this directory.
        """
        options = {"ignore": pep_ignore,
                   "select": pep_select,
                   "max_line_length": max_line_length,
                   "indent_size": tab_width}

        corrected = autopep8.fix_code(''.join(file),
                                      apply_config=local_pep8_config,
                                      options=options).splitlines(True)

        diffs = Diff.from_string_arrays(file, corrected).split_diff()

        for diff in diffs:
            yield Result(self,
                         "The code does not comply to PEP8.",
                         affected_code=(diff.range(filename),),
                         diffs={filename: diff})