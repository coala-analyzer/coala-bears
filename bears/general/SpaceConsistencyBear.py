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
            allow_trailing_whitespace: bool = False,
            allow_leading_blanklines: bool = False,
            indent_size: int = SpacingHelper.DEFAULT_TAB_WIDTH,
            enforce_newline_at_EOF: bool = True,
            ):
        '''
        Check and correct spacing for all textual data. This includes usage of
        tabs vs. spaces, trailing whitespace and (missing) newlines before
        the end of the file.

        :param use_spaces:
            True if spaces are to be used instead of tabs.
        :param allow_trailing_whitespace:
            Whether to allow trailing whitespace or not.
        :param indent_size:
            Number of spaces per indentation level.
        :param enforce_newline_at_EOF:
            Whether to enforce a newline at the End Of File.
        :param allow_leading_blanklines:
            Whether to allow leading blank lines at the start
            of file or not.
        '''
        spacing_helper = SpacingHelper(indent_size)
        result_texts = []
        additional_info_texts = []

        def end_blanklines():
            end_line = False
            enumerated_zip_obj = zip(range(1, len(file) + 1), file)
            enumerated_tuple = tuple(enumerated_zip_obj)

            for line_number, line in enumerated_tuple:
                replacement = line
                if replacement.strip() == '':
                    end_line = line_number
                else:
                    break
            return end_line

        if allow_leading_blanklines:
            start_line_of_file = 1
        else:
            end_blanklines = end_blanklines()
            start_line_of_file = 1
            if end_blanklines:
                start_line_of_file = end_blanklines + 1
                result_texts.append('Leading blank lines.')
                additional_info_texts.append(
                    'Your source code contains leading blank lines.'
                    'Those usually have no meaning. Please consider '
                    'removing them.')
                diff = Diff(file)
                diff.delete_lines(1, end_blanklines)
                inconsistencies = ''.join('\n- ' + string
                                          for string in result_texts)
                yield Result.from_values(
                    self,
                    'Line contains following spacing inconsistencies:'
                    + inconsistencies,
                    diffs={filename: diff},
                    file=filename,
                    additional_info='\n\n'.join(additional_info_texts))
                result_texts = []
                additional_info_texts = []

        for line_number, line in enumerate(file[start_line_of_file - 1:],
                                           start=start_line_of_file):
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
