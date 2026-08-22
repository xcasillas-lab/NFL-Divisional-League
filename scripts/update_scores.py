#!/usr/bin/env python3

import json
import os
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parents[1]
ROSTER_FILE = ROOT / "scoring-data" / "week1-rosters-live-test.json"
SCORE_FILE = ROOT / "scoring-data" / "week1-scores-live-test.json"

TEST_DATE = os.environ.get("DFFL_TEST_DATE", "20260822")
TARGET_PLAYER = "Tyler Goodson"
TARGET_TEAM = "ATL"
TARGET_OWNER = "Xavier"

SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
SUMMARY_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary"

CT = ZoneInfo("America/Chicago")

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

def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def main():
    print("DFFL Tyler Goodson scoring test started")
    print(f"Test date: {TEST_DATE}")

    roster_data = json.loads(ROSTER_FILE.read_text(encoding="utf-8"))
    score_data = json.loads(SCORE_FILE.read_text(encoding="utf-8"))

    # Verify Tyler is on Xavier's current test roster.
    roster_player = None
    for player in roster_data["rosters"][TARGET_OWNER]["players"]:
        if normalize_name(player.get("name", "")) == normalize_name(TARGET_PLAYER):
            roster_player = player
            break

    if not roster_player:
        raise SystemExit(f"{TARGET_PLAYER} not found on {TARGET_OWNER}'s test roster.")

    print(f"Found roster player: {roster_player}")

    board = fetch_json(SCOREBOARD_URL, {"dates": TEST_DATE, "limit": 100})
    events = board.get("events", [])
    print(f"ESPN events found: {len(events)}")

    atl_event = None
    for event in events:
        competitions = event.get("competitions") or []
        teams = []
        for comp in competitions:
            for c in comp.get("competitors") or []:
                abbr = (((c.get("team") or {}).get("abbreviation")) or "").upper()
                if abbr:
                    teams.append(abbr)
        if TARGET_TEAM in teams:
            atl_event = event
            print(f"Found ATL event: {event.get('name')} | event id={event.get('id')}")
            break

    if not atl_event:
        raise SystemExit("Could not find Atlanta's game.")

    summary = fetch_json(SUMMARY_URL, {"event": str(atl_event.get("id"))})

    rushing_yards = 0.0
    rushing_td = 0.0
    receptions = 0.0
    receiving_yards = 0.0
    receiving_td = 0.0

    matched_any = False

    for team_block in (summary.get("boxscore") or {}).get("players") or []:
        team_abbr = (((team_block.get("team") or {}).get("abbreviation")) or "").upper()

        for category in team_block.get("statistics") or []:
            category_name = (category.get("name") or category.get("displayName") or "").lower()
            keys = category.get("keys") or []
            labels = category.get("labels") or []

            for row in category.get("athletes") or []:
                athlete = row.get("athlete") or {}
                athlete_name = athlete.get("displayName") or athlete.get("shortName") or ""

                if normalize_name(athlete_name) != normalize_name(TARGET_PLAYER):
                    continue

                matched_any = True
                stats = row.get("stats") or []
                field_names = keys if keys else labels
                mapped = dict(zip(field_names, stats))

                if "rushing" in category_name:
                    rushing_yards = to_float(mapped.get("rushingYards", mapped.get("YDS", 0)))
                    rushing_td = to_float(mapped.get("rushingTouchdowns", mapped.get("TD", 0)))

                elif "receiving" in category_name:
                    receptions = to_float(mapped.get("receptions", mapped.get("REC", 0)))
                    receiving_yards = to_float(mapped.get("receivingYards", mapped.get("YDS", 0)))
                    receiving_td = to_float(mapped.get("receivingTouchdowns", mapped.get("TD", 0)))

    if not matched_any:
        raise SystemExit("Tyler Goodson was not found in ESPN player stat rows.")

    # DFFL scoring for this test:
    # 1 point / 10 rushing yards
    # 6 points / rushing TD
    # 0.5 points / reception
    # 1 point / 10 receiving yards
    # 6 points / receiving TD
    fantasy_points = (
        rushing_yards / 10.0
        + rushing_td * 6.0
        + receptions * 0.5
        + receiving_yards / 10.0
        + receiving_td * 6.0
    )
    fantasy_points = round(fantasy_points, 2)

    print("")
    print("===== DFFL TYLER GOODSON SCORE =====")
    print(f"Rushing yards: {rushing_yards}")
    print(f"Rushing TD: {rushing_td}")
    print(f"Receptions: {receptions}")
    print(f"Receiving yards: {receiving_yards}")
    print(f"Receiving TD: {receiving_td}")
    print(f"DFFL fantasy points: {fantasy_points}")

    # Preserve all owners. Replace only Tyler's current score row for Xavier.
    existing = score_data.get("players", {}).get(TARGET_OWNER, [])
    new_owner_rows = []
    replaced = False

    for row in existing:
        if normalize_name(row.get("name", "")) == normalize_name(TARGET_PLAYER):
            new_owner_rows.append({
                "position": roster_player.get("position"),
                "name": TARGET_PLAYER,
                "nflTeam": TARGET_TEAM,
                "points": fantasy_points
            })
            replaced = True
        else:
            new_owner_rows.append(row)

    if not replaced:
        new_owner_rows.append({
            "position": roster_player.get("position"),
            "name": TARGET_PLAYER,
            "nflTeam": TARGET_TEAM,
            "points": fantasy_points
        })

    score_data.setdefault("players", {})[TARGET_OWNER] = new_owner_rows

    # For this one-player test, Xavier's team total is just Tyler's points.
    # We will replace this with a sum of all 8 roster players in the full version.
    for matchup in score_data.get("matchups", {}).values():
        if matchup.get("leftOwner") == TARGET_OWNER:
            matchup["leftTotal"] = fantasy_points
        if matchup.get("rightOwner") == TARGET_OWNER:
            matchup["rightTotal"] = fantasy_points

    score_data["lastUpdated"] = datetime.now(CT).isoformat(timespec="seconds")
    score_data["status"] = "live"
    score_data["source"] = {
        "primary": "ESPN public NFL JSON",
        "date": TEST_DATE,
        "testStage": "single-player-scoring",
        "targetPlayer": TARGET_PLAYER
    }

    SCORE_FILE.write_text(
        json.dumps(score_data, indent=2) + "\n",
        encoding="utf-8"
    )

    print("")
    print(f"Updated {SCORE_FILE}")
    print("DFFL Tyler Goodson scoring test completed successfully")

if __name__ == "__main__":
    main()
