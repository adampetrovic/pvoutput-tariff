import os
import unittest
from datetime import date
from pathlib import Path

from uploader import is_public_holiday, load_config


class HolidayTest(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).parent
        self.config = load_config(os.path.join(root, "config.yaml"))

    def test_public_holiday(self):
        self.assertTrue(
            is_public_holiday(self.config["public_holidays"], date(2024, 1, 1))
        )

    def test_not_public_holiday(self):
        self.assertFalse(
            is_public_holiday(self.config["public_holidays"], date(2024, 12, 24))
        )
