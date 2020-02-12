from queue import Queue

from bears.python.DocformatterBear import DocformatterBear
from coalib.testing.LocalBearTestHelper import LocalBearTestHelper
from coalib.settings.Section import Section


bad_file = '''
"""Let's check indentation.

        This module docstring should be dedented."""
'''

good_file = '''
"""Here are some examples.

This module docstring is dedented.

"""
'''

result_message = 'The documentation string does not meet PEP 257 conventions.'


class DocformatterBearTest(LocalBearTestHelper):

    def setUp(self):
        self.uut = DocformatterBear(Section('name'), Queue())

    def test_run(self):
        self.check_validity(self.uut, bad_file.splitlines(), valid=False)
        self.check_validity(self.uut, good_file.splitlines())
