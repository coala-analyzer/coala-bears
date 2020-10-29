from coalib.bearlib.abstractions.Linter import linter
from coalib.results.Result import Result
from coalib.results.RESULT_SEVERITY import RESULT_SEVERITY
import json


@linter(executable='vale')
class ValeLintBear:
    """
    Lints prose and other natural language using the vale linter.

    <https://valelint.github.io>
    """
    SEVERITY_MAP = {'warning': RESULT_SEVERITY.NORMAL,
                    'error': RESULT_SEVERITY.MAJOR}

    @staticmethod
    def create_arguments(filename, file, config_file):
        return ('--output=JSON', '--normalize', filename)

    def process_output(self, output, filename, file):
        result = json.loads(output)
        if result is {}:
            return None
        else:
            for filelist in result:
                for issue in filelist:
                    yield Result.from_values(origin=self,
                                             message=issue['Message'],
                                             file=filename,
                                             column=issue['Span'][0],
                                             end_column=issue['Span'][1]
                                             )
