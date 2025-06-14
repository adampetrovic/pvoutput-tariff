import unittest
from datetime import date, datetime

from uploader import get_current_tariff, is_public_holiday


class EdgeCaseTests(unittest.TestCase):
    def test_get_current_tariff_no_offpeak(self):
        """Test behavior when no offpeak tariff is defined"""
        tariff_config = {
            "peak": {"price": 50.0, "times": [{"start": "14:00", "end": "20:00"}]}
        }

        # Time outside peak should return 0.0 when no offpeak is defined
        test_datetime = datetime(2024, 6, 15, 10, 0, 0)  # 10 AM
        result = get_current_tariff(tariff_config, {}, test_datetime)
        self.assertEqual(result, 0.0)

    def test_get_current_tariff_empty_times(self):
        """Test tariff with empty times list"""
        tariff_config = {
            "shoulder": {"price": 40.0, "times": []},  # Empty times
            "offpeak": {"price": 30.0, "times": []},
        }

        test_datetime = datetime(2024, 6, 15, 10, 0, 0)
        result = get_current_tariff(tariff_config, {}, test_datetime)
        self.assertEqual(result, 30.0)  # Should fall back to offpeak

    def test_is_public_holiday_empty_config(self):
        """Test holiday check with empty config"""
        self.assertFalse(is_public_holiday({}, date(2024, 1, 1)))
        self.assertFalse(is_public_holiday(None, date(2024, 1, 1)))

    def test_is_public_holiday_missing_country(self):
        """Test holiday check with missing country"""
        config = {"region": "NSW"}  # Missing country
        self.assertFalse(is_public_holiday(config, date(2024, 1, 1)))

    def test_seasonal_tariff_edge_dates(self):
        """Test seasonal tariffs on exact start and end dates"""
        from datetime import date

        tariff_config = {
            "summer_peak": {
                "price": 70.0,
                "start_date": date(2024, 1, 1),
                "end_date": date(2024, 3, 31),
                "weekdays_only": False,
                "times": [{"start": "14:00", "end": "20:00"}],
            },
            "offpeak": {"price": 30.0, "times": []},
        }

        # Test on exact start date
        test_datetime = datetime(2024, 1, 1, 15, 0, 0)  # 3 PM on start date
        result = get_current_tariff(tariff_config, {}, test_datetime)
        self.assertEqual(result, 70.0)

        # Test on exact end date
        test_datetime = datetime(2024, 3, 31, 15, 0, 0)  # 3 PM on end date
        result = get_current_tariff(tariff_config, {}, test_datetime)
        self.assertEqual(result, 70.0)

        # Test one day after end date
        test_datetime = datetime(2024, 4, 1, 15, 0, 0)  # 3 PM day after end
        result = get_current_tariff(tariff_config, {}, test_datetime)
        self.assertEqual(result, 30.0)  # Should fall back to offpeak

    def test_weekdays_only_with_holidays(self):
        """Test weekdays_only setting combined with public holidays"""
        from datetime import date

        tariff_config = {
            "weekday_peak": {
                "price": 60.0,
                "start_date": date(2024, 1, 1),
                "end_date": date(2024, 12, 31),
                "weekdays_only": True,
                "times": [{"start": "14:00", "end": "20:00"}],
            },
            "offpeak": {"price": 30.0, "times": []},
        }

        public_holidays = {"country": "AU", "region": "NSW"}
        # Test on a weekday that's also a holiday (New Year's Day 2024 is Monday)
        test_datetime = datetime(2024, 1, 1, 15, 0, 0)  # 3 PM on holiday weekday
        result = get_current_tariff(tariff_config, public_holidays, test_datetime)
        self.assertEqual(result, 30.0)  # Should use offpeak due to holiday

        # Test on regular weekday
        test_datetime = datetime(2024, 1, 2, 15, 0, 0)  # 3 PM on regular Tuesday
        result = get_current_tariff(tariff_config, public_holidays, test_datetime)
        self.assertEqual(result, 60.0)  # Should use weekday peak

    def test_multiple_overlapping_periods(self):
        """Test behavior with multiple overlapping time periods"""
        tariff_config = {
            "super_offpeak": {
                "price": 10.0,
                "times": [{"start": "11:00", "end": "14:00"}],
            },
            "shoulder": {"price": 40.0, "times": [{"start": "07:00", "end": "22:00"}]},
            "offpeak": {"price": 30.0, "times": []},
        }

        # Test time that overlaps - should get first matching tariff
        test_datetime = datetime(2024, 6, 15, 12, 0, 0)  # Noon - overlaps both
        result = get_current_tariff(tariff_config, {}, test_datetime)
        self.assertEqual(result, 10.0)  # Should get super_offpeak (first in dict)


if __name__ == "__main__":
    unittest.main()
