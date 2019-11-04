import json
from inspect import getfullargspec
from functools import lru_cache

from decorator import FunctionMaker

from coalib.bearlib.abstractions.Linter import linter
from coalib.misc.Shell import run_shell_command
from coalib.results.Diff import Diff
from coalib.results.Result import Result
from coalib.results.TextRange import TextRange


class Rulified:
    """
    Decorator for static :meth:`PSScriptAnalyzerBear.create_arguments`.

    Lazily creates a wrapper function defining all PSScriptAnalyzer rules as
    function arguments with `bool` annotation and ``True`` as default, so that
    they get implicitly turned into Bear settings:

    >>> class Bear:
    ...     @Rulified
    ...     def func(arg, **rules):
    ...         pass

    >>> argspec = getfullargspec(Bear.func)
    >>> argspec.args
    ['arg', ...'PSAlignAssignmentStatement'...]
    >>> argspec.annotations
    {...'PSAlignAssignmentStatement': <class 'bool'>...}
    >>> argspec.defaults
    (...True...)

    Implemented as descriptor with all magic in :meth:`.__get__`.
    """

    def __init__(self, func):
        self.func = func
        self.argspec = getfullargspec(func)

    @staticmethod
    @lru_cache()
    def rules():
        """
        Get all available rule names from PSScriptAnalyzer.
        """
        result = run_shell_command([
            'powershell', '-Command',
            'Get-ScriptAnalyzerRule '
            '| Select-Object -ExpandProperty RuleName'])
        if result.code:
            raise RuntimeError(
                'Failed to run powershell -Command Get-ScriptAnalyzerRule{}'
                .format(result[1] and ':\n\n' + result[1]))
        return result[0].split()

    @lru_cache()
    def __get__(self, obj, owner):
        """
        Create the external ``create_arguments`` caller function for
        :class:`PSScriptAnalyzerBear`, wrapping :meth:`self.create_arguments`,
        and defining all PSScriptAnalyzer rules as boolean function arguments
        with default ``True`` values.
        """
        rules = self.rules()
        caller = FunctionMaker.create(
            '{}({}, {})'
            .format(self.func.__name__, ', '.join(self.argspec.args),
                    # unfortunately annotations and defaults don't seem to be
                    # recognized by FuncionMaker ...
                    # ', '.join('{}: bool=False'.format(name)
                    ', '.join('{}'.format(name) for name in rules)),
            'return func({}, {})'
            .format(', '.join(self.argspec.args),
                    ', '.join('{}={}'.format(name, name)
                              for name in rules)),
            {'func': self.func},
            doc=self.func.__doc__, __module__ = __name__)
        # ... so they need to be implicitly added afterwards
        caller.__annotations__ = {name: bool for name in rules}
        caller.__defaults__ = (True, ) * len(rules)
        return caller


@linter(executable='powershell')
class PSScriptAnalyzerBear:
    """
    Check the quality of PowerShell modules and scripts with PSScriptAnalyzer.

    PSScriptAnalyzer is run with all default rules enabled. Rules can be
    disabled by giving them as Bear settings with falsy values.
    """

    LANGUAGES = {'PowerShell'}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = CAN_FIX = {'Syntax', 'Formatting', 'Smell'}
    SEE_MORE = 'https://github.com/PowerShell/PSScriptAnalyzer'

    @Rulified
    def create_arguments(filename, file, config_file, **rules):
        """
        Define a ``powershell -Command`` for running ``Invoke-ScriptAnalyzer``
        cmdlet on `filename` and converting result to JSON.

        All given rules with ``False`` value will be explicitly excluded.
        """
        disable = [name for name, value in rules.items() if not value]
        ruleparam = disable and '-ExcludeRule ' + ', '.join(disable) or ''
        return ('-Command',
                'Invoke-ScriptAnalyzer -Path "{}" -IncludeDefaultRules {} '
                '| ConvertTo-Json -Depth 3'
                .format(filename, ruleparam))

    def process_output(self, output, filename, file):
        violations = output and json.loads(output)
        if isinstance(violations, dict):
            # ==> only one violation
            violations = [violations]
        for item in violations or ():
            location = item['Extent']
            diff = None  # for the case that no correction is found below
            fixes = item['SuggestedCorrections']
            if fixes:
                diff = Diff(list(file))
                for fix in fixes:
                    diff.replace(TextRange.from_values(
                        int(fix['StartLineNumber']),
                        int(fix['StartColumnNumber']),
                        int(fix['EndLineNumber']),
                        int(fix['EndColumnNumber'])
                    ), fix['Text'])
            yield Result.from_values(
                origin='{} ({})'.format(
                    type(self).__name__, item['RuleName']),
                message=item['Message'],
                file=filename,
                line=int(location['StartLineNumber']),
                column=int(location['StartColumnNumber']),
                end_line=int(location['EndLineNumber']),
                end_column=int(location['EndColumnNumber']),
                diffs={filename: diff} if diff else None)
