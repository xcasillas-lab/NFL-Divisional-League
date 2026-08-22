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
TARGET_OWNERS = ["Juan", "Xavier"]

SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
SUMMARY_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary"

CT = ZoneInfo("America/Chicago")
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "DFFL-Live-Scoring-Test/1.0",
    "Accept": "application/json",
})

def normalize_name(name: str) -> str:
    name = unicodedata.normalize("NFKD", name or "")
    name = "".join(ch for ch in name if not unicodedata.combining(ch))
    name = name.lower()
    name = re.sub(r"\b(jr|sr|ii|iii|iv)\.?\b", "", name)
    name = re.sub(r"[^a-z0-9]+", " ", name)
    return " ".join(name.split())

def normalize_team(team: str) -> str:
    team = (team or "").strip().upper()
    aliases = {"WSH": "WAS", "JAX": "JAC"}
    return aliases.get(team, team)

def fetch_json(url, params=None):
    r = SESSION.get(url, params=params, timeout=25)
    r.raise_for_status()
    return r.json()

def to_float(value):
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        m = re.search(r"-?\d+(?:\.\d+)?", str(value))
        return float(m.group(0)) if m else 0.0

def event_teams(event):
    teams = set()
    for comp in event.get("competitions") or []:
        for c in comp.get("competitors") or []:
            abbr = (((c.get("team") or {}).get("abbreviation")) or "")
            if abbr:
                teams.add(normalize_team(abbr))
    return teams

def event_status(event):
    t = ((event.get("status") or {}).get("type")) or {}
    state = str(t.get("state") or "").lower()
    if t.get("completed") or state == "post":
        return "final"
    if state == "in":
        return "live"
    return "pre-game"

def blank_raw():
    return {
        "passingYards": 0.0,
        "passingTouchdowns": 0.0,
        "interceptions": 0.0,
        "rushingYards": 0.0,
        "rushingTouchdowns": 0.0,
        "receptions": 0.0,
        "receivingYards": 0.0,
        "receivingTouchdowns": 0.0,
        "fumblesLost": 0.0,
        "twoPointConversions": 0.0,
    }

def mapped_row(category):
    keys = category.get("keys") or []
    labels = category.get("labels") or []
    names = keys if keys else labels
    return names

def get_mapped_value(mapped, *candidates):
    # Exact match first.
    for candidate in candidates:
        if candidate in mapped:
            return to_float(mapped[candidate])

    # Case-insensitive/fuzzy fallback.
    lowered = {str(k).lower(): v for k, v in mapped.items()}
    for candidate in candidates:
        c = candidate.lower()
        if c in lowered:
            return to_float(lowered[c])
        for k, v in lowered.items():
            if c == k or c in k:
                return to_float(v)

    return 0.0

def player_stats_from_summary(summary):
    """
    Return:
      {(TEAM, normalized player name): raw stat dict}
    """
    out = {}

    for team_block in (summary.get("boxscore") or {}).get("players") or []:
        team = normalize_team((((team_block.get("team") or {}).get("abbreviation")) or ""))

        for category in team_block.get("statistics") or []:
            cat = str(category.get("name") or category.get("displayName") or "").lower()
            field_names = mapped_row(category)

            for row in category.get("athletes") or []:
                athlete = row.get("athlete") or {}
                display_name = athlete.get("displayName") or athlete.get("shortName") or ""
                if not display_name:
                    continue

                key = (team, normalize_name(display_name))
                raw = out.setdefault(key, blank_raw())

                stats = row.get("stats") or []
                mapped = dict(zip(field_names, stats))

                if "pass" in cat:
                    raw["passingYards"] = max(
                        raw["passingYards"],
                        get_mapped_value(mapped, "passingYards", "YDS")
                    )
                    raw["passingTouchdowns"] = max(
                        raw["passingTouchdowns"],
                        get_mapped_value(mapped, "passingTouchdowns", "TD")
                    )
                    raw["interceptions"] = max(
                        raw["interceptions"],
                        get_mapped_value(mapped, "interceptions", "INT")
                    )

                elif "rush" in cat:
                    raw["rushingYards"] = max(
                        raw["rushingYards"],
                        get_mapped_value(mapped, "rushingYards", "YDS")
                    )
                    raw["rushingTouchdowns"] = max(
                        raw["rushingTouchdowns"],
                        get_mapped_value(mapped, "rushingTouchdowns", "TD")
                    )

                elif "receiv" in cat:
                    raw["receptions"] = max(
                        raw["receptions"],
                        get_mapped_value(mapped, "receptions", "REC")
                    )
                    raw["receivingYards"] = max(
                        raw["receivingYards"],
                        get_mapped_value(mapped, "receivingYards", "YDS")
                    )
                    raw["receivingTouchdowns"] = max(
                        raw["receivingTouchdowns"],
                        get_mapped_value(mapped, "receivingTouchdowns", "TD")
                    )

                elif "fumble" in cat:
                    raw["fumblesLost"] = max(
                        raw["fumblesLost"],
                        get_mapped_value(mapped, "fumblesLost", "LOST")
                    )

                # Some ESPN feeds expose two-point conversions in a dedicated category.
                if "two" in cat and "point" in cat:
                    raw["twoPointConversions"] = max(
                        raw["twoPointConversions"],
                        get_mapped_value(mapped, "twoPointConversions", "2PT", "MADE")
                    )

    return out

