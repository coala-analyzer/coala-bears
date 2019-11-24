import os
from queue import Queue

from coalib.settings.Section import Section
from coalib.testing.LocalBearTestHelper import LocalBearTestHelper

from bears.yang.YANGBear import YANGBear


def get_test_filename(basename):
    path = os.path.join(os.path.dirname(__file__), 'test_files', basename)
    assert os.path.isfile(path)
    return path


class YANGBearTest(LocalBearTestHelper):

    def setUp(self):
        self.uut = YANGBear(Section('yang'), Queue())

    def test_valid_files(self):
        self.check_validity(self.uut, [],
                            get_test_filename('coala-model.yang'))

    def test_invalid_files(self):
        self.check_invalidity(self.uut, [],
                              get_test_filename('invalid-model.yang'))
