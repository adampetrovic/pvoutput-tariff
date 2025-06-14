"""Configuration schema validation for PVOutput Tariff application."""

from datetime import date
from typing import Any, Dict, List, Optional, Union


def validate_config(config: Dict[str, Any]) -> None:
    """Validate the configuration structure and content.
    
    Args:
        config: The configuration dictionary to validate
        
    Raises:
        ValueError: If the configuration is invalid
    """
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary")
    
    # Validate required top-level keys
    required_keys = ["pvoutput", "tariffs"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")
    
    # Validate pvoutput section
    _validate_pvoutput_config(config["pvoutput"])
    
    # Validate tariffs section
    _validate_tariffs_config(config["tariffs"])
    
    # Validate optional public_holidays section
    if "public_holidays" in config:
        _validate_public_holidays_config(config["public_holidays"])


def _validate_pvoutput_config(pvoutput_config: Any) -> None:
    """Validate the pvoutput configuration section."""
    if not isinstance(pvoutput_config, dict):
        raise ValueError("pvoutput configuration must be a dictionary")
    
    if "extended_param" not in pvoutput_config:
        raise ValueError("pvoutput configuration must include 'extended_param'")
    
    extended_param = pvoutput_config["extended_param"]
    if not isinstance(extended_param, str):
        raise ValueError("extended_param must be a string")
    
    # Validate extended parameter format (v1-v12)
    if not extended_param.startswith("v") or not extended_param[1:].isdigit():
        raise ValueError("extended_param must be in format 'v1' to 'v12'")
    
    param_num = int(extended_param[1:])
    if param_num < 1 or param_num > 12:
        raise ValueError("extended_param must be between v1 and v12")


def _validate_tariffs_config(tariffs_config: Any) -> None:
    """Validate the tariffs configuration section."""
    if not isinstance(tariffs_config, dict):
        raise ValueError("tariffs configuration must be a dictionary")
    
    if not tariffs_config:
        raise ValueError("tariffs configuration cannot be empty")
    
    # Validate that offpeak tariff exists (it's the fallback)
    if "offpeak" not in tariffs_config:
        raise ValueError("tariffs must include an 'offpeak' tariff as fallback")
    
    # Validate each tariff
    for tariff_name, tariff_config in tariffs_config.items():
        _validate_single_tariff(tariff_name, tariff_config)


def _validate_single_tariff(tariff_name: str, tariff_config: Any) -> None:
    """Validate a single tariff configuration."""
    if not isinstance(tariff_config, dict):
        raise ValueError(f"Tariff '{tariff_name}' must be a dictionary")
    
    # Validate price
    if "price" not in tariff_config:
        raise ValueError(f"Tariff '{tariff_name}' must have a 'price' field")
    
    price = tariff_config["price"]
    if not isinstance(price, (int, float)):
        raise ValueError(f"Tariff '{tariff_name}' price must be a number")
    
    if price < 0:
        raise ValueError(f"Tariff '{tariff_name}' price cannot be negative")
    
    # Validate times
    if "times" not in tariff_config:
        raise ValueError(f"Tariff '{tariff_name}' must have a 'times' field")
    
    times = tariff_config["times"]
    if not isinstance(times, list):
        raise ValueError(f"Tariff '{tariff_name}' times must be a list")
    
    # Validate each time period
    for i, time_period in enumerate(times):
        _validate_time_period(tariff_name, i, time_period)
    
    # Validate optional seasonal fields
    seasonal_fields = ["start_date", "end_date"]
    has_seasonal = any(field in tariff_config for field in seasonal_fields)
    
    if has_seasonal:
        for field in seasonal_fields:
            if field not in tariff_config:
                raise ValueError(
                    f"Tariff '{tariff_name}' with seasonal dates must have both "
                    f"start_date and end_date"
                )
        
        start_date = tariff_config["start_date"]
        end_date = tariff_config["end_date"]
        
        # Convert string dates to date objects if needed
        if isinstance(start_date, str):
            try:
                start_date = date.fromisoformat(start_date)
            except ValueError:
                raise ValueError(f"Tariff '{tariff_name}' start_date has invalid format")
        elif not isinstance(start_date, date):
            raise ValueError(f"Tariff '{tariff_name}' start_date must be a date or date string")
        
        if isinstance(end_date, str):
            try:
                end_date = date.fromisoformat(end_date)
            except ValueError:
                raise ValueError(f"Tariff '{tariff_name}' end_date has invalid format")
        elif not isinstance(end_date, date):
            raise ValueError(f"Tariff '{tariff_name}' end_date must be a date or date string")
        
        if start_date >= end_date:
            raise ValueError(
                f"Tariff '{tariff_name}' start_date must be before end_date"
            )
    
    # Validate optional weekdays_only field
    if "weekdays_only" in tariff_config:
        weekdays_only = tariff_config["weekdays_only"]
        if not isinstance(weekdays_only, bool):
            raise ValueError(
                f"Tariff '{tariff_name}' weekdays_only must be a boolean"
            )


def _validate_time_period(tariff_name: str, index: int, time_period: Any) -> None:
    """Validate a single time period within a tariff."""
    if not isinstance(time_period, dict):
        raise ValueError(
            f"Tariff '{tariff_name}' time period {index} must be a dictionary"
        )
    
    required_fields = ["start", "end"]
    for field in required_fields:
        if field not in time_period:
            raise ValueError(
                f"Tariff '{tariff_name}' time period {index} must have '{field}' field"
            )
    
    # Validate time format
    for field in required_fields:
        time_str = time_period[field]
        if not isinstance(time_str, str):
            raise ValueError(
                f"Tariff '{tariff_name}' time period {index} {field} must be a string"
            )
        
        _validate_time_format(tariff_name, index, field, time_str)


def _validate_time_format(
    tariff_name: str, index: int, field: str, time_str: str
) -> None:
    """Validate time format (HH:MM)."""
    try:
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError("Time must be in HH:MM format")
        
        hour, minute = parts
        hour_int = int(hour)
        minute_int = int(minute)
        
        if hour_int < 0 or hour_int > 23:
            raise ValueError("Hour must be between 00 and 23")
        
        if minute_int < 0 or minute_int > 59:
            raise ValueError("Minute must be between 00 and 59")
            
    except (ValueError, IndexError) as e:
        raise ValueError(
            f"Tariff '{tariff_name}' time period {index} {field} has invalid "
            f"time format '{time_str}': {e}"
        )


def _validate_public_holidays_config(holidays_config: Any) -> None:
    """Validate the public holidays configuration section."""
    if not isinstance(holidays_config, dict):
        raise ValueError("public_holidays configuration must be a dictionary")
    
    if "country" not in holidays_config:
        raise ValueError("public_holidays must have a 'country' field")
    
    country = holidays_config["country"]
    if not isinstance(country, str):
        raise ValueError("public_holidays country must be a string")
    
    if not country:
        raise ValueError("public_holidays country cannot be empty")
    
    # Validate optional region field
    if "region" in holidays_config:
        region = holidays_config["region"]
        if not isinstance(region, str):
            raise ValueError("public_holidays region must be a string")