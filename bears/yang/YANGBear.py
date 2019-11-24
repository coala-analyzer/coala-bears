from os.path import dirname

from coala_utils.decorators import enforce_signature
from coalib.bearlib.abstractions.Linter import linter
from coalib.settings.Setting import typed_list
from dependency_management.requirements.PipRequirement import PipRequirement


@linter(executable='pyang',
        use_stderr=True,
        output_format='regex',
        output_regex=r'.*:(?P<line>\d+):\s*(?P<message>.*)')
class YANGBear:
    """
    Lints `YANG <https://en.wikipedia.org/wiki/YANG>`__ model files using
    ``pyang``.

    From `RFC 7950 <https://tools.ietf.org/html/rfc7950>`__:

    _"YANG is a data modeling language used to model configuration data,
    state data, Remote Procedure Calls, and notifications for network
    management protocols."_
    """
    LANGUAGES = {'YANG'}
    REQUIREMENTS = {PipRequirement('pyang', '1.7.1')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Formatting', 'Smell', 'Syntax'}
    SEE_MORE = 'https://pypi.python.org/pypi/pyang'

    @staticmethod
    @enforce_signature
    def create_arguments(filename, file, config_file,
                         yang_search_paths: typed_list(str)=None):
        """
        :param yang_search_paths:
           A list of search directories for YANG includes. The directory of
           the linted file is always searched by default.
        """
        # At least the file's own directory should be always explicitly
        # defined as search path, since it's not implicitly searched by pyang
        yang_search_paths = [dirname(filename)] + (yang_search_paths or [])
        return '-p', ';'.join(yang_search_paths), '--lint', filename
