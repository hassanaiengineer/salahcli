import math
from typing import Tuple

PI = math.pi

def deg2rad(degrees: float) -> float:
    return degrees * (PI / 180.0)

def rad2deg(radians: float) -> float:
    return radians * (180.0 / PI)

def clamp(value: float, min_val: float, max_val: float) -> float:
    if value < min_val: return min_val
    if value > max_val: return max_val
    return value

def normalize_time(time_val: float) -> float:
    while time_val < 0:
        time_val += 1440.0
    while time_val >= 1440.0:
        time_val -= 1440.0
    return time_val

def calculate_day_of_year(day: int, month: int, year: int) -> int:
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    # Handle leap years
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        days_in_month[1] = 29
        
    day_of_year = day
    for i in range(month - 1):
        day_of_year += days_in_month[i]
        
    return day_of_year

def validate_inputs(day: int, month: int, year: int) -> bool:
    if month < 1 or month > 12: return False
    if day < 1 or day > 31: return False
    if year < 1900 or year > 2100: return False
    
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        days_in_month[1] = 29
        
    if day > days_in_month[month - 1]: return False
    return True

def calculate_solar_parameters(day_of_year: int) -> Tuple[float, float]:
    # Using NOAA solar calculations (more accurate)
    gamma = 2.0 * PI / 365.0 * (day_of_year - 1)
    
    # Equation of time in minutes
    eq_time = 229.18 * (
        0.000075 +
        0.001868 * math.cos(gamma) - 0.032077 * math.sin(gamma) -
        0.014615 * math.cos(2 * gamma) - 0.040849 * math.sin(2 * gamma)
    )
    
    # Solar declination in radians
    solar_dec = (
        0.006918 - 0.399912 * math.cos(gamma) + 0.070257 * math.sin(gamma) -
        0.006758 * math.cos(2 * gamma) + 0.000907 * math.sin(2 * gamma) -
        0.002697 * math.cos(3 * gamma) + 0.00148 * math.sin(3 * gamma)
    )
    
    return eq_time, solar_dec
