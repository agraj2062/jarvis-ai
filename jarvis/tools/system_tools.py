import datetime
import webbrowser

import psutil

from . import tool


@tool("Get the current local date and time.")
def current_time() -> str:
    return datetime.datetime.now().strftime("It is %A, %d %B %Y, %H:%M.")


@tool("Report the health of the computer Jarvis runs on: CPU, memory and battery.")
def system_status() -> str:
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    out = f"CPU at {cpu:.0f} percent, memory at {mem:.0f} percent."
    batt = psutil.sensors_battery()
    if batt:
        plug = "charging" if batt.power_plugged else "on battery"
        out += f" Battery at {batt.percent:.0f} percent, {plug}."
    return out


@tool(
    "Open a web page (http or https only) in the user's browser.",
    {
        "type": "object",
        "properties": {"url": {"type": "string", "description": "Full URL starting with https://"}},
        "required": ["url"],
    },
)
def open_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        return "Only http and https links are allowed."
    webbrowser.open(url)
    return f"Opened {url}."
