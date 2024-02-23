import os
import unittest
from pathlib import Path
from datetime import date

from uploader import load_config, is_public_holiday


class HolidayTest(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).parent
        self.config = load_config(os.path.join(root, "config.yaml"))

    def test_public_holiday(self):
        self.assertTrue(is_public_holiday(self.config['public_holidays'], date(2024, 1, 1)))

    def test_not_public_holiday(self):
        self.assertFalse(is_public_holiday(self.config['public_holidays'], date(2024, 12, 24)))