import os
from coalib.results.result_actions.ResultAction import ResultAction


class DeleteFileAction(ResultAction):
    """
    Deletes a file
    """

    SUCCESS_MESSAGE = 'File deleted successfully.'

    def __init__(self, filename):
        self.filename = filename
        self.description = ('Delete {} [Note: This will '
                            'delete the file permanently]').format(filename)

    @staticmethod
    def is_applicable(result,
                      original_file_dict,
                      file_diff_dict,
                      applied_actions=()):
        return 'DeleteFileAction' not in applied_actions

    def apply(self, result, original_file_dict, file_diff_dict):
        os.remove(self.filename)
        return file_diff_dict
