"""
Authentication Log Parser for Digital Forensics
Parses Linux-style authentication logs (auth.log) for forensic timeline analysis
"""

import re
from datetime import datetime
from typing import List, Dict, Optional


def parse_syslog_timestamp(timestamp_str: str, year: Optional[int] = None) -> str:
    """
    Parse syslog-style timestamp and convert to ISO-8601
    
    Syslog format: "Jan 15 14:30:45" or "2024-01-15T14:30:45"
    
    Args:
        timestamp_str: Raw timestamp from log line
        year: Optional year to use (syslog doesn't include year)
        
    Returns:
        ISO-8601 formatted timestamp
    """
    timestamp_str = timestamp_str.strip()
    
    # Try ISO-8601 format first
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.isoformat()
    except ValueError:
        pass
    
    # Try standard syslog format: "Jan 15 14:30:45"
    try:
        # Use current year if not provided
        if year is None:
            year = datetime.now().year
        
        # Parse without year
        dt = datetime.strptime(timestamp_str, "%b %d %H:%M:%S")
        # Add year
        dt = dt.replace(year=year)
        return dt.isoformat()
    except ValueError:
        pass
    
    # Try syslog with milliseconds: "Jan 15 14:30:45.123"
    try:
        if year is None:
            year = datetime.now().year
        dt = datetime.strptime(timestamp_str, "%b %d %H:%M:%S.%f")
        dt = dt.replace(year=year)
        return dt.isoformat()
    except ValueError:
        pass
    
    # Return as-is if unable to parse
    return timestamp_str


def extract_authentication_event(line: str) -> Optional[Dict[str, str]]:
    """
    Extract authentication event from a single log line
    
    Args:
        line: Single line from auth.log
        
    Returns:
        Dictionary with event details or None if not auth-related
    """
    line = line.strip()
    if not line:
        return None
    
    # Extract timestamp (first 15 characters typically)
    # Syslog format: "Jan 15 14:30:45" or similar
    timestamp_match = re.match(r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', line)
    if not timestamp_match:
        # Try ISO format
        timestamp_match = re.match(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
    
    if not timestamp_match:
        return None
    
    timestamp_str = timestamp_match.group(1)
    iso_timestamp = parse_syslog_timestamp(timestamp_str)
    
    # Authentication event patterns
    patterns = [
        # Failed password attempts
        (r'Failed password for (?:invalid user )?(\S+)', 'Failed login attempt for user: {}'),
        (r'authentication failure.*user=(\S+)', 'Authentication failure for user: {}'),
        (r'FAILED LOGIN.*user=(\S+)', 'Failed login for user: {}'),
        
        # Successful logins
        (r'Accepted password for (\S+)', 'Successful login for user: {}'),
        (r'Accepted publickey for (\S+)', 'Successful SSH key authentication for user: {}'),
        (r'session opened for user (\S+)', 'Session opened for user: {}'),
        
        # Session events
        (r'session closed for user (\S+)', 'Session closed for user: {}'),
        (r'pam_unix\(.*:session\): session opened for user (\S+)', 'Session started for user: {}'),
        (r'pam_unix\(.*:session\): session closed for user (\S+)', 'Session ended for user: {}'),
        
        # Account lockout
        (r'Account locked.*user (\S+)', 'Account locked: {}'),
        (r'account (\S+) locked', 'Account locked: {}'),
        
        # Invalid/unknown users
        (r'Invalid user (\S+)', 'Invalid user login attempt: {}'),
        (r'User (\S+) from .* not allowed', 'Unauthorized login attempt by user: {}'),
        
        # Root access
        (r'root.*authentication failure', 'Failed root authentication attempt'),
        (r'ROOT LOGIN.*refused', 'Root login refused'),
        
        # Sudo events
        (r'sudo:.*user (\S+).*COMMAND=', 'Sudo command executed by user: {}'),
        (r'(\S+) : TTY=.*COMMAND=', 'Privileged command by user: {}'),
        
        # Password changes
        (r'password changed for (\S+)', 'Password changed for user: {}'),
        (r'New password for user (\S+)', 'Password reset for user: {}'),
    ]
    
    # Check each pattern
    for pattern, description_template in patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            # Extract username if captured
            if '{}' in description_template:
                username = match.group(1)
                description = description_template.format(username)
            else:
                description = description_template
            
            return {
                "timestamp": iso_timestamp,
                "description": description,
                "source": "auth_log"
            }
    
    return None


def parse_auth_log(filepath: str) -> List[Dict[str, str]]:
    """
    Parse authentication log file and extract forensic events
    
    Args:
        filepath: Path to auth.log file (read-only)
        
    Returns:
        List of forensic event dictionaries
    """
    events = []
    
    try:
        # Open file in read-only mode
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as logfile:
            for line in logfile:
                event = extract_authentication_event(line)
                if event:
                    events.append(event)
    
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
    except PermissionError:
        print(f"Error: Permission denied: {filepath}")
    except Exception as e:
        print(f"Error parsing log file: {e}")
    
    return events


def main():
    """
    Example usage of the authentication log parser
    """
    # Example: Parse an auth.log file
    filepath = "auth.log"
    events = parse_auth_log(filepath)
    
    # Display results
    print(f"Extracted {len(events)} authentication events")
    for event in events:
        print(f"[{event['timestamp']}] {event['description']}")


if __name__ == "__main__":
    main()