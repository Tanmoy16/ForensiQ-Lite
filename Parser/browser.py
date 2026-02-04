import csv
from datetime import datetime
from typing import List, Dict

def normalize_timestamp(timestamp_str: str) -> str:
    # (Keep your existing timestamp logic or use this simplified one)
    formats = [
        "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f",
        "%m/%d/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%Y%m%d%H%M%S"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str.strip(), fmt).isoformat()
        except ValueError:
            continue
    return timestamp_str.strip()

def parse_browser_history(filepath: str) -> List[Dict[str, str]]:
    events = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as csvfile:
            # Read first few bytes to sniff delimiter (comma vs semicolon)
            sample = csvfile.read(1024)
            csvfile.seek(0)
            dialect = csv.Sniffer().sniff(sample) if sample else 'excel'
            
            reader = csv.DictReader(csvfile, dialect=dialect)
            
            # AUTO-DETECT HEADERS
            # We look for the best matching column name for "timestamp" and "url"
            headers = reader.fieldnames or []
            time_col = next((h for h in headers if 'time' in h.lower() or 'date' in h.lower()), 'timestamp')
            url_col = next((h for h in headers if 'url' in h.lower() or 'link' in h.lower()), 'url')

            print(f"   [Debug] Using CSV Headers -> Time: '{time_col}', URL: '{url_col}'")

            for row in reader:
                if not row: continue
                
                # Flexible extraction
                timestamp = row.get(time_col, '').strip()
                url = row.get(url_col, '').strip()
                
                if not timestamp or not url:
                    continue

                events.append({
                    "timestamp": normalize_timestamp(timestamp),
                    "description": f"Visited URL: {url}",
                    "source": "browser"
                })
                
    except Exception as e:
        print(f"   [Error] CSV Parse Error: {e}")
    
    return events