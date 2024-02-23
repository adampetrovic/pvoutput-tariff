import datetime
import os
import unittest
from pathlib import Path

from uploader import get_current_tariff, load_tariff_config


class MyTestCase(unittest.TestCase):

    def setUp(self):
        root = Path(__file__).parent
        self.config = load_tariff_config(os.path.join(root, "config.yaml"))
    def test_summer_peak(self):
        summer_peak = datetime.datetime(
            2024, 1, 1, 19, 30, 00)
        current_tariff = get_current_tariff(self.config, summer_peak)
        self.assertEqual(current_tariff, 66.1815)

    def test_winter_peak(self):
        summer_peak = datetime.datetime(
            2024, 7, 1, 19, 30, 00)
        current_tariff = get_current_tariff(self.config, summer_peak)
        self.assertEqual(current_tariff, 66.1815)

    def test_outside_peak(self):
        spring_peak = datetime.datetime(
            2024, 9, 9, 19, 30, 00)
        current_tariff = get_current_tariff(self.config, spring_peak)
        self.assertEqual(current_tariff, 33.8415)

        autumn_peak = datetime.datetime(
            2024, 4, 21, 19, 30, 00)
        current_tariff = get_current_tariff(self.config, autumn_peak)
        self.assertEqual(current_tariff, 33.8415)

    def test_offpeak(self):
        offpeak = datetime.datetime(
            2024, 9, 9, 6, 30, 00)
        current_tariff = get_current_tariff(self.config, offpeak)
        self.assertEqual(current_tariff, 31.3005)

    def test_super_offpeak_precedence(self):
        super_offpeak = datetime.datetime(
            2024, 9, 9, 11, 30, 00)
        current_tariff = get_current_tariff(self.config, super_offpeak)
        self.assertEqual(current_tariff, 0)

if __name__ == '__main__':
    unittest.main()
