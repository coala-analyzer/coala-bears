from dependency_management.requirements.GemRequirement import GemRequirement
from dependency_management.requirements.GoRequirement import GoRequirement
from coalib.bearlib.abstractions.Linter import linter


@linter(executable='maintainer',
        global_bear=True,
        output_format='regex',
        output_regex=r'(?P<severity>Error|Warning) \d+ in .+ line '
                     r'(?P<line>\d+): (?P<message>.*)'
        )
class AuthorsBear:

    LANGUAGES = {'Community', 'Maintainer'}
    REQUIREMENTS = {GoRequirement(package='golang.org/gaocegege/maintainer',
                                  flag='-u')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'

    @staticmethod
    def create_arguments(config_file):
        return ('contributor', )
