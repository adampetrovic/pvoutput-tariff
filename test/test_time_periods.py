import unittest
from datetime import time

from uploader import is_time_in_period


class TimePeriodTests(unittest.TestCase):
    def test_normal_time_period(self):
        """Test normal time period (start < end)"""
        current_time = time(15, 30)  # 3:30 PM
        self.assertTrue(is_time_in_period(current_time, "14:00", "16:00"))
        self.assertFalse(is_time_in_period(current_time, "16:00", "18:00"))

    def test_overnight_time_period(self):
        """Test overnight time period (start > end)"""
        # Test time during overnight period
        current_time = time(23, 30)  # 11:30 PM
        self.assertTrue(is_time_in_period(current_time, "22:00", "06:00"))

        current_time = time(2, 30)  # 2:30 AM
        self.assertTrue(is_time_in_period(current_time, "22:00", "06:00"))

        # Test time outside overnight period
        current_time = time(12, 30)  # 12:30 PM
        self.assertFalse(is_time_in_period(current_time, "22:00", "06:00"))

    def test_boundary_times(self):
        """Test exact boundary times"""
        current_time = time(14, 0)  # Exact start time
        self.assertTrue(is_time_in_period(current_time, "14:00", "16:00"))

        current_time = time(16, 0)  # Exact end time
        self.assertTrue(is_time_in_period(current_time, "14:00", "16:00"))

        # Test overnight boundaries
        current_time = time(22, 0)  # Exact start time
        self.assertTrue(is_time_in_period(current_time, "22:00", "06:00"))

        current_time = time(6, 0)  # Exact end time
        self.assertTrue(is_time_in_period(current_time, "22:00", "06:00"))

    def test_single_minute_period(self):
        """Test very short time periods"""
        current_time = time(14, 30)
        self.assertTrue(is_time_in_period(current_time, "14:30", "14:30"))
        self.assertFalse(is_time_in_period(current_time, "14:31", "14:31"))


if __name__ == "__main__":
    unittest.main()
