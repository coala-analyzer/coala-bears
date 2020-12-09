import requests

from difflib import SequenceMatcher

from bears.general.URLHeadBear import URLHeadBear
from coalib.results.Diff import Diff
from coalib.bears.LocalBear import LocalBear
from dependency_management.requirements.PipRequirement import PipRequirement
from coalib.results.RESULT_SEVERITY import RESULT_SEVERITY
from coalib.results.Result import Result


class InvalidLinkBear(LocalBear):
    DEFAULT_TIMEOUT = 15
    LANGUAGES = {'All'}
    REQUIREMENTS = {PipRequirement('requests', '2.12')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Documentation'}
    BEAR_DEPS = {URLHeadBear}

    def run(self, filename, file,
            dependency_results=dict(),
            follow_redirects: bool = False,
            ):
        """
        Find links in any text file and check if they are valid.

        A link is considered valid if the server responds with a 2xx code.

        This bear can automatically fix redirects, but ignores redirect
        URLs that have a huge difference with the original URL.

        Warning: This bear will make HEAD requests to all URLs mentioned in
        your codebase, which can potentially be destructive. As an example,
        this bear would naively just visit the URL from a line that goes like
        `do_not_ever_open = 'https://api.acme.inc/delete-all-data'` wiping out
        all your data.

        :param dependency_results: Results given by URLBear.
        :param follow_redirects: Set to true to autocorrect redirects.
        """
        for result in dependency_results.get(URLHeadBear.name, []):
            line_number, link, code, context, robots_allowed = result.contents
            if context is context.xml_namespace:
                if code and 200 <= code < 300:
                    pass
                else:
                    yield Result.from_values(
                        origin=self,
                        message=('XML Namespace - '
                                 '{url}').format(url=link),
                        file=filename,
                        line=line_number,
                        severity=RESULT_SEVERITY.INFO)
            elif not robots_allowed:
                yield Result.from_values(
                    origin=self,
                    message=('robots.txt does not allow request to '
                             '{url}').format(url=link),
                    file=filename,
                    line=line_number,
                    severity=RESULT_SEVERITY.NORMAL)
            elif code is None:
                yield Result.from_values(
                    origin=self,
                    message=('Broken link - unable to connect to '
                             '{url}').format(url=link),
                    file=filename,
                    line=line_number,
                    severity=RESULT_SEVERITY.MAJOR)
            elif not 200 <= code < 300:
                # HTTP status 404, 410 or 50x
                if code in (404, 410) or 500 <= code < 600:
                    yield Result.from_values(
                        origin=self,
                        message=('Broken link - HTTP Error: {code} '
                                 'generated when connecting to {url}'
                                 ).format(url=link, code=code),
                        file=filename,
                        line=line_number,
                        severity=RESULT_SEVERITY.NORMAL)
                if follow_redirects and 300 <= code < 400:  # HTTP status 30x
                    redirect_url = requests.head(link,
                                                 allow_redirects=True).url
                    matcher = SequenceMatcher(
                        None, redirect_url, link)
                    if (matcher.real_quick_ratio() > 0.7 and
                            matcher.ratio()) > 0.7:
                        diff = Diff(file)
                        current_line = file[line_number - 1]
                        start = current_line.find(link)
                        end = start + len(link)
                        replacement = current_line[:start] + \
                            redirect_url + current_line[end:]
                        diff.change_line(line_number,
                                         current_line,
                                         replacement)

                        yield Result.from_values(
                            self,
                            'This link redirects to ' + redirect_url,
                            diffs={filename: diff},
                            file=filename,
                            line=line_number,
                            severity=RESULT_SEVERITY.NORMAL)
