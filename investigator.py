from timeline import build_timeline
from ai.summarizer import generate_summary
from Parser.browser import parse_browser_history

# Parse available evidence (browser history) and build timeline
events_parsed = parse_browser_history("Evidence/browser.csv")
events = build_timeline(events_parsed)

timeline_text = "\n".join(
    f"{e['timestamp']} - {e['description']} ({e['source']})"
    for e in events
)

summary = generate_summary(timeline_text)

with open("report.md", "w") as f:
    f.write(summary)

print("✔ Investigation report generated")
