import csv
from datetime import datetime
from typing import List, Dict


def normalize_timestamp(timestamp_str: str) -> str:
    """
    Convert various timestamp formats to ISO-8601
    
    Args:
        timestamp_str: Raw timestamp string from CSV
        
    Returns:
        ISO-8601 formatted timestamp string
    """
    # Common timestamp formats found in browser histories
    formats = [
        "%Y-%m-%d %H:%M:%S",           # 2024-01-15 14:30:45
        "%Y-%m-%dT%H:%M:%S",           # 2024-01-15T14:30:45
        "%Y-%m-%d %H:%M:%S.%f",        # 2024-01-15 14:30:45.123456
        "%m/%d/%Y %H:%M:%S",           # 01/15/2024 14:30:45
        "%m/%d/%Y %I:%M:%S %p",        # 01/15/2024 02:30:45 PM
        "%d/%m/%Y %H:%M:%S",           # 15/01/2024 14:30:45
        "%Y%m%d%H%M%S",                # 20240115143045
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp_str.strip(), fmt)
            return dt.isoformat()
        except ValueError:
            continue
    
    # If already ISO-8601 or unrecognized, return as-is
    return timestamp_str.strip()


def parse_browser_history(filepath: str) -> List[Dict[str, str]]:
    """
    Parse browser history CSV file and extract forensic events
    
    Args:
        filepath: Path to browser history CSV file (read-only)
        
    Returns:
        List of forensic event dictionaries
    """
    events = []
    
    try:
        # Open file in read-only mode
        with open(filepath, 'r', encoding='utf-8', newline='') as csvfile:
            # Auto-detect CSV dialect
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Skip empty rows
                if not row:
                    continue
                
                # Extract timestamp (required field)
                timestamp = row.get('timestamp', '').strip()
                if not timestamp:
                    continue
                
                # Normalize timestamp to ISO-8601
                iso_timestamp = normalize_timestamp(timestamp)
                
                # Extract URL (required field)
                url = row.get('url', '').strip()
                if not url:
                    continue
                
                # Check if this was a download event
                downloaded_file = row.get('downloaded_file', '').strip()
                
                if downloaded_file:
                    # Download event
                    description = f"Downloaded file: {downloaded_file}"
                else:
                    # Regular URL visit
                    description = f"Visited URL: {url}"
                
                # Create forensic event
                event = {
                    "timestamp": iso_timestamp,
                    "description": description,
                    "source": "browser"
                }
                
                events.append(event)
    
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
    except PermissionError:
        print(f"Error: Permission denied: {filepath}")
    except Exception as e:
        print(f"Error parsing file: {e}")
    
    return events


def main():
    """
    Example usage of the browser history parser
    """
    # Example: Parse a browser history file
    filepath = "browser_history.csv"
    events = parse_browser_history(filepath)
    
    # Display results
    print(f"Extracted {len(events)} forensic events")
    for event in events:
        print(f"[{event['timestamp']}] {event['description']}")


if __name__ == "__main__":
    main()