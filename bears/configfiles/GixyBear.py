import json

from coalib.bearlib.abstractions.Linter import linter
from dependency_management.requirements.PipRequirement import PipRequirement
from coalib.results.RESULT_SEVERITY import RESULT_SEVERITY
from coalib.results.Result import Result


@linter(executable='gixy')
class GixyBear:
    """
    A wrapper for coala around Gixy

    see <https://github.com/yandex/gixy> for more information about the tool
    """
    REQUIREMENTS = {PipRequirement('gixy', '0.1.*')}

    severity_map = {'HIGH': RESULT_SEVERITY.MAJOR,
                    'MEDIUM': RESULT_SEVERITY.NORMAL,
                    'LOW': RESULT_SEVERITY.INFO}

    @staticmethod
    def create_arguments(filename, file, config_file):
        return ('--format=json', filename)

    def process_output(self, output, filename, file):
        output = json.loads(output) if output else []
        for issue in output:
            yield Result.from_values(
                origin=self,
                message=issue['summary'],
                severity=self.severity_map[issue['severity']],
                file=filename)
