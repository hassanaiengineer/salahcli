import pytest
from salahcli.core.calculator import PrayerTimesCalculator
from salahcli.methods import CalculationMethods
from salahcli.models import HighLatitudeRule

def test_montreal():
    # Example from README: Montreal coordinates and timezone (UTC-5 = -300 minutes)
    calc = PrayerTimesCalculator(45.5017, -73.5673, -300)
    assert calc.is_initialized()
    
    calc.set_calculation_method(CalculationMethods.ISNA)
    if calc.is_high_latitude():
        calc.set_high_latitude_rule(HighLatitudeRule.MIDDLE_OF_NIGHT)
        
    result = calc.calculate(22, 12, 2025)
    
    assert result.valid
    # 6:01 AM is mentioned in the README for Montreal on 22/12/2025
    fajr_time = calc.format_time_12(result.fajr)
    assert fajr_time == "6:01 AM"

def test_kuala_lumpur_imsak():
    # Example from README: Kuala Lumpur (UTC+8 = 480 minutes)
    calc = PrayerTimesCalculator(3.1390, 101.6869, 480)
    calc.set_calculation_method(CalculationMethods.JAKIM)
    calc.set_imsak_offset(18)
    
    result = calc.calculate(1, 3, 2026)
    assert result.valid
    assert result.imsak < result.fajr
    
def test_validation():
    calc = PrayerTimesCalculator(95.0, -73.5673, -300)
    assert not calc.is_initialized()
    
    calc_valid = PrayerTimesCalculator(45.0, -73.0, -300)
    result = calc_valid.calculate(32, 13, 2025)
    assert not result.valid
    assert result.error_message == "Invalid date"

def test_tromso():
    calc = PrayerTimesCalculator(69.65, 18.95, 60)
    calc.set_high_latitude_rule(HighLatitudeRule.MIDDLE_OF_NIGHT)
    result = calc.calculate(22, 12, 2025)
    assert result.valid
