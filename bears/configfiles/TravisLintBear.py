import requests

from coalib.bearlib.abstractions.Linter import linter

from dependency_management.requirements.GemRequirement import GemRequirement


@linter(executable='travis',
        output_format='regex',
        output_regex=r'\[x\]\s+(?P<message>.+)')
class TravisLintBear:
    """
    A validator for your ``.travis.yml`` that attempts to reduce common build
    errors such as:

    - invalid YAML
    - missing language key
    - unsupported runtime versions of Ruby, PHP, OTP, etc.
    - deprecated features or runtime aliases
    """

    LANGUAGES = {'YAML'}
    REQUIREMENTS = {GemRequirement('travis', '1.8.8')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Formatting', 'Syntax'}
    SEE_MORE = 'https://docs.travis-ci.com/user/travis-lint'

    @classmethod
    def check_prerequisites(cls):
        base_check = super().check_prerequisites()
        if base_check is not True:
            return base_check

        check_connection_url = 'https://travis-ci.org/'
        url_status = cls.get_url_status(check_connection_url)

        try:
            if url_status is None:
                return 'You are not connected to the internet.'
            else:
                url_status.raise_for_status()
                return True
        except requests.exceptions.HTTPError:
            return 'Failed to establish a connection to {}.'.format(
                check_connection_url)

    @staticmethod
    def get_url_status(url):
        try:
            return requests.head(url, allow_redirects=False)
        except requests.exceptions.RequestException:
            return None

    @staticmethod
    def create_arguments(filename, file, config_file):
        return 'lint', filename
