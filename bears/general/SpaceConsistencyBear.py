from coalib.bearlib import deprecate_settings
from coalib.bearlib.spacing.SpacingHelper import SpacingHelper
from coalib.bears.LocalBear import LocalBear
from coalib.results.Diff import Diff
from coalib.results.Result import Result


class SpaceConsistencyBear(LocalBear):
    LANGUAGES = {'All'}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_FIX = {'Formatting'}

    @deprecate_settings(indent_size='tab_width')
    def run(self,
            filename,
            file,
            use_spaces: bool,
            allow_trailing_whitespace: bool=False,
            allow_trailing_blanklines: bool=False,
            indent_size: int=SpacingHelper.DEFAULT_TAB_WIDTH,
            enforce_newline_at_EOF: bool=True):
        '''
        Check and correct spacing for all textual data. This includes usage of
        tabs vs. spaces, trailing whitespace and (missing) newlines before
        the end of the file.

        :param use_spaces:
            True if spaces are to be used instead of tabs.
        :param allow_trailing_whitespace:
            Whether to allow trailing whitespace or not.
        :param allow_trailing_blanklines:
            Whether to allow trailing blanklines at EOF or not.
        :param indent_size:
            Number of spaces per indentation level.
        :param enforce_newline_at_EOF:
            Whether to enforce a newline at the End Of File.
        '''
        spacing_helper = SpacingHelper(indent_size)
        result_texts = []
        additional_info_texts = []

        if not allow_trailing_blanklines:
            line_nr_start = next(
                    (i
                     for i, line in reversed(list(enumerate(file, start=0)))
                     if line.strip() != ''), -1) + 1
            if line_nr_start < len(file):
                additional_info_text = (
                    'Your source code contains trailing blanklines at EOF.'
                    'Those usually have no meaning. Please consider'
                    'removing them.')
                diff = Diff(file)
                diff.delete_lines(line_nr_start + 1, len(file))
                yield Result.from_values(
                    self,
                    'Trailing blanklines found.',
                    diffs={filename: diff},
                    file=filename,
                    line=line_nr_start + 1,
                    column=1,
                    end_line=len(file),
                    end_column=len(file[-1]),
                    additional_info=additional_info_text)

        else :
            line_nr_start = len(file)

        for line_number, line in enumerate(file[:line_nr_start],
                                           start=1):
            replacement = line

            if enforce_newline_at_EOF:
                # Since every line contains at the end at least one \n, only
                # the last line could potentially not have one. So we don't
                # need to check whether the current line_number is the last
                # one.
                if replacement[-1] != '\n':
                    replacement += '\n'
                    result_texts.append('No newline at EOF.')
                    additional_info_texts.append(
                        "A trailing newline character ('\\n') is missing from "
                        'your file. '
                        '<http://stackoverflow.com/a/5813359/3212182> gives '
                        'more information about why you might need one.')

            if not allow_trailing_whitespace:
                replacement = replacement.rstrip(' \t\n') + '\n'
                if replacement != line.rstrip('\n') + '\n':
                    result_texts.append('Trailing whitespaces.')
                    additional_info_texts.append(
                        'Your source code contains trailing whitespaces. '
                        'Those usually have no meaning. Please consider '
                        'removing them.')

            if use_spaces:
                pre_replacement = replacement
                replacement = replacement.expandtabs(indent_size)
                if replacement != pre_replacement:
                    result_texts.append('Tabs used instead of spaces.')
            else:
                pre_replacement = replacement
                replacement = spacing_helper.replace_spaces_with_tabs(
                    replacement)
                if replacement != pre_replacement:
                    result_texts.append('Spaces used instead of tabs.')

            if len(result_texts) > 0:
                diff = Diff(file)
                diff.change_line(line_number, line, replacement)
                inconsistencies = ''.join('\n- ' + string
                                          for string in result_texts)
                yield Result.from_values(
                    self,
                    'Line contains following spacing inconsistencies:'
                    + inconsistencies,
                    diffs={filename: diff},
                    file=filename,
                    line=line_number,
                    additional_info='\n\n'.join(additional_info_texts))
                result_texts = []
                additional_info_texts = []
