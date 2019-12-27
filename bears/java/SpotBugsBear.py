from coalib.bearlib.abstractions.Linter import linter
from dependency_management.requirements.DistributionRequirement import (
    DistributionRequirement)


@linter(executable='java',
        output_format='regex')
class SpotBugsBear:
    """
    Uses ``spotbugs`` to find possible bugs in Java programs by looking for
    instances of bug patterns or code instances that are likely to be errors.
    """
    LANGUAGES = {'Java'}
    REQUIREMENTS = {DistributionRequirement(apt_get='default-jre')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Bugs'}
    SEE_MORE = 'https://spotbugs.github.io/'

    def setup_dependencies(self):
        type(self).spotbugs_jar_file = self.download_cached_file(
            '')
