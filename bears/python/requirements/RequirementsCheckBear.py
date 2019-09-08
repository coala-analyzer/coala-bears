import os.path

from coalib.bears.GlobalBear import GlobalBear
from coalib.results.Result import Result, RESULT_SEVERITY
from sarge import capture_both

from dependency_management.requirements.PipRequirement import PipRequirement


class RequirementsCheckBear(GlobalBear):
    """
    The bear to check and find any conflicting pip dependencies.
    """
    LANGUAGES = {
        'Python Requirements',
        'Python 2 Requirements',
        'Python 3 Requirements',
    }
    REQUIREMENTS = {PipRequirement('pip-tools', '3.8.0')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'

    def run(self, require_files: tuple):
        """
        :param require_files:
            Tuple of requirements files.
        """
        data = ''
        orig_file = ''

        for require_file in require_files:
            if not os.path.isfile(os.path.abspath(require_file)):
                raise ValueError('The file \'{}\' doesn\'t exist.'
                                 .format(require_file))

            with open(require_file) as _file:
                content = _file.read()
                if not orig_file:
                    orig_file = content
                else:
                    data += content

        with open(require_files[0], 'a+') as temp_file:
            temp_file.write(data)

        out = capture_both('pip-compile {} -r -n --no-annotate --no-header '
                           '--no-index --allow-unsafe'.format(require_files[0]))

        if out.stderr.text and not out.stdout.text:
            pip_warning = 'Cache entry deserialization failed, entry ignored'
            lines = out.stderr.text.splitlines()
            lines = [line for line in lines if line not in pip_warning]
            yield Result(self,
                         message=lines[0],
                         severity=RESULT_SEVERITY.MAJOR,
                         )

        with open(require_files[0], 'w+') as _file:
            _file.write(orig_file)
