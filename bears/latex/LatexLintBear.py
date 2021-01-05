from coalib.bearlib.abstractions.Linter import linter
from dependency_management.requirements.DistributionRequirement import (
    DistributionRequirement)


@linter(executable='chktex',
        output_format='regex',
        output_regex=r'(?P<severity>Error|Warning) \d+ in .+ line '
                     r'(?P<line>\d+): (?P<message>.*)')
class LatexLintBear:
    """
    Checks the code with ``chktex``.
    """
    LANGUAGES = {'Tex'}
    REQUIREMENTS = {DistributionRequirement('chktex', zypper='texlive-chktex')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Syntax', 'Formatting'}

    @staticmethod
    def create_arguments(filename, file, config_file):
        return (
            '--format',
            '%k %n in {0} line %l: %m'.format(filename),
            filename,
        )
