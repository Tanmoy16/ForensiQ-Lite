from timeline import build_timeline
from ai.llm_client import generate_report
from ai.prompts import REPORT_PROMPT
import json

def main():
    timeline = build_timeline(...)

    findings = {
        "timeline": timeline
    }

    with open("report/findings.json", "w") as f:
        json.dump(findings, f, indent=2)

    findings_text = REPORT_PROMPT + "\n" + json.dumps(findings, indent=2)

    report = generate_report(findings_text)

    with open("report/report.md", "w") as f:
        f.write(report)
