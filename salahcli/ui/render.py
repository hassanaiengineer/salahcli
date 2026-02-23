from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .theme import salah_theme
from .table import prayer_table

console = Console(theme=salah_theme)

def render_today(config: dict, calc, result, method: str) -> None:
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    
    # Header Panel
    header_text = Text()
    header_text.append("📅 ", style="title")
    header_text.append(f"{date_str}\n", style="header")
    header_text.append(f"📍 {config['lat']:.2f}, {config['lon']:.2f} ", style="label")
    header_text.append(f"({method})", style="muted")
    
    panel = Panel.fit(
        header_text,
        title="[title]🕌 salahcli[/title]",
        border_style="cyan"
    )
    console.print(panel)
    console.print()
    
    # Table
    table = prayer_table()
    
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
    
    for name, p_time in prayers:
        formatted_time = calc.format_time_24(p_time)
        table.add_row(
            f"[label]{name}[/label]", 
            f"[time]{formatted_time}[/time]"
        )
        
    console.print(table)

def render_next(next_p_name: str, hours: int, minutes: int) -> None:
    console.print(f"🕌 [muted]Next Prayer:[/muted] [accent]{next_p_name}[/accent]")
    console.print(f"⏳ [muted]Starts in:[/muted] [time]{hours:02d}h {minutes:02d}m[/time]")
