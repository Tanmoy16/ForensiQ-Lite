# 🕵️‍♂️ ForensiQ-Lite

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey.svg)
![AI](https://img.shields.io/badge/AI-Mistral%207B-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**ForensiQ-Lite** is an automated, AI-powered Digital Forensics and Incident Response (DFIR) triage tool. It ingests mixed forensic artifacts (logs, browser histories, binaries), correlates them into a unified chronological timeline, and leverages a local Large Language Model (LLM) to generate comprehensive incident summaries.

Built with a focus on data privacy, all AI processing is done **locally** on your hardware, ensuring sensitive log data never leaves your environment.

---

## ✨ Features

* **Multi-Artifact Parsing:** Intelligently extracts structured data from `.csv` (Browser History), `.log/.txt` (System/Auth logs), and `.exe/.dll/.bin` (Executables).
* **Smart Fallback Routing:** Automatically attempts binary analysis if standard text/log extraction fails on ambiguous files.
* **Unified Timeline Generation:** Aggregates disparate data points from multiple sources into a single, chronologically sorted feed to easily track lateral movement.
* **Local AI Analysis:** Utilizes the Mistral-7b LLM via `ctransformers` to analyze the timeline and generate executive summaries, attack chain reconstructions, and IOC (Indicator of Compromise) reports.
* **Context-Window Safety:** Implements smart text truncation and strict token-limit safety nets to prevent model crashes when analyzing massive log files.
* **Cross-Platform Optimized:** Includes customized processing pipelines for standard Windows CPUs and high-performance Apple Silicon (M1/M2/M3) environments.
* **Cyber-Themed Web Dashboard:** A sleek, dark-mode web interface featuring drag-and-drop evidence uploading and split-pane report viewing.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask, Werkzeug
* **AI Engine:** `ctransformers`, Local GGUF Models (Mistral)
* **Frontend:** HTML5, CSS3 (Custom Dark/Neon UI), Vanilla JavaScript
* **Forensic Parsers:** Custom Regex engines, CSV Dialect Sniffers, Binary Analysis modules

---

## 🚀 Getting Started

### Prerequisites

1.  **Python 3.8+** installed on your system.
2.  **C++ Build Tools** (Required for compiling certain Python dependencies).
3.  **Local LLM Model:** You must download the Mistral-7B GGUF model.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/ForensiQ-Lite.git](https://github.com/yourusername/ForensiQ-Lite.git)
    cd ForensiQ-Lite
    ```

2.  **Create and activate a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install Flask ctransformers werkzeug
    ```
    *(Note: Ensure any dependencies required by your custom `Parser` or `timeline` modules are also installed).*

4.  **Download the AI Model:**
    * Download `mistral-7b-instruct-v0.2.Q4_K_M.gguf` from HuggingFace (TheBloke's repository is recommended).
    * Create a `models` directory in the root of the project.
    * Place the downloaded `.gguf` file inside the `models` folder.

---

## 💻 Usage

### Option 1: Web Interface (Flask Dashboard)
Provides a rich graphical interface for dragging and dropping evidence files.

1.  Run the Flask application:
    ```bash
    python app.py
    ```
2.  Open your web browser and navigate to: `http://127.0.0.1:5000`
3.  Upload your `.csv`, `.log`, or `.exe` files using the interface and click **Initialize Analysis**.

### Option 2: Command Line Interface (CLI)
For quick, terminal-based triage.

1.  Place your evidence files into the `Evidence/` directory.
2.  Run the investigator script:
    ```bash
    python investigator.py
    ```
    *(Alternatively, pass specific files directly via arguments: `python investigator.py --csv path/to/history.csv --log path/to/auth.log`)*
3.  The tool will output the analysis to the terminal and save a detailed `report.md` in the root directory.

---

## 📂 Project Structure

```text
ForensiQ-Lite/
├── app.py                  # Flask Web Server & API Routing
├── investigator.py         # CLI Entry Point
├── timeline.py             # Event correlation engine
├── ai/
│   └── summarizer.py       # LLM Integration & Prompt Engineering
├── Parser/
│   ├── browser.py          # CSV/Browser History extraction
│   ├── log.py              # Syslog/Auth log regex engine
│   └── files.py            # Binary metadata analysis
├── models/
│   └── mistral-7b-instruct-v0.2.Q4_K_M.gguf  # Place LLM here
├── static/                 # Web assets (CSS, JS)
├── templates/              # HTML views (index.html)
└── Evidence/               # Temporary storage for active cases
