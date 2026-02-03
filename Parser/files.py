# parser/files.py

import hashlib
import os
import time

def analyze_file(file_path):
    events = []

    # Compute SHA256 hash
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)

    file_hash = sha256.hexdigest()

    created_time = time.ctime(os.path.getctime(file_path))

    events.append({
        "timestamp": created_time,
        "description": f"Suspicious file created (SHA256: {file_hash[:10]}...)",
        "source": "file_system"
    })

    return events