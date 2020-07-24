from coalib.bearlib.abstractions.Linter import linter
from dependency_management.requirements.PipRequirement import PipRequirement
from coalib.settings.Setting import path
from coalib.settings.Setting import typed_list


@linter(executable='cmakelint',
        output_format='regex',
        output_regex=r'.+:(?P<line>\d+): (?P<message>.*)')
class CMakeLintBear:
    """
    Check CMake code for syntactical or formatting issues.

    For more information consult <https://github.com/richq/cmake-lint>.
    """
    LANGUAGES = {'CMake'}
    REQUIREMENTS = {PipRequirement('cmakelint', '1.3')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Syntax', 'Formatting'}

    @staticmethod
    def create_arguments(filename, file, config_file,
                         filters: typed_list(str) = [],
                         cmakelint_config: path = '',
                         ):
        """
        :param filters: The filter to be applied on cmake file.
        :param cmakelint_config: The location of the cmakelintrc config file.
        """
        args = ()
        if cmakelint_config:
            args += ('--config=' + cmakelint_config,)
        if filters:
            args += ('--filter=' + ','.join(filters),)

        return args + (filename,)
