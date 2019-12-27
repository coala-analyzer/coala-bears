import os
from queue import Queue

from coalib.settings.Section import Section
from coalib.testing.LocalBearTestHelper import LocalBearTestHelper
from coalib.testing.BearTestHelper import generate_skip_decorator

from bears.java.SpotBugsBear import SpotBugsBear


def get_testfile_path(name):
    return os.path.join(os.path.dirname(__file__),
                        'spotbugs_test_files',
                        name)


def load_testfile(name):
    with open(get_testfile_path(name)) as f:
        return f.readlines()


@generate_skip_decorator(SpotBugsBear)
class SpotBugsBearTest(LocalBearTestHelper):

    def setUp(self):
        self.section = Section('name')
        self.uut = SpotBugsBear(self.section, Queue())
