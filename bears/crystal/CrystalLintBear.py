from coalib.bearlib.abstractions.Linter import linter
from dependency_management.requirements.DistributionRequirement import (
    DistributionRequirement)


@linter(executable='ameba',
        output_format='regex',
        strip_ansi=True,
        output_regex=r'.+:(?P<line>\d+):(?P<column>\d+)\n'
                     r'.+(?P<origin>[A-Za-z]+): (?P<message>.*)')
class CrystalLintBear:
    """
    Checks the code with ``ameba``.

    It enforces a consistent Crystal code style
    <https://crystal-lang.org/docs/conventions/coding_style.html>, also catches
    code smells and wrong code constructions.
    """
    LANGUAGE = {'Crystal'}
    REQUIREMENTS = {DistributionRequirement(brew='ameba')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Syntax', 'Unused Code', 'Formatting'}
    SEE_MORE = 'https://github.com/veelenga/ameba'

    @staticmethod
    def create_arguments(filename, file, config_file):
        return filename,
