#!/usr/bin/env python3
import re, argparse, collections, html, json
from datetime import datetime
from pathlib import Path

LOG_RE = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<req>[^"]*)" '
    r'(?P<status>\d{3}) (?P<size>\S+)(?: "(?P<ref>[^"]*)" "(?P<ua>[^"]*)")?'
)

def parse_line(line):
    m = LOG_RE.match(line)
    if not m: return None
    d = m.groupdict()
    d["method"], d["path"], d["proto"] = ("", "", "")
    if d["req"]:
        parts = d["req"].split()
        if len(parts) >= 1: d["method"] = parts[0]
        if len(parts) >= 2: d["path"] = parts[1]
        if len(parts) >= 3: d["proto"] = parts[2]
    return d

def main():
    p = argparse.ArgumentParser(description="Parse web logs and build HTML report")
    p.add_argument("logfile", help="Path to access.log")
    p.add_argument("--out", default="report.html", help="Output HTML file")
    p.add_argument("--top", type=int, default=10, help="Top N IP/UA")
    args = p.parse_args()

    ips = collections.Counter()
    uas = collections.Counter()
    statuses = collections.Counter()
    methods = collections.Counter()
    total = 0

    with open(args.logfile, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            d = parse_line(line)
            if not d: continue
            total += 1
            ips[d["ip"]] += 1
            uas[d.get("ua","-") or "-"] += 1
            statuses[d["status"]] += 1
            methods[d["method"]] += 1

    def table(title, counter):
        rows = "\n".join(
            f"<tr><td>{html.escape(k)}</td><td>{v}</td></tr>"
            for k, v in counter.most_common(args.top)
        )
        return f"<h3>{title}</h3><table border='1' cellpadding='6'><tr><th>Value</th><th>Count</th></tr>{rows}</table>"

    html_doc = f"""<!doctype html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>Log Report</title>
    <style>
    body{{font-family:system-ui,Arial;margin:20px}} table{{border-collapse:collapse}} th{{text-align:left}}</style>
    </head>
    <body>
    <h1>Web Log Report</h1>
    <p>Generated: {datetime.now().isoformat(timespec='seconds')}</p>
    <p>Total lines parsed: {total}</p>
    {table("Top IPs", ips)}
    {table("Top User-Agents", uas)}
    {table("HTTP Status Codes", statuses)}
    {table("HTTP Methods", methods)}
    </body>
    </html>"""

    Path(args.out).write_text(html_doc, encoding="utf-8")
    print(f"Report saved to {args.out}")

if __name__ == "__main__":
    main()
