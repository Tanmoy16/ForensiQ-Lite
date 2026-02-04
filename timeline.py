# timeline.py
"""
ForensiQ-Lite Timeline Engine

Purpose:
- Normalize timestamps from multiple forensic artifacts
- Correlate events across sources
- Produce a unified chronological timeline

This module performs deterministic analysis only.
"""

from datetime import datetime
from typing import List, Dict

SUPPORTED_TIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%b %d %H:%M:%S", 
    "%a %b %d %H:%M:%S %Y",# auth.log style (Feb 03 10:44:12)
]


def _parse_timestamp(timestamp: str) -> datetime:
    """
    Attempt to parse a timestamp string using known formats.
    Returns datetime.min if parsing fails.
    """
    for fmt in SUPPORTED_TIME_FORMATS:
        try:
            return datetime.strptime(timestamp, fmt)
        except ValueError:
            continue

    # Fallback for unparsable timestamps
    return datetime.min


def build_timeline(events: List[Dict]) -> List[Dict]:
    """
    Build a unified forensic timeline from parsed events.

    Each event must contain:
    - timestamp (str)
    - description (str)
    - source (str)

    Returns:
    - Sorted list of events with normalized datetime objects
    """

    timeline = []

    for event in events:
        parsed_time = _parse_timestamp(event.get("timestamp", ""))

        timeline.append({
            "timestamp": event.get("timestamp", "UNKNOWN"),
            "parsed_time": parsed_time,
            "description": event.get("description", ""),
            "source": event.get("source", "unknown")
        })

    # Sort events chronologically
    timeline.sort(key=lambda x: x["parsed_time"])

    return timeline


def format_timeline(timeline: List[Dict]) -> str:
    """
    Convert timeline events into a human-readable string.
    Useful for CLI output and reports.
    """
    lines = []

    for event in timeline:
        time_str = (
            event["parsed_time"].strftime("%Y-%m-%d %H:%M:%S")
            if event["parsed_time"] != datetime.min
            else "UNKNOWN_TIME"
        )

        lines.append(
            f"[{time_str}] ({event['source']}) {event['description']}"
        )

    return "\n".join(lines)