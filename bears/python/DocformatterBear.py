from coalib.bearlib.abstractions.Linter import linter
from dependency_management.requirements.PipRequirement import PipRequirement


@linter(executable='docformatter',
        output_format='unified-diff',
        diff_distance=-1,
        prerequisite_check_command=('docformatter', '--version'),
        prerequisite_check_fail_message='docformatter is not installed. Run '
                                        '`pip install docformatter` to install'
                                        'docformatter.',
        result_message='The documentation string does not meet PEP 257 '
                       'conventions.')
class DocformatterBear:
    """
    Check the docstrings according to PEP 257 conventions.

    More information available at https://github.com/myint/docformatter
    """

    LANGUAGES = {'Python', 'Python 2', 'Python 3'}
    REQUIREMENTS = {PipRequirement('docformatter')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_FIX = {'Formatting', 'Documentation'}

    @staticmethod
    def create_arguments(filename, file, config_file,
                         wrap_summaries_length: int=79,
                         wrap_descriptions_length: int=72,
                         no_blank: bool=False,
                         pre_summary_newline: bool=False,
                         make_summary_multi_line: bool=False,
                         force_wrap: bool=False):
        """
        :param wrap_summaries_length:
            Wrap long summary lines at this length.
        :param wrap_descriptions_length:
            Wrap descriptions at this length.
        :param no_blank:
            Do not add blank line after description.
        :param pre_summary_newline:
            Add a newline before the summary of a multi-line
            docstring.
        :param make_summary_multi_line:
            Add a newline before and after the summary of a one-
            line docstring.
        :param force_wrap:
            Force descriptions to be wrapped even if it may result
            in a mess.
        """
        options = ('--wrap-summaries', str(wrap_summaries_length),
                   '--wrap-descriptions', str(wrap_descriptions_length))
        options += (('--no-blank',) if no_blank else ())
        options += (('--pre-summary-newline',) if pre_summary_newline else ())
        options += (('--make-summary-multi-line',)
                    if make_summary_multi_line else ())
        options += (('--force-wrap',) if force_wrap else ())
        return options + (filename,)
