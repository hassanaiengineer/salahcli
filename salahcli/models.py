from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

class AsrMethod(Enum):
    SHAFII = 1
    HANAFI = 2

class HighLatitudeRule(Enum):
    NONE = auto()
    MIDDLE_OF_NIGHT = auto()
    ONE_SEVENTH = auto()
    ANGLE_BASED = auto()

@dataclass
class CalculationConfig:
    name: str
    fajr_angle: float
    isha_angle: float
    isha_is_interval: bool = False
    isha_minutes: int = 0

@dataclass
class PrayerTimesResult:
    fajr: float = 0.0
    sunrise: float = 0.0
    dhuhr: float = 0.0
    asr: float = 0.0
    maghrib: float = 0.0
    isha: float = 0.0
    imsak: float = 0.0
    duha: float = 0.0
    valid: bool = False
    error_message: Optional[str] = None
