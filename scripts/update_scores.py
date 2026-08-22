#!/usr/bin/env python3

import json
import os
import re
import unicodedata
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
ROSTER_FILE = ROOT / "scoring-data" / "week1-rosters-live-test.json"

TEST_DATE = os.environ.get("DFFL_TEST_DATE", "20260822")
TARGET_PLAYER = "Tyler Goodson"
TARGET_TEAM = "ATL"

SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
SUMMARY_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary"

def normalize_name(name: str) -> str:
    name = unicodedata.normalize("NFKD", name or "")
    name = "".join(ch for ch in name if not unicodedata.combining(ch))
    name = name.lower()
    name = re.sub(r"\b(jr|sr|ii|iii|iv)\.?\b", "", name)
    name = re.sub(r"[^a-z0-9]+", " ", name)
    return " ".join(name.split())

def fetch_json(url, params=None):
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def main():
    print("DFFL single-player stat test started")
    print(f"Test date: {TEST_DATE}")
    print(f"Target player: {TARGET_PLAYER} ({TARGET_TEAM})")

    roster_data = json.loads(ROSTER_FILE.read_text(encoding="utf-8"))

    # Confirm Tyler Goodson is actually in the current test roster JSON.
    found_in_roster = False
    for owner, roster in roster_data.get("rosters", {}).items():
        for player in roster.get("players", []):
            if normalize_name(player.get("name", "")) == normalize_name(TARGET_PLAYER):
                print(f"Found in roster: owner={owner}, position={player.get('position')}, team={player.get('nflTeam')}")
                found_in_roster = True
                break
        if found_in_roster:
            break

    if not found_in_roster:
        raise SystemExit(f"{TARGET_PLAYER} was not found in week1-rosters-live-test.json")

    board = fetch_json(
        SCOREBOARD_URL,
        {"dates": TEST_DATE, "limit": 100}
    )

    events = board.get("events", [])
    print(f"ESPN events found: {len(events)}")

    atl_event = None

    for event in events:
        competitions = event.get("competitions") or []
        if not competitions:
            continue

        teams = []
        for comp in competitions:
            for c in comp.get("competitors") or []:
                abbr = (((c.get("team") or {}).get("abbreviation")) or "")
                if abbr:
                    teams.append(abbr.upper())

        if TARGET_TEAM in teams:
            atl_event = event
            print(f"Found ATL event: {event.get('name')} | event id={event.get('id')}")
            break

    if not atl_event:
        raise SystemExit("Could not find Atlanta's game in ESPN scoreboard data.")

    event_id = str(atl_event.get("id"))
    summary = fetch_json(SUMMARY_URL, {"event": event_id})

    boxscore = summary.get("boxscore") or {}
    player_blocks = boxscore.get("players") or []

    matched = False

    for team_block in player_blocks:
        team_abbr = (((team_block.get("team") or {}).get("abbreviation")) or "").upper()

        for category in team_block.get("statistics") or []:
            category_name = category.get("displayName") or category.get("name") or "Unknown Category"
            labels = category.get("labels") or []
            keys = category.get("keys") or []

            for row in category.get("athletes") or []:
                athlete = row.get("athlete") or {}
                athlete_name = athlete.get("displayName") or athlete.get("shortName") or ""

                if normalize_name(athlete_name) == normalize_name(TARGET_PLAYER):
                    matched = True
                    stats = row.get("stats") or []

                    print("")
                    print("===== ESPN PLAYER STAT ROW =====")
                    print(f"Team: {team_abbr}")
                    print(f"Category: {category_name}")
                    print(f"Player: {athlete_name}")
                    print(f"Labels: {labels}")
                    print(f"Keys: {keys}")
                    print(f"Stats: {stats}")

                    # Print label/key-to-value pairs to make the next scoring step easy.
                    field_names = keys if keys else labels
                    if field_names:
                        print("Mapped fields:")
                        for k, v in zip(field_names, stats):
                            print(f"  {k}: {v}")

    if not matched:
        print("")
        print("Tyler Goodson was not found in ESPN's player-stat rows for this event.")
        print("That may mean ESPN has not populated the box score yet, or the player did not record a listed statistic.")
        raise SystemExit(2)

    print("")
    print("DFFL single-player stat test completed successfully")

if __name__ == "__main__":
    main()
