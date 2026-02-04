import os
import shutil
import math
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

# --- IMPORT FORENSIQ MODULES ---
from timeline import build_timeline
from ai.summarizer import generate_summary
from Parser.browser import parse_browser_history
from Parser.log import parse_auth_log
from Parser.files import analyze_file

app = Flask(__name__)

# --- CONFIGURATION ---
UPLOAD_FOLDER = 'Evidence'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- OPTIMIZED SETTINGS (For 4096 Token Context) ---
# We can now process ~30 events per batch (approx 2000-3000 tokens)
# This leaves ~1000 tokens for the AI's response.
BATCH_SIZE = 30
MAX_CHARS_PER_BATCH = 10000 

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def clear_evidence_folder():
    """Wipes the Evidence folder before a new investigation."""
    try:
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"   [System] Failed to delete {file_path}: {e}")
        print("--- SYSTEM: Evidence locker cleared ---")
    except Exception as e:
        print(f"--- SYSTEM WARNING: Could not clear folder: {e} ---")

def process_timeline_in_batches(timeline):
    """
    Splits the timeline into optimal chunks for the Mistral 4K context window.
    """
    total_events = len(timeline)
    # Calculate batches
    num_batches = math.ceil(total_events / BATCH_SIZE)
    
    print(f"--- AI: Splitting {total_events} events into {num_batches} optimized batch(es)... ---")
    
    full_narrative = []
    
    for i in range(num_batches):
        start_idx = i * BATCH_SIZE
        end_idx = start_idx + BATCH_SIZE
        batch_events = timeline[start_idx:end_idx]
        
        # 1. Prepare Text
        batch_text = "\n".join(
            f"[{e['timestamp']}] ({e['source']}) {e['description']}" 
            for e in batch_events
        )
        
        # 2. Safety Check (Just in case massive logs appear)
        if len(batch_text) > MAX_CHARS_PER_BATCH:
            print(f"   [Batch {i+1}] Truncating text from {len(batch_text)} to {MAX_CHARS_PER_BATCH} chars.")
            batch_text = batch_text[:MAX_CHARS_PER_BATCH] + "\n...[TRUNCATED]..."

        print(f"   [Batch {i+1}/{num_batches}] Analyzing events {start_idx} to {end_idx}...")
        
        try:
            # 3. Send to AI
            batch_summary = generate_summary(batch_text)
            
            # 4. Append Result
            full_narrative.append(f"\n\n#### 🔎 Analysis Phase {i+1} (Events {start_idx}-{end_idx})")
            full_narrative.append(batch_summary)
            
        except Exception as e:
            print(f"   [Batch {i+1} Error] {e}")
            full_narrative.append(f"\n[⚠️ Phase {i+1} Skipped: Error generating summary]")

    return "\n".join(full_narrative)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    print("\n=== STARTING INVESTIGATION (HIGH PERFORMANCE MODE) ===")
    
    clear_evidence_folder()
    
    all_events = []
    files_processed_count = 0
    uploaded_files = request.files.getlist('evidence_files')

    if not uploaded_files or uploaded_files[0].filename == '':
        return jsonify({"error": "No evidence files received."}), 400

    print(f"--- SYSTEM: Processing {len(uploaded_files)} artifact(s) ---")

    for file in uploaded_files:
        if file.filename == '': continue
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filepath)
            print(f"-> Saved: {filename}")
        except Exception as e:
            print(f"   [Error] Could not save {filename}: {e}")
            continue

        # --- PARSER ROUTING ---
        current_file_events = []
        try:
            # Browser History
            if filename.lower().endswith('.csv'):
                print(f"   [Parser] Mode: Browser History")
                current_file_events = parse_browser_history(filepath)
                
            # System Logs
            elif filename.lower().endswith(('.log', '.txt')):
                print(f"   [Parser] Mode: System Log")
                current_file_events = parse_auth_log(filepath)
                # Fallback logic
                if not current_file_events and ('.exe' in filename.lower() or '.bin' in filename.lower()):
                    current_file_events = analyze_file(filepath)

            # Binaries
            elif filename.lower().endswith(('.exe', '.bin', '.dll')):
                print(f"   [Parser] Mode: Binary Analysis")
                current_file_events = analyze_file(filepath)

            if current_file_events:
                all_events.extend(current_file_events)
                files_processed_count += 1
            else:
                print(f"   [Warning] {filename} parsed but contained 0 valid events.")

        except Exception as e:
            print(f"   [Error] Parser failure on {filename}: {e}")

    # --- FINAL CHECKS ---
    if files_processed_count == 0:
        return jsonify({"error": "No valid artifacts detected."}), 400

    if not all_events:
        return jsonify({"error": "No forensic events found in files."}), 400

    # --- PROCESSING ---
    try:
        print(f"--- TIMELINE: Correlating {len(all_events)} events ---")
        timeline = build_timeline(all_events)
        
        # Use batch processor
        final_report = process_timeline_in_batches(timeline)
        
        print("=== INVESTIGATION COMPLETE ===\n")
        
        return jsonify({
            "status": "success",
            "timeline": timeline,
            "report": final_report
        })

    except Exception as e:
        print(f"--- FATAL ERROR: {e} ---")
        return jsonify({"error": f"System Failure: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)