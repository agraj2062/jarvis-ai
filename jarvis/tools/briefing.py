from . import tool
from .github_tools import list_notifications
from .system_tools import current_time, system_status


@tool(
    "Give a full status briefing: time, machine health and GitHub notifications. "
    "Use for 'good morning', 'status report' or 'brief me'."
)
def briefing() -> str:
    parts = [current_time(), system_status()]
    try:
        parts.append("GitHub: " + list_notifications())
    except Exception as e:  # token missing, offline, etc.
        parts.append(f"GitHub unavailable: {e}")
    return "\n".join(parts)
