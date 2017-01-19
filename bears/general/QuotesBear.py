from coalib.bears.LocalBear import LocalBear
from bears.general.AnnotationBear import AnnotationBear
from coalib.results.Diff import Diff
from coalib.results.HiddenResult import HiddenResult
from coalib.results.Result import Result


class QuotesBear(LocalBear):

    BEAR_DEPS = {AnnotationBear}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Formatting'}

    def correct_single_line_str(self, filename, file, sourcerange,
                                preferred_quotation):
        """
        Corrects a given single line string assuming it does not use the
        preferred quotation. If the preferred quotation mark is used inside the
        string, no correction will be made.

        This function will yield one or no Result objects.

        :param filename:
            The filename of the file to correct the line in.
        :param file:
            The file contents as list of lines.
        :param sourcerange:
            The sourcerange indicating where to find the string.
        :param preferred_quotation:
            ``'`` or ``"`` respectively.
        """
        str_contents = file[sourcerange.start.line - 1][
                       sourcerange.start.column:sourcerange.end.column-1]

        if preferred_quotation in str_contents:
            return

        before = file[sourcerange.start.line - 1][:sourcerange.start.column-1]
        after = file[sourcerange.end.line - 1][sourcerange.end.column:]

        replacement = (before + preferred_quotation + str_contents +
                       preferred_quotation + after)

        diff = Diff(file)
        diff.change_line(sourcerange.start.line,
                         file[sourcerange.start.line - 1],
                         replacement)
        yield Result(self, 'You do not use the preferred quotation marks.',
                     diff.affected_code(filename), diffs={filename: diff})

    def run(self, filename, file, dependency_results,
            preferred_quotation: str='"'):
        """
        Checks and corrects your quotation style.

        For all single line strings, this bear will correct the quotation to
        your preferred quotation style if that kind of quote is not included
        within the string. Multi line strings are not supported.

        :param preferred_quotation: Your preferred quotation character, e.g.
                                    ``"`` or ``'``.
        """
        if not isinstance(dependency_results[AnnotationBear.name][0],
                          HiddenResult):
            return
        if isinstance(dependency_results[AnnotationBear.name][0].contents,
                      str):
            self.err(dependency_results[AnnotationBear.name][0].contents)
            return

        dep_contents = dependency_results[AnnotationBear.name][0].contents
        annotation_dict = {}
        s_a = 'singleline strings'
        s_b = 'multiline strings'
        annotation_dict['strings'] = (dep_contents[s_a] +
                                      dep_contents[s_b])
        ranges = annotation_dict['strings']

        for string_range in ranges:
            temp_range = string_range.full_range
            if (file[temp_range.start.line-1][temp_range.start.column-1] ==
                    preferred_quotation):
                continue

            if temp_range.start.line == temp_range.end.line:
                yield from self.correct_single_line_str(
                    filename, file, temp_range, preferred_quotation)
