import logging
import sys
from datetime import date, datetime, time
from typing import Any, Dict, Optional

import click
import dateutil.tz
import holidays
import requests
import yaml

from config_schema import validate_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


# Helper function to check if current time is within a specified period
def is_time_in_period(current_time: time, start_str: str, end_str: str) -> bool:
    start_parts = list(map(int, start_str.split(":")))
    end_parts = list(map(int, end_str.split(":")))
    start_time = time(start_parts[0], start_parts[1])
    end_time = time(end_parts[0], end_parts[1])
    # Handle overnight periods
    if start_time <= end_time:
        return start_time <= current_time <= end_time
    else:  # Overnight period, e.g., 22:00-06:00
        return start_time <= current_time or current_time <= end_time


def is_public_holiday(public_holidays: Dict[str, Any], current_date: date) -> bool:
    if not public_holidays:
        return False

    country = public_holidays.get("country")
    state = public_holidays.get("region")
    if not country:
        return False
    return current_date in holidays.country_holidays(country, state)


# Function to load tariff information from a YAML file
def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from a YAML file.

    Args:
        config_path: Path to the configuration YAML file

    Returns:
        Dictionary containing the configuration

    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If the YAML is invalid
    """
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            if not config:
                raise ValueError("Configuration file is empty")
            
            # Validate configuration structure
            validate_config(config)
            
            logging.info(f"Successfully loaded config from {config_path}")
            return dict(config)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Invalid YAML in config file: {e}")
        raise
    except Exception as e:
        logging.error(f"Error loading config file: {e}")
        raise


def get_current_tariff(
    tariff_config: Dict[str, Any],
    public_holidays: Dict[str, Any],
    current_datetime: datetime,
) -> float:
    # Create a copy to avoid modifying the original dictionary
    tariff_config_copy = tariff_config.copy()
    # set offpeak as a fallback if no other tariff matches
    offpeak = tariff_config_copy.pop("offpeak", None)
    # go through the remaining tariffs
    for _, tariff in tariff_config_copy.items():
        periods = tariff.get("times", [])
        # check if current time matches any tariff
        if any(
            is_time_in_period(current_datetime.time(), period["start"], period["end"])
            for period in periods
        ):
            # if our tariff isn't seasonal, then we've found our tariff
            # as we have passed our seasonal tariffs already
            if "start_date" not in tariff and "end_date" not in tariff:
                return float(tariff["price"])
            else:
                weekdays_only = tariff.get("weekdays_only", False)
                is_weekday = current_datetime.weekday() < 5
                is_holiday = is_public_holiday(public_holidays, current_datetime.date())
                if not is_holiday and (
                    (weekdays_only and is_weekday) or not weekdays_only
                ):
                    # if we are in the range of the start and end date then we found our tariff
                    if (
                        tariff["start_date"]
                        <= current_datetime.date()
                        <= tariff["end_date"]
                    ):
                        return float(tariff["price"])

    return float(offpeak["price"]) if offpeak else 0.0


def send_price_to_pvoutput(
    api_key: str, system_id: str, extended_param: str, price: float, now: datetime
) -> requests.Response:
    """Send price data to PVOutput API.

    Args:
        api_key: PVOutput API key
        system_id: PVOutput system ID
        extended_param: Extended parameter name (e.g., 'v12')
        price: Current tariff price
        now: Current datetime

    Returns:
        Response object from the API call

    Raises:
        requests.RequestException: If the API call fails
    """
    date_str = now.strftime("%Y%m%d")
    # pvoutput expects a data feed sent to an extended parameter every 5 minutes
    # e.g. 00, 05, 10, ..., 55
    minute = now.minute - now.minute % 5
    time_str = f"{now.hour:02d}:{minute:02d}"

    url = "https://pvoutput.org/service/r2/addstatus.jsp"
    headers = {
        "X-Pvoutput-Apikey": api_key,
        "X-Pvoutput-SystemId": system_id,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = f"{extended_param}={price}&d={date_str}&t={time_str}"

    try:
        logging.info(f"Sending tariff {price}c to PVOutput for {date_str} {time_str}")
        response = requests.post(url, headers=headers, data=data, timeout=30)
        response.raise_for_status()
        logging.info(f"Successfully sent data to PVOutput: {response.status_code}")
        return response
    except requests.exceptions.Timeout:
        logging.error("Request to PVOutput API timed out")
        raise
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error from PVOutput API: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending data to PVOutput: {e}")
        raise


# Main CLI command
@click.command()
@click.option(
    "--config",
    "config_path",
    default="/config/config.yaml",
    help="Path to the configuration YAML file.",
)
@click.option(
    "--api-key",
    "api_key",
    envvar="PVOUTPUT_API_KEY",
    required=False,
    help="PVOutput API key.",
)
@click.option(
    "--system-id",
    "system_id",
    envvar="PVOUTPUT_SYSTEM_ID",
    required=False,
    help="PVOutput System ID.",
)
@click.option(
    "--timezone",
    "timezone",
    envvar="TZ",
    default="Australia/Sydney",
    required=True,
    help="Timezone for calculations.",
)
def main(
    config_path: str, api_key: Optional[str], system_id: Optional[str], timezone: str
) -> None:
    """Main CLI command to calculate and send tariff data to PVOutput."""
    try:
        # Validate required parameters
        if not api_key or not system_id:
            logging.error("Both --api-key and --system-id are required")
            raise click.ClickException("Missing required API credentials")

        config = load_config(config_path)

        # Validate config structure
        required_keys = ["tariffs", "pvoutput"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")

        if "extended_param" not in config["pvoutput"]:
            raise ValueError("Missing 'extended_param' in pvoutput config")

        current_datetime = datetime.now(dateutil.tz.gettz(timezone))
        logging.info(f"Calculating tariff for {current_datetime}")

        tariffs = config.get("tariffs")
        public_holidays = config.get("public_holidays")
        if not tariffs:
            raise ValueError("Missing 'tariffs' in config")

        current_tariff = get_current_tariff(
            tariffs, public_holidays or {}, current_datetime
        )

        send_price_to_pvoutput(
            api_key,
            system_id,
            config["pvoutput"]["extended_param"],
            current_tariff,
            current_datetime,
        )

        logging.info(f"Operation completed successfully. Tariff: {current_tariff}c")

    except Exception as e:
        logging.error(f"Application failed: {e}")
        raise click.ClickException(str(e))


if __name__ == "__main__":
    main()
