import re
from datetime import datetime
from typing import List, Dict, Optional

def parse_auth_log(filepath: str) -> List[Dict[str, str]]:
    events = []
    
    # Regex for standard log timestamps (Syslog or ISO)
    # Group 1 captures the Timestamp, Group 2 captures the rest
    log_pattern = re.compile(r'^([A-Z][a-z]{2}\s+\d+\s\d{2}:\d{2}:\d{2}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s+(.*)', re.IGNORECASE)

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as logfile:
            for line in logfile:
                line = line.strip()
                if not line: continue
                
                match = log_pattern.search(line)
                if match:
                    timestamp_str = match.group(1)
                    message = match.group(2)
                    
                    # Keywords to identify "Suspicious" vs "General" info
                    # You can add more keywords here to filter noise
                    description = message
                    
                    events.append({
                        "timestamp": timestamp_str, # You can normalize this if needed
                        "description": description[:200], # Truncate long logs
                        "source": "auth_log"
                    })
                else:
                    # FALLBACK: If line has no timestamp at start, check if it looks important
                    if "error" in line.lower() or "fail" in line.lower():
                         events.append({
                            "timestamp": "UNKNOWN",
                            "description": line[:200],
                            "source": "auth_log_raw"
                        })

    except Exception as e:
        print(f"   [Error] Log Parse Error: {e}")
    
    return events