from queue import Queue

from bears.latex.LatexLintBear import LatexLintBear
from coalib.testing.BearTestHelper import generate_skip_decorator
from coalib.testing.LocalBearTestHelper import LocalBearTestHelper
from coalib.settings.Section import Section


@generate_skip_decorator(LatexLintBear)
class LatexLintBearTest(LocalBearTestHelper):

    def setUp(self):
        self.section = Section('name')
        self.uut = LatexLintBear(self.section, Queue())

    def test_result(self):
        self.check_validity(self.uut, ['{.}', '{ sometext }'])
        self.check_invalidity(self.uut, ['{ .}', '{ sometext }'])
        results = self.check_invalidity(self.uut, ['2018-12-01'])
        self.assertEqual('Wrong length of dash may have been used.',
                         results[0].message)
