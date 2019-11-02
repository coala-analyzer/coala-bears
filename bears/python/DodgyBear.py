import json

from coalib.bearlib.abstractions.Linter import linter
from dependency_management.requirements.PipRequirement import PipRequirement
from coalib.results.Result import Result


@linter(executable='dodgy',
        use_stdout=True,
        use_stderr=False,
        global_bear=True)
class DodgyBear:
    """
    Checks Python files for "dodgy" looking values such
    as AWS secret keys, passwords, SCM diff check-ins,
    SSH keys and any other type of hardcoded secrets.
    """

    LANGUAGES = {'Python'}
    REQUIREMENTS = {PipRequirement('dodgy', '0.1.9')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Security', 'Hardcoded Secret',
                  'SCM Diff Check-in', 'SSH Keys'}
    SEE_MORE = 'https://github.com/landscapeio/dodgy'

    @staticmethod
    def create_arguments(config_file):
        return []

    def process_output(self, output, filename, file):
        """
        Parses JSON stdout call and yields results
        according to the executable output.
        :param output:
            string output from the executable i.e. dodgy
        """
        print(output)
        issues = json.loads(output)
        for issue in issues['warnings']:
            yield Result.from_values(origin=self,
                                     message=issue['message'],
                                     file=issue['path'],
                                     line=issue['line'])
