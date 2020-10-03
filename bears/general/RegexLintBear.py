import re

from sarge import run, Capture

from bears.general.AnnotationBear import AnnotationBear
from coalib.bears.LocalBear import LocalBear
from dependency_management.requirements.PipRequirement import PipRequirement


class RegexLintBear(LocalBear):
    LANGUAGES = {'All'}
    REQUIREMENTS = {PipRequirement('regexlint', '1.6')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Formatting'}
    BEAR_DEPS = {AnnotationBear}

    def run(self, filename, file, dependency_results):
        """
        Bear for linting regex through regexlint.

        :param dependency_results:
            Results given by the AnnotationBear.
        """
        annotation_dict = dependency_results[AnnotationBear.name][0].contents
        for src_range in annotation_dict['strings']:
            src_line = src_range.affected_source({filename: file})[0]
            regex = src_line[src_range.start.column:src_range.end.column-1]
            try:
                re.compile(regex)
            except re.error:
                continue
            out = run('regexlint --regex "{}"'.format(regex),
                      stdout=Capture()).stdout.text
            if out[-3:-1] == 'OK':
                continue
            yield Result.from_values(
                origin=self,
                message=out,
                file=filename,
                line=src_range.start.line,
                column=src_range.start.column,
                end_line=src_range.end.line,
                end_column=src_range.end.column,
            )
