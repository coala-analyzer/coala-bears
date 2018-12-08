from coalib.bearlib.abstractions.Linter import linter
from dependency_management.requirements.GoRequirement import GoRequirement


@linter(executable='goreturns',
        use_stdin=True,
        output_format='corrected',
        result_message='Imports or returns need to be added/removed.')
class GoReturnsBear:  # pragma nt: no cover
    """
    Proposes corrections of Go code using ``goreturns``.
    """
    LANGUAGES = {'Go'}
    REQUIREMENTS = {GoRequirement(
        package='github.com/sqs/goreturns', flag='-u')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_FIX = {'Security'}

    @staticmethod
    def create_arguments(filename, file, config_file):
        return ()
