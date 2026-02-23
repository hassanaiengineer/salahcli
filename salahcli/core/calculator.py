import math
from typing import Tuple, Optional

from ..models import PrayerTimesResult, AsrMethod, HighLatitudeRule, CalculationConfig
from .solar import (
    deg2rad, rad2deg, clamp, normalize_time, calculate_day_of_year,
    validate_inputs, calculate_solar_parameters
)
from .high_latitude import apply_high_latitude_adjustments

class PrayerTimesCalculator:
    def __init__(self, latitude: float, longitude: float, timezone_offset_minutes: int):
        self._latitude = latitude
        self._longitude = longitude
        self._timezone_offset_minutes = timezone_offset_minutes
        
        self._adj_fajr = 0
        self._adj_sunrise = 0
        self._adj_dhuhr = 0
        self._adj_asr = 0
        self._adj_maghrib = 0
        self._adj_isha = 0
        
        self._fajr_angle = 18.0
        self._isha_angle = 17.0
        self._isha_is_interval = False
        self._isha_minutes = 0
        
        self._asr_method = AsrMethod.SHAFII
        self._high_lat_rule = HighLatitudeRule.NONE
        
        self._imsak_offset_minutes = 10
        self._duha_angle = 4.5
        
        self._initialized = False
        if -90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0:
            self._initialized = True

    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def latitude(self) -> float:
        return self._latitude

    def is_high_latitude(self) -> bool:
        return abs(self._latitude) > 66.5

    def set_calculation_method(self, config: CalculationConfig) -> None:
        self._fajr_angle = config.fajr_angle
        self._isha_angle = config.isha_angle
        self._isha_is_interval = config.isha_is_interval
        self._isha_minutes = config.isha_minutes

    def set_custom_method(self, fajr_angle: float, isha_angle: float, isha_is_interval: bool = False, isha_minutes: int = 0) -> None:
        self._fajr_angle = fajr_angle
        self._isha_angle = isha_angle
        self._isha_is_interval = isha_is_interval
        self._isha_minutes = isha_minutes

    def set_asr_method(self, method: AsrMethod) -> None:
        self._asr_method = method

    def set_high_latitude_rule(self, rule: HighLatitudeRule) -> None:
        self._high_lat_rule = rule

    def set_adjustments(self, adj_fajr: int, adj_sunrise: int, adj_dhuhr: int, 
                        adj_asr: int, adj_maghrib: int, adj_isha: int) -> None:
        self._adj_fajr = adj_fajr
        self._adj_sunrise = adj_sunrise
        self._adj_dhuhr = adj_dhuhr
        self._adj_asr = adj_asr
        self._adj_maghrib = adj_maghrib
        self._adj_isha = adj_isha

    def set_imsak_offset(self, minutes_before_fajr: int) -> None:
        self._imsak_offset_minutes = minutes_before_fajr

    def set_duha_angle(self, degrees_above_horizon: float) -> None:
        self._duha_angle = degrees_above_horizon

    def _calculate_solar_noon(self, eq_time: float) -> float:
        return 720.0 - 4.0 * self._longitude - eq_time + self._timezone_offset_minutes

    def _calculate_time_for_angle(self, angle: float, solar_noon: float, solar_dec: float, is_morning: bool) -> float:
        lat_rad = deg2rad(self._latitude)
        
        # Hour angle calculation with defensive clamping
        cos_h = (math.sin(deg2rad(angle)) - math.sin(lat_rad) * math.sin(solar_dec)) / (math.cos(lat_rad) * math.cos(solar_dec))
        cos_h = clamp(cos_h, -1.0, 1.0)
        
        hour_angle = math.acos(cos_h)
        delta = rad2deg(hour_angle) * 4.0
        
        return solar_noon - delta if is_morning else solar_noon + delta

    def _calculate_asr_time(self, solar_noon: float, solar_dec: float) -> float:
        lat_rad = deg2rad(self._latitude)
        shadow_factor = 2.0 if self._asr_method == AsrMethod.HANAFI else 1.0
        
        angle = math.atan(1.0 / (shadow_factor + math.tan(abs(lat_rad - solar_dec))))
        
        cos_h = (math.sin(angle) - math.sin(lat_rad) * math.sin(solar_dec)) / (math.cos(lat_rad) * math.cos(solar_dec))
        cos_h = clamp(cos_h, -1.0, 1.0)
        
        hour_angle = math.acos(cos_h)
        return solar_noon + rad2deg(hour_angle) * 4.0

    def calculate(self, day: int, month: int, year: int) -> PrayerTimesResult:
        return self.calculate_with_offset(day, month, year, 0)

    def calculate_with_offset(self, day: int, month: int, year: int, dst_minutes: int) -> PrayerTimesResult:
        result = PrayerTimesResult()
        
        if not self._initialized:
            result.error_message = "Invalid coordinates"
            return result
            
        if not validate_inputs(day, month, year):
            result.error_message = "Invalid date"
            return result
            
        day_of_year = calculate_day_of_year(day, month, year)
        eq_time, solar_dec = calculate_solar_parameters(day_of_year)
        solar_noon = self._calculate_solar_noon(eq_time)
        
        # Astronomical times
        result.fajr = self._calculate_time_for_angle(-self._fajr_angle, solar_noon, solar_dec, True)
        result.sunrise = self._calculate_time_for_angle(-0.833, solar_noon, solar_dec, True)
        result.dhuhr = solar_noon
        result.asr = self._calculate_asr_time(solar_noon, solar_dec)
        result.maghrib = self._calculate_time_for_angle(-0.833, solar_noon, solar_dec, False)
        
        if self._isha_is_interval:
            result.isha = result.maghrib + self._isha_minutes
        else:
            result.isha = self._calculate_time_for_angle(-self._isha_angle, solar_noon, solar_dec, False)
            
        apply_high_latitude_adjustments(result, solar_dec, self._high_lat_rule, self._fajr_angle, self._isha_angle)
        
        # Imsak & Duha
        result.imsak = normalize_time(result.fajr - self._imsak_offset_minutes)
        result.duha = self._calculate_time_for_angle(self._duha_angle, solar_noon, solar_dec, True)
        
        # Apply time offsets and normalize
        result.fajr = normalize_time(result.fajr + self._adj_fajr + dst_minutes)
        result.sunrise = normalize_time(result.sunrise + self._adj_sunrise + dst_minutes)
        result.dhuhr = normalize_time(result.dhuhr + self._adj_dhuhr + dst_minutes)
        result.asr = normalize_time(result.asr + self._adj_asr + dst_minutes)
        result.maghrib = normalize_time(result.maghrib + self._adj_maghrib + dst_minutes)
        result.isha = normalize_time(result.isha + self._adj_isha + dst_minutes)
        result.imsak = normalize_time(result.imsak + self._adj_fajr + dst_minutes)
        result.duha = normalize_time(result.duha + self._adj_sunrise + dst_minutes)
        
        result.valid = True
        return result

    @staticmethod
    def format_time_12(minutes: float) -> str:
        hour = int(minutes / 60.0)
        minute = int(round(minutes - (hour * 60.0)))
        
        if minute >= 60:
            minute = 0
            hour += 1
            
        hour = hour % 24
        
        h = hour % 12
        if h == 0:
            h = 12
        period = "AM" if hour < 12 else "PM"
        
        return f"{h}:{minute:02d} {period}"

    @staticmethod
    def format_time_24(minutes: float) -> str:
        hour = int(minutes / 60.0)
        minute = int(round(minutes - (hour * 60.0)))
        
        if minute >= 60:
            minute = 0
            hour += 1
            
        hour = hour % 24
        return f"{hour:02d}:{minute:02d}"
