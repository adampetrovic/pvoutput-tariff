import tempfile
import unittest
from unittest.mock import Mock, patch
import yaml

import click
from click.testing import CliRunner

from uploader import main


class MainCLITests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        
        # Create a test config
        self.test_config = {
            "pvoutput": {"extended_param": "v12"},
            "public_holidays": {"country": "AU", "region": "NSW"},
            "tariffs": {
                "peak": {
                    "price": 66.1815,
                    "times": [{"start": "14:00", "end": "20:00"}]
                },
                "offpeak": {"price": 31.3005, "times": []}
            }
        }

    def test_missing_api_credentials(self):
        """Test error when API credentials are missing"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(self.test_config, f)
            config_path = f.name

        # Test missing both credentials
        result = self.runner.invoke(main, ["--config", config_path])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Missing required API credentials", result.output)

        # Test missing system ID
        result = self.runner.invoke(main, [
            "--config", config_path,
            "--api-key", "test_key"
        ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Missing required API credentials", result.output)

        # Test missing API key
        result = self.runner.invoke(main, [
            "--config", config_path,
            "--system-id", "test_id"
        ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Missing required API credentials", result.output)

    def test_missing_config_keys(self):
        """Test error when required config keys are missing"""
        # Test missing tariffs
        bad_config = {"pvoutput": {"extended_param": "v12"}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(bad_config, f)
            config_path = f.name

        result = self.runner.invoke(main, [
            "--config", config_path,
            "--api-key", "test_key",
            "--system-id", "test_id"
        ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Missing required config key: tariffs", result.output)

        # Test missing pvoutput
        bad_config = {"tariffs": {"offpeak": {"price": 30, "times": []}}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(bad_config, f)
            config_path = f.name

        result = self.runner.invoke(main, [
            "--config", config_path,
            "--api-key", "test_key",
            "--system-id", "test_id"
        ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Missing required config key: pvoutput", result.output)

        # Test missing extended_param
        bad_config = {
            "tariffs": {"offpeak": {"price": 30, "times": []}},
            "pvoutput": {}
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(bad_config, f)
            config_path = f.name

        result = self.runner.invoke(main, [
            "--config", config_path,
            "--api-key", "test_key",
            "--system-id", "test_id"
        ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Missing 'extended_param' in pvoutput config", result.output)

    def test_missing_tariffs_in_config(self):
        """Test error when tariffs key exists but is None/empty"""
        bad_config = {
            "tariffs": None,  # Explicitly None
            "pvoutput": {"extended_param": "v12"}
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(bad_config, f)
            config_path = f.name

        result = self.runner.invoke(main, [
            "--config", config_path,
            "--api-key", "test_key",
            "--system-id", "test_id"
        ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Missing 'tariffs' in config", result.output)

    @patch("uploader.send_price_to_pvoutput")
    def test_successful_execution(self, mock_send):
        """Test successful execution of main function"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_send.return_value = mock_response

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(self.test_config, f)
            config_path = f.name

        result = self.runner.invoke(main, [
            "--config", config_path,
            "--api-key", "test_key",
            "--system-id", "test_id",
            "--timezone", "Australia/Sydney"
        ])

        self.assertEqual(result.exit_code, 0)
        mock_send.assert_called_once()


if __name__ == "__main__":
    unittest.main()