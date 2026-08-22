#!/usr/bin/env python3

import os
import requests

TEST_DATE = "20260820"  # Fixed diagnostic date: Raiders at Texans
TARGET_TEAM = "LV"
SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
SUMMARY_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary"

def fetch_json(url, params=None):
    r = requests.get(url, params=params, timeout=25)
    r.raise_for_status()
    return r.json()

def main():
    print("DFFL Raiders raw ESPN player diagnostic started")
    print(f"Test date: {TEST_DATE}")

    board = fetch_json(SCOREBOARD_URL, {"dates": TEST_DATE, "limit": 100})
    events = board.get("events", [])

    raiders_event = None
    for event in events:
        teams = []
        for comp in event.get("competitions") or []:
            for c in comp.get("competitors") or []:
                abbr = (((c.get("team") or {}).get("abbreviation")) or "").upper()
                if abbr:
                    teams.append(abbr)

        if TARGET_TEAM in teams:
            raiders_event = event
            print(f"Found Raiders event: {event.get('name')} | id={event.get('id')}")
            break

    if not raiders_event:
        raise SystemExit("Could not find the Raiders game for this date.")

    summary = fetch_json(SUMMARY_URL, {"event": str(raiders_event.get("id"))})

    found_any = False

    for team_block in (summary.get("boxscore") or {}).get("players") or []:
        team_abbr = (((team_block.get("team") or {}).get("abbreviation")) or "").upper()
        if team_abbr != TARGET_TEAM:
            continue

        for category in team_block.get("statistics") or []:
            category_name = category.get("displayName") or category.get("name") or "Unknown"
            if category_name.lower() not in {"rushing", "receiving"}:
                continue

            print("")
            print(f"===== {category_name.upper()} =====")
            print(f"Labels: {category.get('labels')}")
            print(f"Keys: {category.get('keys')}")

            for row in category.get("athletes") or []:
                athlete = row.get("athlete") or {}
                display_name = athlete.get("displayName")
                short_name = athlete.get("shortName")
                athlete_id = athlete.get("id")
                jersey = athlete.get("jersey")
                stats = row.get("stats") or []

                print("")
                print("PLAYER RAW:")
                print(f"  id: {athlete_id}")
                print(f"  displayName: {display_name}")
                print(f"  shortName: {short_name}")
                print(f"  jersey: {jersey}")
                print(f"  stats: {stats}")

                if display_name and "Washington" in display_name:
                    found_any = True
                    print("  >>> TARGET MATCH: WASHINGTON <<<")

    if not found_any:
        print("")
        print("No Raiders player with 'Washington' in displayName was found.")
        raise SystemExit(2)

    print("")
    print("DFFL Raiders raw ESPN player diagnostic completed successfully")

if __name__ == "__main__":
    main()
