from shutil import which
from dependency_management.requirements.AnyOneOfRequirements import (
    AnyOneOfRequirements)
from dependency_management.requirements.ExecutableRequirement import (
    ExecutableRequirement)

from coalib.bearlib.abstractions.Linter import linter
from coalib.bearlib import deprecate_settings
from coala_utils.param_conversion import negate

_executable = which('run.sh') or which('pmd')


@linter(_executable or 'pmd', output_format='regex',
        output_regex=r'.+:(?P<line>.+):(?P<message>.*)')
class JavaPMDBear:
    """
    Check Java code for possible issues like potential bugs, dead code or too
    complicated expressions.

    More information is available at
    <http://pmd.github.io/pmd-5.4.1/pmd-java/rules/index.html>.
    """

    LANGUAGES = {'Java'}
    REQUIREMENTS = {
        AnyOneOfRequirements(
            [ExecutableRequirement('pmd'),
             ExecutableRequirement('run.sh'),
             ]
        ),
    }
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Code Simplification', 'Unreachable Code', 'Smell',
                  'Duplication'}

    @staticmethod
    @deprecate_settings(allow_unnecessary_code=('check_unnecessary', negate),
                        allow_unused_code=('check_unused', negate))
    def create_arguments(filename, file, config_file,
                         pmd_config: str = None,
                         check_best_practices: bool = True,
                         check_braces: bool = True,
                         check_clone_implementation: bool = True,
                         check_code_size: bool = True,
                         check_comments: bool = False,
                         check_controversial: bool = False,
                         check_design: bool = False,
                         check_imports: bool = True, check_naming: bool = True,
                         check_optimizations: bool = False,
                         check_strings: bool = False,
                         allow_unnecessary_code: bool = False,
                         allow_unused_code: bool = False):
        """
        :param pmd_config:
            Allows custom rulesets other than default.
        :param check_best_practices:
            Checks for best practices.
        :param check_braces:
            Checks for the right use of braces.
        :param check_clone_implementation:
            Checks for the right implementation of the ``clone()`` function.
        :param check_code_size:
            Checks for large or complicated code constructs.
        :param check_comments:
            Checks comments for length, content and placement.
        :param check_controversial:
            Does various checks that are considered controversial.
        :param check_design:
            Checks for optimal code implementations. Alternate approaches
            are suggested.
        :param check_imports:
            Checks for duplicate and unused imports.
        :param check_naming:
            Checks the names of identifiers against some rules.
        :param check_optimizations:
            Checks for best pratices regarding optimization.
        :param check_strings:
            Checks for String, StringBuffer and StringBuilder instances.
        :param allow_unnecessary_code:
            Allows unnecessary code.
        :param allow_unused_code:
            Allows unused code.
        """
        if pmd_config:
            rules = pmd_config
        else:
            options = {
                'java-basic': check_best_practices,
                'java-braces': check_braces,
                'java-clone': check_clone_implementation,
                'java-codesize': check_code_size,
                'java-comments': check_comments,
                'java-controversial': check_controversial,
                'java-design': check_design,
                'java-imports': check_imports,
                'java-naming': check_naming,
                'java-optimizations': check_optimizations,
                'java-strings': check_strings,
                'java-unnecessary': not allow_unnecessary_code,
                'java-unusedcode': not allow_unused_code}
            rules = ','.join(key for key in options if options[key])

        executable = tuple(['pmd'] if _executable.endswith('run.sh') else [])
        arguments = '-R', rules, '-d', filename, '-f', 'text'
        return executable + arguments
