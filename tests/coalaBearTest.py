import logging
import unittest
import unittest.mock

import bears
import coalib

from bears import assert_supported_version


class coalaBearTest(unittest.TestCase):

    def test_check_coala_version(self):
        bears.__version__ = coalib.__version__ = '1.0.0.dev999999999'
        logger = logging.getLogger()
        with self.assertLogs(logger, 'WARNING') as cm:
            bears.check_coala_version()
            self.assertEqual(0, len(cm.output))

            bears.__version__ = '1.1.0.dev999999999'
            bears.check_coala_version()
            self.assertEqual(0, len(cm.output))

            bears.__version__ = '1.0.0.dev999999999'
            coalib.__version__ = '1.1.0.dev999999999'
            bears.check_coala_version()
            self.assertIn('Version mismatch between coala',
                          cm.output[0])

    @unittest.mock.patch('sys.version_info', tuple((2, 7, 11)))
    def test_python_version_27(self):
        with self.assertRaises(SystemExit) as cm:
            assert_supported_version()

        self.assertEqual(cm.exception.code, 4)

    @unittest.mock.patch('sys.version_info', tuple((3, 3, 6)))
    def test_python_version_33(self):
        with self.assertRaises(SystemExit) as cm:
            assert_supported_version()

        self.assertEqual(cm.exception.code, 4)

    def test_python_version_34(self):
        assert_supported_version()
