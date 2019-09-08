import requests
from urllib.parse import urlparse

from bears.general.URLBear import URLBear, LINK_CONTEXT

from coalib.bears.LocalBear import LocalBear
from dependency_management.requirements.PipRequirement import PipRequirement
from coalib.bearlib import deprecate_settings
from coalib.results.HiddenResult import HiddenResult
from coalib.results.Result import Result
from coalib.settings.Setting import typed_dict
from coala_utils.decorators import (enforce_signature, generate_ordering,
                                    generate_repr)


@generate_repr(('id', hex),
               'origin',
               'affected_code',
               'message',
               'link',
               'http_status_code',
               'link_context',
               'head_response')
@generate_ordering('affected_code',
                   'link',
                   'http_status_code',
                   'link_context',
                   'head_response',
                   'contents',
                   'severity',
                   'confidence',
                   'origin',
                   'message_base',
                   'message_arguments',
                   'aspect',
                   'additional_info',
                   'debug_msg')
class URLHeadResult(HiddenResult):

    @enforce_signature
    def __init__(self, origin, affected_code,
                 link: str,
                 head_response: (requests.models.Response, Exception),
                 link_context: LINK_CONTEXT):

        http_status_code = (head_response.status_code if
                            isinstance(head_response,
                                       requests.models.Response)
                            else None)
        Result.__init__(self, origin,
                        '%s responds with HTTP %s' % (link, http_status_code),
                        affected_code)

        self.contents = [affected_code[0].start.line, link, http_status_code,
                         link_context]
        self.link = link
        self.http_status_code = http_status_code
        self.link_context = link_context
        self.head_response = head_response


class URLHeadBear(LocalBear):
    BEAR_DEPS = {URLBear}
    DEFAULT_TIMEOUT = 15
    LANGUAGES = {'All'}
    REQUIREMENTS = {PipRequirement('requests', '2.12')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Documentation'}

    # DNS IP by Cloudfare
    check_connection_url = 'https://1.1.1.1/'

    @classmethod
    def check_prerequisites(cls):
        head_resp = cls.get_head_response(
            cls.check_connection_url, cls.DEFAULT_TIMEOUT)
        return ('You are not connected to the internet.'
                if isinstance(head_resp, Exception) else True)

    @staticmethod
    def get_head_response(url, timeout):
        try:
            headers = {'User-Agent': (
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/70.0.3538.77 Safari/537.36')}
            head_resp = requests.head(url, allow_redirects=False,
                                      headers=headers, timeout=timeout)
            return head_resp
        except requests.exceptions.RequestException as exc:
            return exc

    @deprecate_settings(network_timeout=('timeout', lambda t: {'*': t}))
    def run(self, filename, file, dependency_results=dict(),
            network_timeout: typed_dict(str, int, DEFAULT_TIMEOUT) = dict(),
            ):
        """
        Find links in any text file and tells its head response and
        status code.

        Warning: This bear will make HEAD requests to all URLs mentioned in
        your codebase, which can potentially be destructive. As an example,
        this bear would naively just visit the URL from a line that goes like
        `do_not_ever_open = 'https://api.acme.inc/delete-all-data'` wiping out
        all your data.

        :param network_timeout: A dict mapping URLs and timeout to be
                                used for that URL. All the URLs that have
                                the same host as that of URLs provided
                                will be passed that timeout. It can also
                                contain a wildcard timeout entry with key
                                '*'. The timeout of all the websites not
                                in the dict will be the value of the key
                                '*'.
        :param link_ignore_regex: A regex for urls to ignore.
        :param link_ignore_list: Comma separated url globs to ignore
        """
        network_timeout = {urlparse(url).netloc
                           if not url == '*' else '*': timeout
                           for url, timeout in network_timeout.items()}

        for result in dependency_results.get(URLBear.name, []):
            host = urlparse(result.link).netloc
            head_resp = self.get_head_response(
                result.link,
                network_timeout.get(host)
                if host in network_timeout
                else network_timeout.get('*')
                if '*' in network_timeout
                else URLHeadBear.DEFAULT_TIMEOUT)

            yield URLHeadResult(self, result.affected_code, result.link,
                                head_resp, result.link_context)
