import datetime
import os
import unittest
from pathlib import Path

from uploader import get_current_tariff, load_config


class TariffTests(unittest.TestCase):

    def setUp(self):
        root = Path(__file__).parent
        config = load_config(os.path.join(root, "config.yaml"))
        self.tariff_config = config["tariffs"]
        self.public_holidays = config["public_holidays"]
        self.price_mapping = dict(
            (tariff, params["price"]) for tariff, params in self.tariff_config.items()
        )

    def test_summer_peak_weekday(self):
        summer_peak = datetime.datetime(2024, 1, 10, 19, 30, 00)
        current_tariff = get_current_tariff(
            self.tariff_config, self.public_holidays, summer_peak
        )
        self.assertEqual(current_tariff, self.price_mapping["peak_summer"])

    def test_summer_peak_public_holiday(self):
        summer_peak = datetime.datetime(2024, 1, 1, 19, 30, 00)
        current_tariff = get_current_tariff(
            self.tariff_config, self.public_holidays, summer_peak
        )
        self.assertEqual(current_tariff, self.price_mapping["shoulder"])

    def test_not_summer_peak_weekend(self):
        # Jan 6th 2024 is a Saturday
        summer_peak = datetime.datetime(2024, 1, 6, 19, 30, 00)
        current_tariff = get_current_tariff(
            self.tariff_config, self.public_holidays, summer_peak
        )

        # shouldn't
        self.assertEqual(current_tariff, self.price_mapping["shoulder"])

    def test_winter_peak(self):
        # June 3rd 2024 is a Monday
        summer_peak = datetime.datetime(2024, 6, 3, 19, 30, 00)
        current_tariff = get_current_tariff(
            self.tariff_config, self.public_holidays, summer_peak
        )
        self.assertEqual(current_tariff, self.price_mapping["peak_winter"])

    def test_winter_peak_weekend(self):
        # June 1st 2024 is a Saturday
        summer_peak = datetime.datetime(2024, 6, 1, 19, 30, 00)
        current_tariff = get_current_tariff(
            self.tariff_config, self.public_holidays, summer_peak
        )
        self.assertEqual(current_tariff, self.price_mapping["shoulder"])

    def test_not_winter_peak_holiday(self):
        # June 10th 2024 is a public holiday
        summer_peak = datetime.datetime(2024, 6, 10, 19, 30, 00)
        current_tariff = get_current_tariff(
            self.tariff_config, self.public_holidays, summer_peak
        )
        self.assertEqual(current_tariff, self.price_mapping["shoulder"])

    def test_outside_peak(self):
        spring_peak = datetime.datetime(2024, 9, 9, 19, 30, 00)
        current_tariff = get_current_tariff(
            self.tariff_config, self.public_holidays, spring_peak
        )
        self.assertEqual(current_tariff, 33.8415)

        autumn_peak = datetime.datetime(2024, 4, 21, 19, 30, 00)
        current_tariff = get_current_tariff(
            self.tariff_config, self.public_holidays, autumn_peak
        )
        self.assertEqual(current_tariff, self.price_mapping["shoulder"])

    def test_offpeak(self):
        offpeak = datetime.datetime(2024, 9, 9, 6, 30, 00)
        current_tariff = get_current_tariff(
            self.tariff_config, self.public_holidays, offpeak
        )
        self.assertEqual(current_tariff, self.price_mapping["offpeak"])

    def test_super_offpeak_precedence(self):
        # pick a time that overlaps with both super offpeak and shoulder
        super_offpeak = datetime.datetime(2024, 9, 9, 11, 30, 00)
        current_tariff = get_current_tariff(
            self.tariff_config, self.public_holidays, super_offpeak
        )
        self.assertEqual(current_tariff, self.price_mapping["super_offpeak"])


if __name__ == "__main__":
    unittest.main()
