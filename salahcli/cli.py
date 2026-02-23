import argparse
import json
import sys
import urllib.request
from datetime import datetime, timedelta

from .core.calculator import PrayerTimesCalculator
from .methods import CalculationMethods
from .models import CalculationConfig
from .config import load_config, save_config, config_exists
from .ui.render import render_today, render_next

def get_method_by_name(name: str) -> CalculationConfig:
    methods = {
        "MWL": CalculationMethods.MWL,
        "ISNA": CalculationMethods.ISNA,
        "EGYPT": CalculationMethods.EGYPT,
        "MAKKAH": CalculationMethods.MAKKAH,
        "KARACHI": CalculationMethods.KARACHI,
        "TEHRAN": CalculationMethods.TEHRAN,
        "JAFARI": CalculationMethods.JAFARI,
        "GULF": CalculationMethods.GULF,
        "KUWAIT": CalculationMethods.KUWAIT,
        "QATAR": CalculationMethods.QATAR,
        "SINGAPORE": CalculationMethods.SINGAPORE,
        "FRANCE": CalculationMethods.FRANCE,
        "TURKEY": CalculationMethods.TURKEY,
        "RUSSIA": CalculationMethods.RUSSIA,
        "DUBAI": CalculationMethods.DUBAI,
        "JAKIM": CalculationMethods.JAKIM,
        "TUNISIA": CalculationMethods.TUNISIA,
        "ALGERIA": CalculationMethods.ALGERIA,
        "INDONESIA": CalculationMethods.INDONESIA,
        "MOROCCO": CalculationMethods.MOROCCO,
        "PORTUGAL": CalculationMethods.PORTUGAL,
        "JORDAN": CalculationMethods.JORDAN,
    }
    return methods.get(name.upper(), CalculationMethods.MWL)

def init_command():
    print("Detecting location via IP...")
    try:
        url = "http://ip-api.com/json?fields=status,message,country,city,lat,lon,timezone,offset"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
        
        if data.get("status") != "success":
            print("Failed to detect location.")
            sys.exit(1)
            
        lat = data.get("lat")
        lon = data.get("lon")
        tz_offset_minutes = int(data.get("offset", 0) / 60)
        city = data.get("city")
        country = data.get("country")
        
        print(f"Detected Location: {city}, {country} (Lat: {lat}, Lon: {lon})")
        ans = input("Save this configuration? [Y/n]: ").strip().lower()
        if ans in ('', 'y', 'yes'):
            method = "MWL"
            save_config(lat, lon, tz_offset_minutes, method)
            print("Configuration saved successfully.")
        else:
            print("Configuration aborted.")
    except Exception as e:
        print(f"Error detecting location: {e}")
        sys.exit(1)

def print_today(config):
    now = datetime.now()
    calc = PrayerTimesCalculator(config["lat"], config["lon"], config["tz"])
    if not calc.is_initialized():
        print("Invalid coordinates in config.")
        return
        
    method_name = config.get("method", "MWL")
    method = get_method_by_name(method_name)
    calc.set_calculation_method(method)
    
    result = calc.calculate(now.day, now.month, now.year)
    if not result.valid:
        print(f"Error calculating prayer times: {result.error_message}")
        return
        
    render_today(config, calc, result, method_name)

def next_prayer(config):
    now = datetime.now()
    calc = PrayerTimesCalculator(config["lat"], config["lon"], config["tz"])
    if not calc.is_initialized():
        print("Invalid coordinates in config.")
        return
        
    method_name = config.get("method", "MWL")
    method = get_method_by_name(method_name)
    calc.set_calculation_method(method)
    
    # Check today's times
    result = calc.calculate(now.day, now.month, now.year)
    if not result.valid:
        print("Error calculating prayer times.")
        return
        
    current_minutes = now.hour * 60 + now.minute + now.second / 60.0
    
    prayers = [
        ("Imsak", result.imsak),
        ("Fajr", result.fajr),
        ("Sunrise", result.sunrise),
        ("Duha", result.duha),
        ("Dhuhr", result.dhuhr),
        ("Asr", result.asr),
        ("Maghrib", result.maghrib),
        ("Isha", result.isha)
    ]
    
    next_p_name = None
    next_p_time = None
    
    for name, p_time in prayers:
        if p_time > current_minutes:
            next_p_name = name
            next_p_time = p_time
            break
            
    # If all prayers today have passed, get tomorrow's Imsak
    if not next_p_name:
        tomorrow = now + timedelta(days=1)
        res_tomorrow = calc.calculate(tomorrow.day, tomorrow.month, tomorrow.year)
        if res_tomorrow.valid:
            next_p_name = "Imsak"
            next_p_time = res_tomorrow.imsak + 1440.0 # add 24 hours in minutes
            
    if not next_p_name:
        print("Could not determine next prayer.")
        return
        
    diff_minutes = next_p_time - current_minutes
    hours = int(diff_minutes // 60)
    minutes = int(diff_minutes % 60)
    
    render_next(next_p_name, hours, minutes)

def main():
    parser = argparse.ArgumentParser(description="salahcli - Islamic prayer times CLI")
    subparsers = parser.add_subparsers(dest="command", required=False)
    
    subparsers.add_parser("init", help="Initialize configuration using IP geolocation")
    subparsers.add_parser("today", help="Show prayer times for today")
    subparsers.add_parser("next", help="Show the next upcoming prayer and countdown")
    
    args = parser.parse_args()
    
    if args.command is None:
        args.command = "today"
    
    if args.command == "init":
        init_command()
        return
        
    if not config_exists():
        print("Configuration not found. Please run 'salahcli init' first.")
        sys.exit(1)
        
    config = load_config()
    
    if args.command == "today":
        print_today(config)
    elif args.command == "next":
        next_prayer(config)

if __name__ == "__main__":
    main()
