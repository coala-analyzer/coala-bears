import itertools

from coalib.bears.GlobalBear import GlobalBear
from coalib.results.Result import Result
from coalib.results.RESULT_SEVERITY import RESULT_SEVERITY
from bears.general.actions.DeleteFileAction import DeleteFileAction


class DuplicateFileBear(GlobalBear):
    LANGUAGES = {'All'}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Duplication'}

    def run(self):
        """
        Checks for Duplicate Files
        """
        if not self.file_dict:
            yield Result(self, 'You did not add any file to compare',
                         severity=RESULT_SEVERITY.MAJOR)
        elif len(self.file_dict) == 1:
            yield Result(self, 'You included only one file',
                         severity=RESULT_SEVERITY.MAJOR)
        else:
            unique_tuples = [file_tuple for file_tuple in
                             itertools.combinations(self.file_dict, 2)]

            for file_pair in unique_tuples:
                if (self.file_dict[file_pair[0]] ==
                        self.file_dict[file_pair[1]]):
                    first_file_name = file_pair[0]
                    second_file_name = file_pair[1]
                    message = ('File ' + first_file_name + ' is identical'
                               ' to File ' + second_file_name)
                    yield Result(origin=self,
                                 message=message,
                                 severity=RESULT_SEVERITY.INFO,
                                 actions=[DeleteFileAction(first_file_name),
                                          DeleteFileAction(second_file_name)])
