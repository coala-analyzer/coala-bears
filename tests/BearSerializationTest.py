import itertools
import json
import os
import unittest

from pyprint.NullPrinter import NullPrinter

from coalib.bears.BEAR_KIND import BEAR_KIND
from coalib.collecting.Collectors import collect_bears
from coalib.output.JSONEncoder import create_json_encoder
from coalib.output.printers.LogPrinter import LogPrinter


class BearSerializationTest(unittest.TestCase):
    """
    Test to make sure all bears are serializable.
    """

    def setUp(self):
        printer = LogPrinter(NullPrinter())
        local_bears, global_bears = collect_bears(
            [os.path.abspath("bears")],
            ["**"],
            [BEAR_KIND.LOCAL, BEAR_KIND.GLOBAL],
            printer,
            warn_if_unused_glob=False)
        self.bears = list(itertools.chain(local_bears, global_bears))
        self.JSONEncoder = create_json_encoder(use_relpath=False)

    def test(self):
        ERROR_STR = ("{} is not JSON serializable. If you have added or "
                     "modified this bear then make sure all non-serializable "
                     "attributes are private. More information about "
                     "serializable attributes can be found at https://docs."
                     "python.org/3.4/library/json.html#encoders-and-decoders")
        for bear in self.bears:
            try:
                json.dumps(bear, cls=self.JSONEncoder)
            except TypeError:
                self.fail(ERROR_STR.format(bear.name))
