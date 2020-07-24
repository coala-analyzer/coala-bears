import re
import logging

from coalib.bears.LocalBear import LocalBear
from coalib.results.Result import Result
from coalib.results.RESULT_SEVERITY import RESULT_SEVERITY


class LineCountBear(LocalBear):
    LANGUAGES = {'All'}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Formatting'}

    def _get_blank_line_count(self, file):
        pattern = re.compile(r'^\s*$')
        num_blank_lines = len([x for x in file if pattern.match(x)])
        return num_blank_lines

    def run(self, filename, file, min_lines_per_file: int = 1,
            max_lines_per_file: int = 1000,
            exclude_blank_lines: bool = False,
            ):
        """
        Count the number of lines in a file and ensure that they lie within
        the range of given sizes.

        :param min_lines_per_file: Minimum number of lines required per file.
        :param max_lines_per_file: Maximum number of lines allowed per file.
        :param exclude_blank_lines: ``True`` if blank lines are to be excluded.
        """
        file_length = len(file)
        if min_lines_per_file > max_lines_per_file:
            logging.error('Allowed maximum lines per file ({}) is smaller '
                          'than minimum lines per file ({})'
                          .format(max_lines_per_file,
                                  min_lines_per_file))
            return

        if exclude_blank_lines:
            num_blank_lines = self._get_blank_line_count(file)
            file_length = file_length - num_blank_lines

        if file_length > max_lines_per_file:
            yield Result.from_values(
                origin=self,
                message=('This file had {count} lines, which is {extra} '
                         'lines more than the maximum limit specified.'
                         .format(count=file_length,
                                 extra=file_length-max_lines_per_file)),
                severity=RESULT_SEVERITY.NORMAL,
                file=filename)

        elif file_length < min_lines_per_file:
            yield Result.from_values(
                origin=self,
                message=('This file has {} lines, while {} lines are '
                         'required.'
                         .format(file_length,
                                 min_lines_per_file)),
                file=filename)
