from coalib.bearlib.languages.Language import Language, UnknownLanguageError
from coalib.bearlib import deprecate_settings
from coalib.bears.LocalBear import LocalBear
from coalib.results.HiddenResult import HiddenResult
from coalib.results.Result import Result, RESULT_SEVERITY
from coalib.results.SourceRange import SourceRange
from coalib.results.AbsolutePosition import AbsolutePosition
from coala_utils.string_processing.Core import unescaped_search_for


class AnnotationBear(LocalBear):
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'

    @deprecate_settings(coalang_dir='coalang_dir')
    def run(self, filename, file, language: str, coalang_dir: str = None):
        """
        Finds out all the positions of strings and comments in a file.
        The Bear searches for valid comments and strings and yields their
        ranges as SourceRange objects in HiddenResults.

        :param language:
            The programming language of the source code.
        :param coalang_dir:
            External directory for coalang file.
        :return:
            One HiddenResult containing a dictionary with keys being 'strings'
            or 'comments' and values being a tuple of SourceRanges pointing to
            the strings and a tuple of SourceRanges pointing to all comments
            respectively. The ranges do include string quotes or the comment
            starting separator but not anything before (e.g. when using
            ``u"string"``, the ``u`` will not be in the source range).
        """
        try:
            lang = Language[language].get_default_version()
        except UnknownLanguageError:
            content = (
                'coalang specification for {} not found.'.format(language))
            yield HiddenResult(self, content)
            return

        string_delimiters = dict(getattr(lang, 'string_delimiters', {}))
        multiline_string_delimiters = dict(
            getattr(lang, 'multiline_string_delimiters', {}))
        multiline_comment_delimiters = dict(
            getattr(lang, 'multiline_comment_delimiters', {}))
        try:
            if isinstance(lang.comment_delimiters, str):
                comment_delimiters = [lang.comment_delimiters]
            else:
                iter(lang.comment_delimiters)
                comment_delimiters = lang.comment_delimiters
        except (AttributeError, TypeError):
            comment_delimiters = ()
        string_ranges = comment_ranges = ()
        try:
            string_ranges, comment_ranges = self.find_annotation_ranges(
                file,
                filename,
                string_delimiters,
                multiline_string_delimiters,
                comment_delimiters,
                multiline_comment_delimiters)

        except NoCloseError as e:
            yield Result(self, str(e), severity=RESULT_SEVERITY.MAJOR,
                         affected_code=(e.code,))

        content = {'strings': string_ranges, 'comments': comment_ranges}
        yield HiddenResult(self, content)

    def find_annotation_ranges(self,
                               file,
                               filename,
                               string_delimiters,
                               multiline_string_delimiters,
                               comment_delimiter,
                               multiline_comment_delimiters):
        """
        Finds ranges of all annotations.

        :param file:
            A tuple of strings, with each string being a line in the file.
        :param filename:
            The name of the file.
        :param string_delimiters:
            A dictionary containing the various ways to  define single-line
            strings in a language.
        :param multiline_string_delimiters:
            A dictionary containing the various ways to define multi-line
            strings in a language.
        :param comment_delimiter:
            A tuple containing the various ways to define single-line
            comments in a language.
        :param multiline_comment_delimiters:
            A dictionary containing the various ways to define multi-line
            comments in a language.
        :return:
            Two tuples first containing a tuple of strings, the second a tuple
            of comments.
        """
        text = ''.join(file)
        strings_range = []
        comments_range = []
        position = 0
        while position <= len(text):

            def get_new_position():
                _range, end_position = self.get_range_end_position(
                    file,
                    filename,
                    text,
                    multiline_string_delimiters,
                    position,
                    self.get_multiline)
                if end_position and _range:
                    strings_range.append(_range)
                    return end_position + 1

                _range, end_position = self.get_range_end_position(
                    file,
                    filename,
                    text,
                    string_delimiters,
                    position,
                    self.get_singleline_strings)
                if end_position and _range:
                    strings_range.append(_range)
                    return end_position + 1

                _range, end_position = self.get_range_end_position(
                    file,
                    filename,
                    text,
                    multiline_comment_delimiters,
                    position,
                    self.get_multiline)
                if end_position and _range:
                    comments_range.append(_range)
                    return end_position + 1

                _range, end_position = self.get_range_end_position(
                    file,
                    filename,
                    text,
                    comment_delimiter,
                    position,
                    self.get_singleline_comment,
                    single_comment=True)
                if end_position and _range:
                    comments_range.append(_range)
                    return end_position + 1

                return position + 1

            position = get_new_position()

        return tuple(strings_range), tuple(comments_range)

    @staticmethod
    def get_range_end_position(file,
                               filename,
                               text,
                               annotations,
                               position,
                               func,
                               single_comment=False):
        _range = end_position = None
        for annotation in annotations:
            if text[position:].startswith(annotation):
                if single_comment:
                    ret_val = func(file,
                                   filename,
                                   text,
                                   annotation,
                                   position)
                else:
                    ret_val = func(file,
                                   filename,
                                   text,
                                   annotation,
                                   annotations[annotation],
                                   position)
                if ret_val:
                    _range, end_position = ret_val[0], ret_val[1]

        return _range, end_position

    @staticmethod
    def get_multiline(file,
                      filename,
                      text,
                      annotation_start,
                      annotation_end,
                      position):
        """
        Gets sourcerange and end position of an annotation that can span
        multiple lines.

        :param file:
            A tuple of strings, with each string being a line in the file.
        :param filename:
            The name of the file.
        :param annotation_start:
            The string specifying the start of the annotation.
        :param annotation_end:
            The string specifying the end of the annotation.
        :param position:
            An integer identifying the position where the annotation started.
        :return:
            A SourceRange object holding the range of the multi-line annotation
            and the end_position of the annotation as an integer.
        """
        end_end = get_end_position(annotation_end,
                                   text,
                                   position + len(annotation_start) - 1)
        if end_end == -1:
            _range = SourceRange.from_absolute_position(
                filename,
                AbsolutePosition(file, position))
            raise NoCloseError(annotation_start, _range)

        return (SourceRange.from_absolute_position(
                    filename,
                    AbsolutePosition(file, position),
                    AbsolutePosition(file, end_end)),
                end_end)

    @staticmethod
    def get_singleline_strings(file,
                               filename,
                               text,
                               string_start,
                               string_end,
                               position):
        """
        Gets sourcerange of a single-line string and its end position.

        :param file:
            A tuple of strings, with each string being a line in the file.
        :param filename:
            The name of the file.
        :param string_start:
            The string which specifies how a string starts.
        :param string_end:
            The string which specifies how a string ends.
        :position:
            An integer identifying the position where the string started.
        :return:
            A SourceRange object identifying the range of the single-line
            string and the end_position of the string as an integer.
        """
        end_position = get_end_position(string_end,
                                        text,
                                        position + len(string_start) - 1)
        newline = get_end_position('\n', text, position)
        if newline == -1:
            newline = len(text)
        if end_position == -1:
            _range = SourceRange.from_absolute_position(
                filename,
                AbsolutePosition(file, position))
            raise NoCloseError(string_start, _range)
        if newline > end_position:
            return (SourceRange.from_absolute_position(
                        filename,
                        AbsolutePosition(file, position),
                        AbsolutePosition(file, end_position)),
                    end_position)

    @staticmethod
    def get_singleline_comment(file, filename, text, comment, position):
        """
        Gets Sourcerange of a single-line comment where the start is the
        start of comment and the end is the end of line.

        :param file:
            A tuple of strings, with each string being a line in the file.
        :param filename:
            The name of the file.
        :param comment:
            The string which specifies the comment.
        :position:
            An integer identifying the position where the string started.
        :return:
            A SourceRange object identifying the range of the single-line
            comment and the end_position of the comment as an integer.
        """
        end_position = get_end_position('\n',
                                        text,
                                        position + len(comment) - 1)
        if end_position == -1:
            end_position = len(text) - 1
        return (SourceRange.from_absolute_position(
                    filename,
                    AbsolutePosition(file, position),
                    AbsolutePosition(file, end_position)),
                end_position)


def get_end_position(end_marker, text, position):
    try:
        end_match = next(unescaped_search_for(end_marker, text[position + 1:]))
        end_position = position + end_match.span()[1]
    except StopIteration:
        end_position = -1

    return end_position


class NoCloseError(Exception):

    def __init__(self, annotation, code):
        Exception.__init__(self, annotation + ' has no closure')
        self.code = code
