import logging

from coalib.bears.LocalBear import LocalBear
from coalib.results.Result import Result
from coalib.bearlib.languages.Language import Language, UnknownLanguageError


class LineContinuationBear(LocalBear):
    def run(self,
            filename,
            file,
            language,
            ignore_with: bool = False,
            ):
        """
        It is a generic bear which will look for any lines which
        end with the explicit use of line continuation operators,
        which is considered as a bad practice. The solution
        would be to use implicit type of line continuation methods.

        Note that this requires the coalang to know the tokens
        used for line continuation and hence any language not
        having the line continuation attribute will result in an error.

        :param filename:
            Name of the file that needs to be checked.
        :param file:
            File that needs to be checked in the form of a list of strings.
        :param language:
            Language to be used for finding the line continuation tokens.
        :param ignore_with:
            Ignore line continuation operators in with statements.
        """
        try:
            lang = Language[language]
            line_continuation = lang.get_default_version().line_continuation
        except (UnknownLanguageError, AttributeError):
            logging.error('Language {} is not yet supported.'.format(language))
            return

        for line_number, line in enumerate(file):
            if len(line) > 1 and not ignore_with:
                if line[-2] in line_continuation:
                    if '>>> from ' in line:
                        continue
                    yield Result.from_values(
                        origin=self,
                        message='Explicit line continuation is not allowed.',
                        file=filename,
                        line=line_number + 1,
                        column=len(line) - 1,
                        end_line=line_number + 1,
                        end_column=len(line),
                    )
            elif len(line) > 1 and ignore_with:
                if line[-2] in line_continuation and line[:5] != 'with ':
                    yield Result.from_values(
                        origin=self,
                        message='Explicit line continuation is not allowed.',
                        file=filename,
                        line=line_number + 1,
                        column=len(line) - 1,
                        end_line=line_number + 1,
                        end_column=len(line),
                    )
