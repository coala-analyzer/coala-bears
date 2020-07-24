import os
import platform
import shutil
import stat
import unittest
import unittest.mock
from queue import Queue
from tempfile import mkdtemp
from pathlib import Path

from coalib.testing.BearTestHelper import generate_skip_decorator
from bears.vcs.git.GitCommitBear import GitCommitBear
from coala_utils.string_processing.Core import escape
from coalib.misc.Shell import run_shell_command
from coalib.settings.ConfigurationGathering import get_config_directory
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting


@generate_skip_decorator(GitCommitBear)
class GitCommitBearTest(unittest.TestCase):

    @staticmethod
    def run_git_command(*args, stdin=None):
        run_shell_command(' '.join(('git',) + args), stdin)

    @staticmethod
    def git_commit(msg):
        # Use stdin mode from git, since -m on Windows cmd does not support
        # multiline messages.
        GitCommitBearTest.run_git_command('commit',
                                          '--allow-empty',
                                          '--allow-empty-message',
                                          '--file=-',
                                          stdin=msg)

    def run_uut(self, *args, **kwargs):
        """
        Runs the unit-under-test (via `self.uut.run()`) and collects the
        messages of the yielded results as a list.

        :param args:   Positional arguments to forward to the run function.
        :param kwargs: Keyword arguments to forward to the run function.
        :return:       A list of the message strings.
        """
        return list(result.message for result in self.uut.run(*args, **kwargs))

    def assert_no_msgs(self):
        """
        Assert that there are no messages in the message queue of the bear, and
        show the messages in the failure messgae if it is not empty.
        """
        self.assertTrue(
            self.msg_queue.empty(),
            'Expected no messages in bear message queue, but got: ' +
            str(list(str(i) for i in self.msg_queue.queue)))

    def setUp(self):
        self.msg_queue = Queue()
        self.section = Section('')
        self.uut = GitCommitBear(None, self.section, self.msg_queue)

        self._old_cwd = os.getcwd()
        self.gitdir = mkdtemp()
        os.chdir(self.gitdir)
        self.run_git_command('init')
        self.run_git_command('config', 'user.email coala@coala.io')
        self.run_git_command('config', 'user.name coala')

    @staticmethod
    def _windows_rmtree_remove_readonly(func, path, excinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def tearDown(self):
        os.chdir(self._old_cwd)
        if platform.system() == 'Windows':
            onerror = self._windows_rmtree_remove_readonly
        else:
            onerror = None
        shutil.rmtree(self.gitdir, onerror=onerror)

    def test_git_failure(self):
        # In this case use a reference to a non-existing commit, so just try
        # to log all commits on a newly created repository.
        self.assertEqual(self.run_uut(), [])

        git_error = self.msg_queue.get().message
        self.assertEqual(git_error[:4], 'git:')

        self.assert_no_msgs()

    def test_empty_message(self):
        self.git_commit('')

        self.assertEqual(self.run_uut(),
                         ['HEAD commit has no message.'])
        self.assert_no_msgs()

        self.assertEqual(self.run_uut(allow_empty_commit_message=True),
                         [])
        self.assert_no_msgs()

    def test_github_pull_request_temporary_merge_commit_check(self):
        self.run_git_command('remote', 'add', 'upstream',
                             'https://github.com/coala/coala-quickstart.git')
        run_shell_command('git fetch upstream pull/259/merge:pytest36')
        run_shell_command('git checkout pytest36')
        self.assertEqual(self.run_uut(), [])

        run_shell_command('git fetch upstream pull/257/merge:patch-1')
        run_shell_command('git checkout patch-1')
        self.assertEqual(self.run_uut(),
                         ["Shortlog of HEAD commit isn't in imperative"
                          " mood! Bad words are 'Fixed'"])

        self.git_commit('Simple git commit')
        self.assertEqual(self.run_uut(), [])

    def test_github_PR_merge_commit_check_offline(self):
        Path('testfile1.txt').touch()
        run_shell_command('git add testfile1.txt')
        run_shell_command('git commit -m "First commit"')
        commit_hash1, _ = run_shell_command('git rev-parse HEAD')
        commit_hash1 = commit_hash1.strip('\n')

        run_shell_command('git checkout -b feature1 master')
        Path('testfile2.txt').touch()
        run_shell_command('git add testfile2.txt')
        run_shell_command('git commit -m "Second commit"')
        commit_hash2, _ = run_shell_command('git rev-parse HEAD')
        commit_hash2 = commit_hash2.strip('\n')

        run_shell_command('git checkout master')
        run_shell_command('git merge --no-ff feature1')
        command = ('git commit --amend -m "Merge %s into %s"'
                   % (commit_hash1, commit_hash2))
        run_shell_command(command)

        self.assertEqual(self.run_uut(), [])

        Path('testfile3.txt').touch()
        run_shell_command('git add testfile3.txt')
        run_shell_command('git commit -m "Adding First commit"')
        commit_hash1, _ = run_shell_command('git rev-parse HEAD')
        commit_hash1 = commit_hash1.strip('\n')

        run_shell_command('git checkout -b feature2 master')
        Path('testfile4.txt').touch()
        run_shell_command('git add testfile4.txt')
        run_shell_command('git commit -m "Second commit"')
        commit_hash2, _ = run_shell_command('git rev-parse HEAD')
        commit_hash2 = commit_hash2.strip('\n')

        run_shell_command('git checkout master')
        run_shell_command('git merge --no-ff feature2')
        command = ('git commit --amend -m "Merge %s into %s"'
                   % (commit_hash1, commit_hash2))
        run_shell_command(command)

        self.assertEqual(self.run_uut(),
                         ["Shortlog of HEAD commit isn't in imperative"
                          " mood! Bad words are 'Adding'"])

    def test_shortlog_checks_length(self):
        self.git_commit('Commit messages that nearly exceed default limit..')

        self.assertEqual(self.run_uut(), [])
        self.assert_no_msgs()

        self.assertEqual(self.run_uut(shortlog_length=17),
                         ['Shortlog of the HEAD commit contains 50 '
                          'character(s). This is 33 character(s) longer than '
                          'the limit (50 > 17).'])
        self.assert_no_msgs()

        self.git_commit('Add a very long shortlog for a bad project history.')
        self.assertEqual(self.run_uut(),
                         ['Shortlog of the HEAD commit contains 51 '
                          'character(s). This is 1 character(s) longer than '
                          'the limit (51 > 50).'])
        self.assert_no_msgs()

    def test_shortlog_checks_shortlog_trailing_period(self):
        self.git_commit('Shortlog with dot.')
        self.assertEqual(self.run_uut(shortlog_trailing_period=True), [])
        self.assertEqual(self.run_uut(shortlog_trailing_period=False),
                         ['Shortlog of HEAD commit contains a period at end.'])
        self.assertEqual(self.run_uut(shortlog_trailing_period=None), [])

        self.git_commit('Shortlog without dot')
        self.assertEqual(
            self.run_uut(shortlog_trailing_period=True),
            ['Shortlog of HEAD commit contains no period at end.'])
        self.assertEqual(self.run_uut(shortlog_trailing_period=False), [])
        self.assertEqual(self.run_uut(shortlog_trailing_period=None), [])

    def test_shortlog_wip_check(self):
        self.git_commit('[wip] Shortlog')
        self.assertEqual(self.run_uut(shortlog_wip_check=False), [])
        self.assertEqual(self.run_uut(shortlog_wip_check=True),
                         ['This commit seems to be marked as work in progress '
                          'and should not be used in production. Treat '
                          'carefully.'])
        self.git_commit('WIP: Shortlog')
        self.assertEqual(self.run_uut(shortlog_wip_check=True),
                         ['This commit seems to be marked as work in progress '
                          'and should not be used in production. Treat '
                          'carefully.'])
        self.assertEqual(self.run_uut(shortlog_wip_check=None), [])
        self.git_commit('Shortlog as usual')
        self.assertEqual(self.run_uut(shortlog_wip_check=True), [])

    def test_shortlog_checks_imperative(self):
        self.git_commit('tag: Add shortlog in imperative')
        self.assertNotIn("Shortlog of HEAD commit isn't in imperative "
                         "mood! Bad words are 'added'",
                         self.run_uut())
        self.git_commit('Added invalid shortlog')
        self.assertIn("Shortlog of HEAD commit isn't in imperative "
                      "mood! Bad words are 'Added'",
                      self.run_uut())
        self.git_commit('Adding another invalid shortlog')
        self.assertIn("Shortlog of HEAD commit isn't in imperative "
                      "mood! Bad words are 'Adding'",
                      self.run_uut())
        self.git_commit('Added another invalid shortlog')
        self.assertNotIn("Shortlog of HEAD commit isn't in imperative "
                         "mood! Bad words are 'Added'",
                         self.run_uut(shortlog_imperative_check=False))

    def test_shortlog_checks_regex(self):
        pattern = '.*?: .*[^.]'

        self.git_commit('tag: message')
        self.assertEqual(self.run_uut(shortlog_regex=pattern), [])

        self.git_commit('tag: message invalid.')
        self.assertEqual(
            self.run_uut(shortlog_regex=pattern),
            ['Shortlog of HEAD commit does not match given regex: {regex}'
             .format(regex=pattern)])

        self.git_commit('SuCkS cOmPleTely')
        self.assertEqual(
            self.run_uut(shortlog_regex=pattern),
            ['Shortlog of HEAD commit does not match given regex: {regex}'
             .format(regex=pattern)])
        # Check for full-matching.
        pattern = 'abcdefg'

        self.git_commit('abcdefg')
        self.assertEqual(self.run_uut(shortlog_regex=pattern), [])

        self.git_commit('abcdefgNO MATCH')
        self.assertEqual(
            self.run_uut(shortlog_regex=pattern),
            ['Shortlog of HEAD commit does not match given regex: {regex}'
             .format(regex=pattern)])

    def test_body_checks(self):
        self.git_commit(
            'Commits message with a body\n\n'
            'nearly exceeding the default length of a body, but not quite. '
            'haaaaaands')

        self.assertEqual(self.run_uut(), [])
        self.assert_no_msgs()

        self.git_commit('Shortlog only')

        self.assertEqual(self.run_uut(), [])
        self.assert_no_msgs()

        # Force a body.
        self.git_commit('Shortlog only ...')
        self.assertEqual(self.run_uut(force_body=True),
                         ['No commit message body at HEAD.'])
        self.assert_no_msgs()

        # Miss a newline between shortlog and body.
        self.git_commit('Shortlog\nOops, body too early')
        self.assertEqual(self.run_uut(),
                         ['No newline found between shortlog and body at '
                          'HEAD commit. Please add one.'])
        self.assert_no_msgs()

        # And now too long lines.
        self.git_commit('Shortlog\n\n'
                        'This line is ok.\n'
                        'This line is by far too long (in this case).\n'
                        'This one too, blablablablablablablablabla.')
        self.assertEqual(self.run_uut(body_line_length=41),
                         ['Body of HEAD commit contains too long lines. '
                          'Commit body lines should not exceed 41 '
                          'characters.'])
        self.assert_no_msgs()

        # Allow long lines with ignore regex
        self.git_commit('Shortlog\n\n'
                        'This line is ok.\n'
                        'This line is by far too long (in this case).')
        self.assertEqual(self.run_uut(body_line_length=41,
                                      ignore_length_regex=('^.*too long',)),
                         [])
        self.assertTrue(self.msg_queue.empty())

        # body_regex, not fully matched
        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Fix 1112')
        self.assertEqual(self.run_uut(
                             body_regex=r'Fix\s+[1-9][0-9]*\s*'),
                         ['No match found in commit message for the regular '
                          r'expression provided: Fix\s+[1-9][0-9]*\s*'])
        self.assert_no_msgs()

        # Matching with regexp, fully matched
        self.git_commit('Shortlog\n\n'
                        'TICKER\n'
                        'CLOSE 2017')
        self.assertEqual(self.run_uut(
                             body_regex=r'TICKER\s*CLOSE\s+[1-9][0-9]*'), [])
        self.assert_no_msgs()

    def test_check_issue_reference(self):
        # Commit with no remotes configured
        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Closes #01112')
        self.assertEqual(self.run_uut(body_close_issue=True), [])

        # Adding BitBucket remote for testing
        self.run_git_command('remote', 'add', 'test',
                             'https://bitbucket.com/user/repo.git')

        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Closes #1112')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_close_issue_full_url=True),
                         ['Host bitbucket does not support full issue '
                          'reference.'])

        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Closes #1112')
        self.assertEqual(self.run_uut(
                             body_close_issue=True), [])

        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Resolves https://bitbucket.org/user/repo/issues/1/')
        self.assertEqual(self.run_uut(
                             body_close_issue=True),
                         ['Invalid bitbucket issue reference: '
                          'https://bitbucket.org/user/repo/issues/1/'])

        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Resolves https://bitbucket.org/user/repo/issues/1/')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_close_issue_full_url=True),
                         ['Host bitbucket does not support full issue '
                          'reference.'])

        # Adding BitBucket's ssh remote for testing
        self.run_git_command('remote', 'set-url', 'test',
                             'git@bitbucket.org:user/repo.git')

        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Closes #1112')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_close_issue_full_url=True),
                         ['Host bitbucket does not support full issue '
                          'reference.'])

        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Closes #1112')
        self.assertEqual(self.run_uut(
                             body_close_issue=True), [])

        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Fix issue #1112')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_enforce_issue_reference=True), [])

        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Resolving    bug#1112')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_enforce_issue_reference=True),
                         ['Invalid bitbucket issue reference: bug#1112'])

        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Fixed randomkeyword#1112')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_enforce_issue_reference=True),
                         ['Invalid bitbucket issue reference: '
                          'randomkeyword#1112'])

        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Closes#1112')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_enforce_issue_reference=True),
                         ['Body of HEAD commit does not contain any '
                          'issue reference.'])

        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Closes bug bug#1112')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_enforce_issue_reference=True),
                         ['Invalid bitbucket issue reference: bug'])

        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Closesticket #1112')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_enforce_issue_reference=True),
                         ['Body of HEAD commit does not contain any '
                          'issue reference.'])

        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Resolves https://bitbucket.org/user/repo/issues/1/')
        self.assertEqual(self.run_uut(
                             body_close_issue=True),
                         ['Invalid bitbucket issue reference: '
                          'https://bitbucket.org/user/repo/issues/1/'])

        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Resolves https://bitbucket.org/user/repo/issues/1/')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_close_issue_full_url=True),
                         ['Host bitbucket does not support full issue '
                          'reference.'])

        # Adding GitHub remote for testing, ssh way :P
        self.run_git_command('remote', 'set-url', 'test',
                             'git@github.com:user/repo.git')

        # GitHub host with an issue
        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Fixed https://github.com/usr/repo/issues/1112\n'
                        'and https://github.com/usr/repo/issues/1312')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_close_issue_full_url=True), [])

        # No keywords and no issues
        self.git_commit('Shortlog\n\n'
                        'This line is ok.\n'
                        'This line is by far too long (in this case).\n'
                        'This one too, blablablablablablablablabla.')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_close_issue_full_url=True,
                             body_close_issue_on_last_line=True), [])
        self.assert_no_msgs()

        # No keywords, no issues, no body
        self.git_commit('Shortlog only')
        self.assertEqual(self.run_uut(body_close_issue=True,
                                      body_close_issue_on_last_line=True), [])
        self.assert_no_msgs()

        # Has keyword but no valid issue URL
        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Fix https://github.com/user/repo.git')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_close_issue_full_url=True),
                         ['Invalid github full issue reference: '
                          'https://github.com/user/repo.git'])
        self.assert_no_msgs()

        # GitHub host with short issue tag
        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Fix #1112, #1115 and #123')
        self.assertEqual(self.run_uut(body_close_issue=True,), [])

        # GitHub host with invalid short issue tag
        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Fix #01112 and #111')
        self.assertEqual(self.run_uut(body_close_issue=True,),
                         ['Invalid github issue number: #01112'])
        self.assert_no_msgs()

        # GitHub host with no full issue reference
        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Fix #1112')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_close_issue_full_url=True),
                         ['Invalid github full issue reference: #1112'])
        self.assert_no_msgs()

        # Invalid characters in issue number
        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Fix #1112-3')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_close_issue_full_url=True),
                         ['Invalid github full issue reference: #1112-3'])
        self.assert_no_msgs()

        # Adding GitLab remote for testing
        self.run_git_command('remote', 'set-url', 'test',
                             'https://gitlab.com/user/repo.git')

        # GitLab chosen and has an issue
        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Resolve https://gitlab.com/usr/repo/issues/1112\n'
                        'and https://gitlab.com/usr/repo/issues/1312')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_close_issue_full_url=True), [])

        # Invalid issue number in URL
        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Closing https://gitlab.com/user/repo/issues/123\n'
                        'and https://gitlab.com/user/repo/issues/not_num')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_close_issue_full_url=True),
                         ['Invalid gitlab full issue reference: '
                          'https://gitlab.com/user/repo/issues/not_num'])
        self.assert_no_msgs()

        # Invalid URL
        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Fix www.google.com/issues/hehehe')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_close_issue_full_url=True),
                         ['Invalid gitlab full issue reference: '
                          'www.google.com/issues/hehehe'])
        self.assert_no_msgs()

        # One of the short references is broken
        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Resolve #11 and close #notnum')
        self.assertEqual(self.run_uut(body_close_issue=True,),
                         ['Invalid gitlab issue reference: #notnum'])
        self.assert_no_msgs()

        # Close issues in other repos
        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Resolve #11 and close github/gitter#32')
        self.assertEqual(self.run_uut(body_close_issue=True,), [])
        self.assert_no_msgs()

        # Incorrect close issue other repo pattern
        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Another line, blablablablablabla.\n'
                        'Fix #11 and close github#32')
        self.assertEqual(self.run_uut(body_close_issue=True,),
                         ['Invalid gitlab issue reference: github#32'])
        self.assert_no_msgs()

        # Last line enforce full URL
        self.git_commit('Shortlog\n\n'
                        'First line, blablablablablabla.\n'
                        'Fix http://gitlab.com/user/repo/issues/1112\n'
                        'Another line, blablablablablabla.\n')
        self.assertEqual(self.run_uut(
                             body_close_issue=True,
                             body_close_issue_full_url=True,
                             body_close_issue_on_last_line=True,
                             body_enforce_issue_reference=True),
                         ['Body of HEAD commit does not contain any full issue'
                          ' reference in the last line.'])
        self.assert_no_msgs()

    def test_different_path(self):
        no_git_dir = mkdtemp()
        self.git_commit('Add a very long shortlog for a bad project history.')
        os.chdir(no_git_dir)
        # When section doesn't have a project_dir
        self.assertEqual(self.run_uut(), [])
        git_error = self.msg_queue.get().message
        self.assertEqual(git_error[:4], 'git:')
        # when section does have a project_dir
        self.section.append(Setting('project_dir', escape(self.gitdir, '\\')))
        self.assertEqual(self.run_uut(),
                         ['Shortlog of the HEAD commit contains 51 '
                          'character(s). This is 1 character(s) longer than '
                          'the limit (51 > 50).'])
        self.assertEqual(get_config_directory(self.section),
                         self.gitdir)
        os.chdir(self.gitdir)
        os.rmdir(no_git_dir)
