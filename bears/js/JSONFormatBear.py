import json
import sys
from collections import OrderedDict
from re import match

from coala_utils.param_conversion import negate
from coalib.bearlib import deprecate_settings
from coalib.bearlib.spacing.SpacingHelper import SpacingHelper
from coalib.bears.LocalBear import LocalBear
from coalib.misc.Compatibility import JSONDecodeError
from coalib.results.Diff import Diff
from coalib.results.Result import Result


class JSONFormatBear(LocalBear):

    LANGUAGES = {'JSON'}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    ASCIINEMA_URL = 'https://asciinema.org/a/6vxc7076tnf996zanpdfwojwu'
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Formatting'}

    @deprecate_settings(indent_size='tab_width',
                        escape_unicode=('keep_unicode', negate))
    def run(self, filename, file,
            max_line_length: int = 0,
            json_sort: bool = False,
            indent_size: int = SpacingHelper.DEFAULT_TAB_WIDTH,
            escape_unicode: bool = True,
            ):
        """
        Raises issues for any deviations from the pretty-printed JSON.

        :param max_line_length: Maximum number of characters for a line.
                                When set to 0 allows infinite line length.
        :param json_sort:       Whether or not keys should be sorted.
        :param indent_size:     Number of spaces per indentation level.
        :param escape_unicode:  Whether or not to escape unicode values using
                                ASCII.
        """
        if not max_line_length:
            max_line_length = sys.maxsize

        # Output a meaningful message if empty file given as input
        if len(file) == 0:
            yield Result.from_values(self,
                                     'This file is empty.',
                                     file=filename)
            return

        try:
            json_content = json.loads(''.join(file),
                                      object_pairs_hook=OrderedDict)
        except JSONDecodeError as err:
            err_content = match(r'(.*): line (\d+) column (\d+)', str(err))
            yield Result.from_values(
                self,
                'This file does not contain parsable JSON. ' +
                err_content.group(1) + '.',
                file=filename,
                line=int(err_content.group(2)),
                column=int(err_content.group(3)))
            return

        for line_number, line in enumerate(file):
            line = line.expandtabs(indent_size)
            if len(line) > max_line_length + 1:
                yield Result.from_values(
                    origin=self,
                    message='Line is longer than allowed.'
                            ' ({actual} > {maximum})'.format(
                                actual=len(line)-1,
                                maximum=max_line_length),
                    file=filename,
                    line=line_number + 1,
                    column=max_line_length + 1,
                    end_line=line_number + 1,
                    end_column=len(line),
                    )

        corrected = json.dumps(json_content,
                               sort_keys=json_sort,
                               indent=indent_size,
                               ensure_ascii=escape_unicode
                               ).splitlines(True)
        # Because of a bug in several python versions we have to correct
        # whitespace here.
        corrected = tuple(line.rstrip(' \n') + '\n' for line in corrected)
        diff = Diff.from_string_arrays(file, corrected)

        if len(diff) > 0:
            # Appropriate message is displayed to the user based on
            # json_sort value
            format_message = ('This file can be reformatted '
                              'by following indentation.')
            if json_sort:
                format_message = ('This file can be reformatted by sorting '
                                  'keys and following indentation.')
            yield Result(self,
                         format_message,
                         affected_code=tuple(d.range(filename)
                                             for d in diff.split_diff()),
                         diffs={filename: diff})
