from datetime import datetime, time
import yaml

import click
import requests
import pytz
import time as time_module

# Helper function to check if current time is within a specified period
def is_time_in_period(current_time, start_str, end_str):
    start_time = time(*map(int, start_str.split(':')))
    end_time = time(*map(int, end_str.split(':')))
    # Handle overnight periods
    if start_time <= end_time:
        return start_time <= current_time <= end_time
    else:  # Overnight period, e.g., 22:00-06:00
        return start_time <= current_time or current_time <= end_time

# Function to load tariff information from a YAML file
def load_tariff_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

# Function to determine the current tariff
def get_current_tariff(tariff_config, current_datetime):
    now = current_datetime
    current_time = now.time()

    # Check for super offpeak and EV offpeak first since they are the most specific
    if 'super_offpeak' in tariff_config['tariffs'] and any(is_time_in_period(current_time, period['start'], period['end']) for period in tariff_config['tariffs']['super_offpeak'].get('times', [])):
        return tariff_config['tariffs']['super_offpeak']['price']
    if 'ev_offpeak' in tariff_config['tariffs'] and any(is_time_in_period(current_time, period['start'], period['end']) for period in tariff_config['tariffs']['ev_offpeak'].get('times', [])):
        return tariff_config['tariffs']['ev_offpeak']['price']

    # Check peak periods for both summer and winter
    for season in ['peak_summer', 'peak_winter']:
        if season in tariff_config['tariffs']:
            peak_info = tariff_config['tariffs'][season]
            if peak_info['start_date'] <= now.date() <= peak_info['end_date']:
                for period in peak_info['times']:
                    if is_time_in_period(current_time, period['start'], period['end']):
                        return peak_info['price']

    # Shoulder pricing applies at specific times not covered by peak or offpeak
    if 'shoulder' in tariff_config['tariffs'] and any(is_time_in_period(current_time, period['start'], period['end']) for period in tariff_config['tariffs']['shoulder'].get('times', [])):
        return tariff_config['tariffs']['shoulder']['price']

    # Default to offpeak for all other times
    return tariff_config['tariffs']['offpeak']['price']

# Function to send the POST request to PVOutput
def send_price_to_pvoutput(api_key, system_id, price, now):
    date_str = now.strftime('%Y%m%d')
    # Round down the current time to the nearest 5 minutes
    time_str = now.strftime('%H:%M')
    minute = now.minute - now.minute % 5
    time_str = f"{now.hour:02d}:{minute:02d}"
    url = "https://pvoutput.org/service/r2/addstatus.jsp"
    headers = {
        'X-Pvoutput-Apikey': api_key,
        'X-Pvoutput-SystemId': system_id,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = f"v10={price}&d={date_str}&t={time_str}"
    response = requests.post(url, headers=headers, data=data)
    return response

# Main CLI command
@click.command()
@click.option('--config', 'config_path', default='config.yaml', help='Path to the configuration YAML file.')
@click.option('--api-key', 'api_key', envvar='PVOUTPUT_API_KEY', required=False, help='PVOutput API key.')
@click.option('--system-id', 'system_id', envvar='PVOUTPUT_SYSTEM_ID', required=False, help='PVOutput System ID.')
@click.option('--timezone', 'timezone', envvar='TZ', default='Australia/Sydney', required=True, help='PVOutput System ID.')
def main(config_path, api_key, system_id, timezone):
    tariff_config = load_tariff_config(config_path)
    current_datetime = datetime.now(pytz.timezone(timezone))
    current_tariff = get_current_tariff(tariff_config, current_datetime)
    response = send_price_to_pvoutput(api_key, system_id, current_tariff, current_datetime)
    print(f"Sent tariff {current_tariff}c to PVOutput. Response: {response.status_code} - {response.text}")

if __name__ == '__main__':
    main()