def dffl_offensive_points(raw):
    # DFFL/Yahoo rules currently being tested:
    # Passing: 1 pt / 25 yds, 4 / pass TD, -1 / INT
    # Rushing: 1 pt / 10 yds, 6 / rush TD
    # Receiving: 0.5 / reception, 1 pt / 10 yds, 6 / rec TD
    # Fumble lost: -2
    # Two-point conversion: +2
    points = 0.0
    points += raw["passingYards"] / 25.0
    points += raw["passingTouchdowns"] * 4.0
    points -= raw["interceptions"] * 1.0

    points += raw["rushingYards"] / 10.0
    points += raw["rushingTouchdowns"] * 6.0

    points += raw["receptions"] * 0.5
    points += raw["receivingYards"] / 10.0
    points += raw["receivingTouchdowns"] * 6.0

    points -= raw["fumblesLost"] * 2.0
    points += raw["twoPointConversions"] * 2.0

    return round(points + 1e-9, 2)

def main():
    print("DFFL two-owner offensive scoring test started")
    print(f"Test date: {TEST_DATE}")
    print(f"Owners: {', '.join(TARGET_OWNERS)}")

    roster_data = json.loads(ROSTER_FILE.read_text(encoding="utf-8"))
    score_data = json.loads(SCORE_FILE.read_text(encoding="utf-8"))

    # Collect only the NFL teams needed for Juan and Xavier's current rosters.
    needed_teams = set()
    for owner in TARGET_OWNERS:
        for p in roster_data["rosters"][owner]["players"]:
            if p.get("position") != "DEF" and p.get("nflTeam"):
                needed_teams.add(normalize_team(p["nflTeam"]))

    print(f"Needed NFL teams: {sorted(needed_teams)}")

    board = fetch_json(SCOREBOARD_URL, {"dates": TEST_DATE, "limit": 100})
    events = board.get("events", [])
    print(f"ESPN events found: {len(events)}")

    # Download each relevant game summary once.
    summaries = []
    relevant_statuses = []

    for event in events:
        teams = event_teams(event)
        if not (teams & needed_teams):
            continue

        event_id = str(event.get("id") or "")
        if not event_id:
            continue

        print(f"Relevant event: {event.get('name')} | id={event_id}")
        summaries.append(fetch_json(SUMMARY_URL, {"event": event_id}))
        relevant_statuses.append(event_status(event))

    # Merge all player stat rows from relevant games.
    all_stats = {}
    for summary in summaries:
        all_stats.update(player_stats_from_summary(summary))

    owner_totals = {}

    for owner in TARGET_OWNERS:
        rows = []
        total = 0.0

        print("")
        print(f"===== {owner.upper()} =====")

        for player in roster_data["rosters"][owner]["players"]:
            position = player.get("position") or ""
            name = player.get("name") or ""
            team = normalize_team(player.get("nflTeam") or "")

            # DEF is intentionally left at zero in Step 2.
            if position == "DEF":
                rows.append({
                    "position": position,
                    "name": name,
                    "nflTeam": team,
                    "points": 0.0,
                    "foundInFeed": False,
                    "note": "DEF scoring will be added in Step 3."
                })
                print(f"{position:4} {name}: 0.00 (DEF deferred to Step 3)")
                continue

            raw = all_stats.get((team, normalize_name(name)), blank_raw())
            found = (team, normalize_name(name)) in all_stats
            points = dffl_offensive_points(raw)

            rows.append({
                "position": position,
                "name": name,
                "nflTeam": team,
                "points": points,
                "foundInFeed": found,
                "raw": raw
            })

            total += points
            print(f"{position:4} {name}: {points:.2f} | found={found}")

        total = round(total, 2)
        owner_totals[owner] = total
        score_data.setdefault("players", {})[owner] = rows
        print(f"{owner} offensive total: {total:.2f}")

    # Update only Matchup 2 (Juan vs Xavier) totals.
    for matchup in score_data.get("matchups", {}).values():
        left = matchup.get("leftOwner")
        right = matchup.get("rightOwner")

        if left in owner_totals:
            matchup["leftTotal"] = owner_totals[left]
        if right in owner_totals:
            matchup["rightTotal"] = owner_totals[right]

    if "live" in relevant_statuses:
        score_data["status"] = "live"
    elif relevant_statuses and all(s == "final" for s in relevant_statuses):
        score_data["status"] = "final"
    else:
        score_data["status"] = "pre-game"

    score_data["lastUpdated"] = datetime.now(CT).isoformat(timespec="seconds")
    score_data["source"] = {
        "primary": "ESPN public NFL JSON",
        "date": TEST_DATE,
        "testStage": "two-owner-offensive-scoring",
        "owners": TARGET_OWNERS,
        "defenseIncluded": False
    }

    SCORE_FILE.write_text(
        json.dumps(score_data, indent=2) + "\n",
        encoding="utf-8"
    )

    print("")
    print("===== MATCHUP TOTALS =====")
    print(f"Juan: {owner_totals.get('Juan', 0):.2f}")
    print(f"Xavier: {owner_totals.get('Xavier', 0):.2f}")
    print(f"Updated: {SCORE_FILE}")
    print("DFFL two-owner offensive scoring test completed successfully")

if __name__ == "__main__":
    main()
