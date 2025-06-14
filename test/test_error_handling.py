import os
import tempfile
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

import requests
import yaml

from uploader import load_config, send_price_to_pvoutput, main


class ErrorHandlingTests(unittest.TestCase):
    def test_load_config_file_not_found(self):
        """Test error handling when config file doesn't exist"""
        with self.assertRaises(FileNotFoundError):
            load_config("/nonexistent/path/config.yaml")

    def test_load_config_empty_file(self):
        """Test error handling when config file is empty"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            with self.assertRaises(ValueError) as cm:
                load_config(temp_path)
            self.assertIn("Configuration file is empty", str(cm.exception))
        finally:
            os.unlink(temp_path)

    def test_load_config_invalid_yaml(self):
        """Test error handling when YAML is invalid"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name

        try:
            with self.assertRaises(yaml.YAMLError):
                load_config(temp_path)
        finally:
            os.unlink(temp_path)

    @patch("requests.post")
    def test_send_price_timeout(self, mock_post):
        """Test timeout handling in API call"""
        mock_post.side_effect = requests.exceptions.Timeout()
        
        from datetime import datetime
        
        with self.assertRaises(requests.exceptions.Timeout):
            send_price_to_pvoutput(
                "test_key", "test_id", "v12", 25.0, datetime.now()
            )

    @patch("requests.post")
    def test_send_price_http_error(self, mock_post):
        """Test HTTP error handling in API call"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_post.return_value = mock_response
        
        from datetime import datetime
        
        with self.assertRaises(requests.exceptions.HTTPError):
            send_price_to_pvoutput(
                "test_key", "test_id", "v12", 25.0, datetime.now()
            )

    @patch("requests.post")
    def test_send_price_request_exception(self, mock_post):
        """Test general request exception handling"""
        mock_post.side_effect = requests.exceptions.RequestException()
        
        from datetime import datetime
        
        with self.assertRaises(requests.exceptions.RequestException):
            send_price_to_pvoutput(
                "test_key", "test_id", "v12", 25.0, datetime.now()
            )

    @patch("requests.post")
    def test_send_price_success(self, mock_post):
        """Test successful API call"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        from datetime import datetime
        
        result = send_price_to_pvoutput(
            "test_key", "test_id", "v12", 25.0, datetime.now()
        )
        
        self.assertEqual(result, mock_response)
        mock_response.raise_for_status.assert_called_once()


if __name__ == "__main__":
    unittest.main()