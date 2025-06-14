import unittest
from datetime import date

from config_schema import validate_config


class ConfigValidationTests(unittest.TestCase):
    def setUp(self):
        """Set up a valid base configuration for testing."""
        self.valid_config = {
            "pvoutput": {"extended_param": "v12"},
            "tariffs": {
                "peak": {
                    "price": 66.18,
                    "times": [{"start": "14:00", "end": "20:00"}]
                },
                "offpeak": {
                    "price": 31.30,
                    "times": []
                }
            },
            "public_holidays": {
                "country": "AU",
                "region": "NSW"
            }
        }

    def test_valid_config(self):
        """Test that a valid configuration passes validation."""
        validate_config(self.valid_config)  # Should not raise

    def test_config_not_dict(self):
        """Test error when config is not a dictionary."""
        with self.assertRaises(ValueError) as cm:
            validate_config("not a dict")
        self.assertIn("Configuration must be a dictionary", str(cm.exception))

    def test_missing_required_keys(self):
        """Test error when required top-level keys are missing."""
        # Missing pvoutput
        config = {"tariffs": {}}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("Missing required configuration key: pvoutput", str(cm.exception))

        # Missing tariffs
        config = {"pvoutput": {"extended_param": "v12"}}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("Missing required configuration key: tariffs", str(cm.exception))

    def test_pvoutput_validation(self):
        """Test pvoutput section validation."""
        config = self.valid_config.copy()
        
        # Invalid pvoutput type
        config["pvoutput"] = "not a dict"
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("pvoutput configuration must be a dictionary", str(cm.exception))

        # Missing extended_param
        config["pvoutput"] = {}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("pvoutput configuration must include 'extended_param'", str(cm.exception))

        # Invalid extended_param type
        config["pvoutput"] = {"extended_param": 12}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("extended_param must be a string", str(cm.exception))

        # Invalid extended_param format
        config["pvoutput"] = {"extended_param": "invalid"}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("extended_param must be in format 'v1' to 'v12'", str(cm.exception))

        # Extended param out of range
        config["pvoutput"] = {"extended_param": "v13"}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("extended_param must be between v1 and v12", str(cm.exception))

    def test_tariffs_validation(self):
        """Test tariffs section validation."""
        config = self.valid_config.copy()
        
        # Invalid tariffs type
        config["tariffs"] = "not a dict"
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("tariffs configuration must be a dictionary", str(cm.exception))

        # Empty tariffs
        config["tariffs"] = {}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("tariffs configuration cannot be empty", str(cm.exception))

        # Missing offpeak tariff
        config["tariffs"] = {
            "peak": {"price": 50.0, "times": [{"start": "14:00", "end": "20:00"}]}
        }
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("tariffs must include an 'offpeak' tariff", str(cm.exception))

    def test_single_tariff_validation(self):
        """Test individual tariff validation."""
        config = self.valid_config.copy()
        
        # Invalid tariff type
        config["tariffs"]["peak"] = "not a dict"
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("Tariff 'peak' must be a dictionary", str(cm.exception))

        # Missing price
        config["tariffs"]["peak"] = {"times": []}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("Tariff 'peak' must have a 'price' field", str(cm.exception))

        # Invalid price type
        config["tariffs"]["peak"] = {"price": "not a number", "times": []}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("Tariff 'peak' price must be a number", str(cm.exception))

        # Negative price
        config["tariffs"]["peak"] = {"price": -10.0, "times": []}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("Tariff 'peak' price cannot be negative", str(cm.exception))

        # Missing times
        config["tariffs"]["peak"] = {"price": 50.0}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("Tariff 'peak' must have a 'times' field", str(cm.exception))

        # Invalid times type
        config["tariffs"]["peak"] = {"price": 50.0, "times": "not a list"}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("Tariff 'peak' times must be a list", str(cm.exception))

    def test_seasonal_tariff_validation(self):
        """Test seasonal tariff date validation."""
        config = self.valid_config.copy()
        
        # Only start_date without end_date
        config["tariffs"]["peak"] = {
            "price": 50.0,
            "times": [{"start": "14:00", "end": "20:00"}],
            "start_date": date(2024, 1, 1)
        }
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("must have both start_date and end_date", str(cm.exception))

        # Invalid start_date format
        config["tariffs"]["peak"] = {
            "price": 50.0,
            "times": [{"start": "14:00", "end": "20:00"}],
            "start_date": "invalid-date",
            "end_date": date(2024, 3, 31)
        }
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("start_date has invalid format", str(cm.exception))

        # start_date after end_date
        config["tariffs"]["peak"] = {
            "price": 50.0,
            "times": [{"start": "14:00", "end": "20:00"}],
            "start_date": date(2024, 3, 31),
            "end_date": date(2024, 1, 1)
        }
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("start_date must be before end_date", str(cm.exception))

        # Invalid weekdays_only type
        config["tariffs"]["peak"] = {
            "price": 50.0,
            "times": [{"start": "14:00", "end": "20:00"}],
            "weekdays_only": "yes"
        }
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("weekdays_only must be a boolean", str(cm.exception))

    def test_invalid_date_types(self):
        """Test various invalid date types."""
        config = self.valid_config.copy()
        
        # Invalid start_date type (not string or date)
        config["tariffs"]["peak"] = {
            "price": 50.0,
            "times": [{"start": "14:00", "end": "20:00"}],
            "start_date": 123,
            "end_date": date(2024, 3, 31)
        }
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("start_date must be a date or date string", str(cm.exception))

        # Invalid end_date type  
        config["tariffs"]["peak"] = {
            "price": 50.0,
            "times": [{"start": "14:00", "end": "20:00"}],
            "start_date": date(2024, 1, 1),
            "end_date": 123
        }
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("end_date must be a date or date string", str(cm.exception))

        # Invalid end_date format
        config["tariffs"]["peak"] = {
            "price": 50.0,
            "times": [{"start": "14:00", "end": "20:00"}],
            "start_date": date(2024, 1, 1),
            "end_date": "bad-date-format"
        }
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("end_date has invalid format", str(cm.exception))

    def test_time_period_validation(self):
        """Test time period validation."""
        config = self.valid_config.copy()
        
        # Invalid time period type
        config["tariffs"]["peak"]["times"] = ["not a dict"]
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("time period 0 must be a dictionary", str(cm.exception))

        # Missing start time
        config["tariffs"]["peak"]["times"] = [{"end": "20:00"}]
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("must have 'start' field", str(cm.exception))

        # Missing end time
        config["tariffs"]["peak"]["times"] = [{"start": "14:00"}]
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("must have 'end' field", str(cm.exception))

        # Invalid time type
        config["tariffs"]["peak"]["times"] = [{"start": 14, "end": "20:00"}]
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("start must be a string", str(cm.exception))

    def test_time_format_validation(self):
        """Test time format validation."""
        config = self.valid_config.copy()
        
        # Invalid time format - no colon
        config["tariffs"]["peak"]["times"] = [{"start": "1400", "end": "20:00"}]
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("Time must be in HH:MM format", str(cm.exception))

        # Invalid hour
        config["tariffs"]["peak"]["times"] = [{"start": "25:00", "end": "20:00"}]
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("Hour must be between 00 and 23", str(cm.exception))

        # Invalid minute
        config["tariffs"]["peak"]["times"] = [{"start": "14:60", "end": "20:00"}]
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("Minute must be between 00 and 59", str(cm.exception))

        # Non-numeric hour
        config["tariffs"]["peak"]["times"] = [{"start": "ab:00", "end": "20:00"}]
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("invalid time format", str(cm.exception))

    def test_public_holidays_validation(self):
        """Test public holidays section validation."""
        config = self.valid_config.copy()
        
        # Invalid type
        config["public_holidays"] = "not a dict"
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("public_holidays configuration must be a dictionary", str(cm.exception))

        # Missing country
        config["public_holidays"] = {"region": "NSW"}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("public_holidays must have a 'country' field", str(cm.exception))

        # Invalid country type
        config["public_holidays"] = {"country": 123}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("public_holidays country must be a string", str(cm.exception))

        # Empty country
        config["public_holidays"] = {"country": ""}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("public_holidays country cannot be empty", str(cm.exception))

        # Invalid region type
        config["public_holidays"] = {"country": "AU", "region": 123}
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("public_holidays region must be a string", str(cm.exception))

    def test_valid_edge_cases(self):
        """Test valid edge cases that should pass validation."""
        # Configuration without public holidays
        config = {
            "pvoutput": {"extended_param": "v1"},
            "tariffs": {
                "offpeak": {"price": 0.0, "times": []}  # Zero price is valid
            }
        }
        validate_config(config)  # Should not raise

        # Overnight time period
        config = {
            "pvoutput": {"extended_param": "v12"},
            "tariffs": {
                "overnight": {
                    "price": 15.0,
                    "times": [{"start": "22:00", "end": "06:00"}]
                },
                "offpeak": {"price": 30.0, "times": []}
            }
        }
        validate_config(config)  # Should not raise


if __name__ == "__main__":
    unittest.main()