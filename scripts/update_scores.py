#!/usr/bin/env python3

import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parents[1]
SCORE_FILE = ROOT / "scoring-data" / "week1-scores-live-test.json"

TEST_DATE = os.environ.get("DFFL_TEST_DATE", "20260822")
CT = ZoneInfo("America/Chicago")

def main():
    print("DFFL scoring test started")
    print(f"Test date: {TEST_DATE}")
    print(f"Score file: {SCORE_FILE}")

    url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
    response = requests.get(
        url,
        params={"dates": TEST_DATE, "limit": 100},
        timeout=20
    )
    response.raise_for_status()

    data = response.json()
    events = data.get("events", [])
    print(f"ESPN events found: {len(events)}")

    score_data = json.loads(SCORE_FILE.read_text(encoding="utf-8"))

    now_ct = datetime.now(CT).isoformat(timespec="seconds")

    score_data["lastUpdated"] = now_ct
    score_data["source"] = {
        "primary": "ESPN public NFL JSON",
        "date": TEST_DATE,
        "eventCount": len(events),
        "testStage": "connection-check"
    }

    SCORE_FILE.write_text(
        json.dumps(score_data, indent=2) + "\n",
        encoding="utf-8"
    )

    print(f"Updated JSON at: {now_ct}")
    print("DFFL scoring test completed successfully")

if __name__ == "__main__":
    main()
