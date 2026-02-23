from ..models import PrayerTimesResult, HighLatitudeRule

def night_fraction(angle: float, rule: HighLatitudeRule) -> float:
    if rule == HighLatitudeRule.ONE_SEVENTH:
        return 1.0 / 7.0
    elif rule == HighLatitudeRule.MIDDLE_OF_NIGHT:
        return 0.5
    elif rule == HighLatitudeRule.ANGLE_BASED:
        return angle / 60.0
    return 0.0

def apply_high_latitude_adjustments(
    times: PrayerTimesResult,
    solar_dec: float,
    rule: HighLatitudeRule,
    fajr_angle: float,
    isha_angle: float
) -> None:
    if rule == HighLatitudeRule.NONE:
        return
        
    night_length = (times.sunrise - times.maghrib) % 1440.0
    if night_length < 0:
        night_length += 1440.0
        
    fajr_diff = times.sunrise - times.fajr
    isha_diff = times.isha - times.maghrib
    
    if fajr_diff < 0 or fajr_diff > night_length * 0.5:
        portion = night_fraction(fajr_angle, rule)
        times.fajr = times.sunrise - night_length * portion
        
    if isha_diff < 0 or isha_diff > night_length * 0.5:
        portion = night_fraction(isha_angle, rule)
        times.isha = times.maghrib + night_length * portion
