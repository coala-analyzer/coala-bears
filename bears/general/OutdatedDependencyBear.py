from coalib.bears.LocalBear import LocalBear
from coalib.results.Result import Result
from dependency_management.requirements.PipRequirement import PipRequirement
from distutils.version import LooseVersion
from sarge import run, Capture


class OutdatedDependencyBear(LocalBear):
    LANGUAGES = {'All'}
    REQUIREMENTS = {PipRequirement('pip-tools', '3.8.0')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'

    def run(self, filename, file, requirement_type: str,):
        """
        Checks for the outdated dependencies in a project.

        :param requirement_type:
            One of the requirement types supported by coala's package manager.
        :param requirements_file:
            Requirements file can be specified to look for the requirements.
        """
        requirement_types = ['pip']

        if requirement_type not in requirement_types:
            raise ValueError('Currently the bear only supports {} as '
                             'requirement_type.'
                             .format(', '.join(
                                 _type for _type in requirement_types)))

        message = ('The requirement {} with version {} is not '
                   'pinned to its latest version {}.')

        out = run('pip-compile -n --allow-unsafe {}'.format(filename),
                  stdout=Capture())

        data = [line for line in out.stdout.text.splitlines()
                if '#' not in line and line]

        for requiremenent in data:
            package, version = requiremenent.split('==')
            pip_requirement = PipRequirement(package)
            latest_ver = pip_requirement.get_latest_version()
            line_number = [num for num, line in enumerate(file, 1)
                           if package in line.lower()]

            if LooseVersion(version) < LooseVersion(latest_ver):
                yield Result.from_values(origin=self,
                                         message=message.format(
                                                    package,
                                                    version,
                                                    latest_ver),
                                         file=filename,
                                         line=line_number[0],
                                         end_line=line_number[0],
                                         )
