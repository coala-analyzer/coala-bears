import os
from coalib.bears.LocalBear import LocalBear
from coalib.results.Diff import Diff
from coalib.results.Result import Result


class ShebangBear(LocalBear):
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_FIX = {'Syntax'}

    def run(self, filename, file):
        """
        Ensure that the file uses the generic Shebang operator.
        """
        if not file or file[0].startswith('#!/usr/bin/env'):
            return
        if file[0].startswith('#!'):
            diff = Diff(file)
            message = None
            binary = os.path.basename(file[0]).strip('\n')
            new_line = '#!/usr/bin/env {}'.format(binary)
            diff.modify_line(1, new_line)
            message_desc = ('This eliminates the limitations caused by systems'
                            ' that have non-standard file system layout')
            message = 'Use the {}.\n{}.'.format(repr(new_line), message_desc)

            yield Result(
                self,
                message,
                diff.affected_code(filename),
                diffs={filename: diff})
