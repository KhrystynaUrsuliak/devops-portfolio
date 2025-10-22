#!/usr/bin/env python3
import argparse
import sys
import time
import json
import csv
from pathlib import Path
import requests

DEFAULT_DISCORD = "https://discord.com/api/webhooks/1430483868653322241/1l3D7Jmzti3wy_v3qLTIH9qNluvaQ8LD1w7rUqSsJ0kOWBmbARDqeWzrSRnrd2-hH07g"

def notify_discord(webhook, title, message):
    if not webhook: return
    try:
        requests.post(webhook, json={"username":"API Monitor",
                                     "embeds":[{"title":title,"description":message}]}, timeout=10)
    except Exception as e:
        print(f"Discord notify failed: {e}", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(description="API availability monitor")
    p.add_argument("urls", nargs="*", help="Endpoints to check")
    p.add_argument("--from-file", help="Text file with one URL per line")
    p.add_argument("--timeout", type=float, default=10)
    p.add_argument("--retries", type=int, default=1)
    p.add_argument("--warn-ms", type=int, default=1500, help="Warn if response time exceeds")
    p.add_argument("--out-json", default="api_results.json")
    p.add_argument("--out-csv", default="api_results.csv")
    p.add_argument("--discord", help="Discord webhook URL")
    p.add_argument("--slack", help="Slack webhook URL")
    args = p.parse_args()
    if not args.discord:
        args.discord = DEFAULT_DISCORD

    urls = list(args.urls)
    if args.from_file:
        urls += [u.strip() for u in Path(args.from_file).read_text().splitlines() if u.strip()]
    if not urls:
        p.error("Provide URLs or --from-file")

    results = []
    session = requests.Session()

    for url in urls:
        status = None
        ok = False
        elapsed_ms = None
        err = ""
        for attempt in range(args.retries + 1):
            t0 = time.perf_counter()
            try:
                r = session.get(url, timeout=args.timeout)
                elapsed_ms = int((time.perf_counter() - t0) * 1000)
                status = r.status_code
                ok = 200 <= r.status_code < 400
                if ok: break
            except Exception as e:
                elapsed_ms = int((time.perf_counter() - t0) * 1000)
                err = str(e)
        results.append({
            "url": url, "status": status, "ok": ok,
            "elapsed_ms": elapsed_ms, "error": err, "timestamp": int(time.time())
        })

        if not ok:
            msg = f"{url} is DOWN (status={status}, err={err}, {elapsed_ms} ms)"
            notify_discord(args.discord, "Endpoint DOWN", msg)
        elif elapsed_ms is not None and elapsed_ms >= args.warn_ms:
            msg = f"{url} is SLOW ({elapsed_ms} ms)"
            notify_discord(args.discord, "Endpoint SLOW", msg)

    Path(args.out_json).write_text(json.dumps(results, indent=2), encoding="utf-8")
    
    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader(); w.writerows(results)

    print(f"Saved: {args.out_json}, {args.out_csv}")

if __name__ == "__main__":
    main()
