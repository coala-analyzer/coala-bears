import os.path

from coalib.bears.GlobalBear import GlobalBear
from dependency_management.requirements.PythonImportRequirement import (
                PythonImportRequirement)
from coalib.results.Result import Result


class PyromaBear(GlobalBear):
    LANGUAGES = {'Python', 'Python 3'}
    REQUIREMENTS = {PythonImportRequirement('pyroma',
                                            '2.2.0',
                                            ['pyroma.projectdata.get_data',
                                             'pyroma.ratings.rate'])}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'

    def run(self):
        """
        Checks for Python packaging best practices using `pyroma`.

        Pyroma rhymes with aroma, and is a product aimed at giving a rating of
        how well a Python project complies with the best practices of the
        Python packaging ecosystem, primarily PyPI, pip, Distribute etc,
        as well as a list of issues that could be improved.

        See <https://bitbucket.org/regebro/pyroma/> for more information.
        """
        pyroma = list(self.__class__.REQUIREMENTS)[0]
        pyroma.is_importable()
        setup_files = [setup_file for setup_file in self.file_dict
                       if os.path.basename(setup_file) == 'setup.py']

        if not setup_files:
            yield Result(self, 'Your package does'
                         ' not contain a setup file.')
        else:
            for setup_file in setup_files:
                data = pyroma.get_data(os.path.dirname(setup_file))
                rating = pyroma.rate(data)
                messages = rating[1]

                for message in messages:
                    yield Result.from_values(origin=self,
                                             message=message,
                                             file=setup_file)
