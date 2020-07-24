from coalib.bearlib.abstractions.Linter import linter


@linter(executable='linter-prolog', output_format="regex",
        output_regex=r'(\w+):\s+(?p<file_name>[^\:]+):(?p<line>(\d+)):'
                     r'(?p<column>((\d+):))?\s+(.*)')
class PrologLinterBear:
    """
    Check prolog code to keep it clean and readable.

    More information is available at <https://github.com/wysiib/linter-prolog>.
    """

    LANGUAGES = {"Prolog"}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Syntax', 'Formatting'}

    @staticmethod
    def create_arguments(filename, file, config_file):
        return filename,
