import os
from queue import Queue
from shutil import which
from unittest.case import skipIf

from bears.multimedia.FFprobeBear import FFprobeBear
from coalib.testing.LocalBearTestHelper import LocalBearTestHelper
from coalib.settings.Section import Section


@skipIf(which('ffprobe') is None, 'ffprobe is not installed')
class StyleLintBearTest(LocalBearTestHelper):

    def setUp(self):
        self.section = Section('test section')
        self.uut = FFprobeBear(self.section, Queue())
        test_files = os.path.join(os.path.dirname(__file__), 'test_files')
        self.good_file = os.path.join(test_files, 'good_file.mp4')
        self.bad_video_file = os.path.join(test_files, 'bad_file.mp4')
        self.bad_text_file = os.path.join(test_files, 'text')
        self.bad_misc_file = os.path.join(test_files, 'test.json')

    def test_run(self):
        self.check_validity(self.uut, [], self.good_file)
        self.check_invalidity(self.uut, [], self.bad_video_file)
        self.check_invalidity(self.uut, [], self.bad_text_file)
        self.check_invalidity(self.uut, [], self.bad_misc_file)
