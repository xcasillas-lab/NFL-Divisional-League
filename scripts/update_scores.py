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

TEAM_ALIASES = {
    "WSH": "WAS",
    "JAX": "JAC"
}

def normalize_name(name: str) -> str:
    name = unicodedata.normalize("NFKD", name or "")
    name = "".join(ch for ch in name if not unicodedata.combining(ch))
    name = name.lower()
    name = re.sub(r"\b(jr|sr|ii|iii|iv)\.?\b", "", name)
    name = re.sub(r"[^a-z0-9]+", " ", name)
    return " ".join(name.split())

def normalize_team(team: str) -> str:
    team = (team or "").strip().upper()
    return TEAM_ALIASES.get(team, team)

def fetch_json(url, params=None):
    r = requests.get(url, params=params, timeout=25)
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

def get_mapped_value(mapped, *candidates):
    for candidate in candidates:
        if candidate in mapped:
            return to_float(mapped[candidate])

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
    out = {}

    for team_block in (summary.get("boxscore") or {}).get("players") or []:
        team = normalize_team((((team_block.get("team") or {}).get("abbreviation")) or ""))

        for category in team_block.get("statistics") or []:
            cat = str(category.get("name") or category.get("displayName") or "").lower()
            keys = category.get("keys") or []
            labels = category.get("labels") or []
            field_names = keys if keys else labels

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
                    raw["passingYards"] = max(raw["passingYards"], get_mapped_value(mapped, "passingYards", "YDS"))
                    raw["passingTouchdowns"] = max(raw["passingTouchdowns"], get_mapped_value(mapped, "passingTouchdowns", "TD"))
                    raw["interceptions"] = max(raw["interceptions"], get_mapped_value(mapped, "interceptions", "INT"))

                elif "rush" in cat:
                    raw["rushingYards"] = max(raw["rushingYards"], get_mapped_value(mapped, "rushingYards", "YDS"))
                    raw["rushingTouchdowns"] = max(raw["rushingTouchdowns"], get_mapped_value(mapped, "rushingTouchdowns", "TD"))

                elif "receiv" in cat:
                    raw["receptions"] = max(raw["receptions"], get_mapped_value(mapped, "receptions", "REC"))
                    raw["receivingYards"] = max(raw["receivingYards"], get_mapped_value(mapped, "receivingYards", "YDS"))
                    raw["receivingTouchdowns"] = max(raw["receivingTouchdowns"], get_mapped_value(mapped, "receivingTouchdowns", "TD"))

                elif "fumble" in cat:
                    raw["fumblesLost"] = max(raw["fumblesLost"], get_mapped_value(mapped, "fumblesLost", "LOST"))

                if "two" in cat and "point" in cat:
                    raw["twoPointConversions"] = max(
                        raw["twoPointConversions"],
                        get_mapped_value(mapped, "twoPointConversions", "2PT", "MADE")
                    )

    return out

def dffl_offensive_points(raw):
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

def game_scores(summary):
    scores = {}
    competitions = (summary.get("header") or {}).get("competitions") or []

    if competitions:
        for competitor in competitions[0].get("competitors") or []:
            abbr = normalize_team((((competitor.get("team") or {}).get("abbreviation")) or ""))
            if abbr:
                scores[abbr] = int(to_float(competitor.get("score")))

    return scores

def points_allowed_score(points_allowed):
    if points_allowed == 0:
        return 10.0
    if 1 <= points_allowed <= 6:
        return 7.0
    if 7 <= points_allowed <= 13:
        return 4.0
    if 14 <= points_allowed <= 20:
        return 1.0
    if 21 <= points_allowed <= 27:
        return 0.0
    if 28 <= points_allowed <= 34:
        return -1.0
    return -4.0

def find_team_stat(stats, *candidates):
    for stat in stats:
        names = [
            stat.get("name"),
            stat.get("label"),
            stat.get("displayName")
        ]
        flat = " ".join(str(x or "") for x in names).lower().replace(" ", "")

        for candidate in candidates:
            c = candidate.lower().replace(" ", "")
            if c and c in flat:
                return to_float(stat.get("value", stat.get("displayValue")))

    return 0.0

def player_return_and_defense_tds(summary, target_team):
    """
    Sum D/ST touchdown categories from ESPN player box-score rows:
      - interception return TD
      - fumble return TD
      - kick return TD
      - punt return TD

    Returns:
      defensive_td_count, return_td_count
    """
    target_team = normalize_team(target_team)
    defensive_tds = 0.0
    return_tds = 0.0

    for team_block in (summary.get("boxscore") or {}).get("players") or []:
        team = normalize_team((((team_block.get("team") or {}).get("abbreviation")) or ""))
        if team != target_team:
            continue

        for category in team_block.get("statistics") or []:
            cat = str(category.get("name") or category.get("displayName") or "").lower()
            keys = category.get("keys") or []
            labels = category.get("labels") or []
            field_names = keys if keys else labels

            for row in category.get("athletes") or []:
                stats = row.get("stats") or []
                mapped = dict(zip(field_names, stats))

                # Defensive TDs.
                if "interception" in cat:
                    defensive_tds += get_mapped_value(
                        mapped,
                        "interceptionTouchdowns",
                        "interceptionReturnTouchdowns",
                        "TD"
                    )

                elif "fumble" in cat:
                    defensive_tds += get_mapped_value(
                        mapped,
                        "fumbleReturnTouchdowns",
                        "fumbleTouchdowns",
                        "TD"
                    )

                # Special-teams return TDs.
                elif "kickreturn" in cat or "kick return" in cat:
                    return_tds += get_mapped_value(
                        mapped,
                        "kickReturnTouchdowns",
                        "TD"
                    )

                elif "puntreturn" in cat or "punt return" in cat:
                    return_tds += get_mapped_value(
                        mapped,
                        "puntReturnTouchdowns",
                        "TD"
                    )

    return defensive_tds, return_tds

def blocked_kicks_from_team_stats(team_stats):
    """
    ESPN labels vary. Count blocked punts, field goals and PATs when present.
    Avoid counting the same stat twice by reading one matching value per label.
    """
    blocked = 0.0
    seen_labels = set()

    for stat in team_stats:
        names = [
            stat.get("name"),
            stat.get("label"),
            stat.get("displayName")
        ]
        label = " ".join(str(x or "") for x in names).lower().replace(" ", "")

        if not label or label in seen_labels:
            continue

        if (
            "blockedpunt" in label
            or "puntsblocked" in label
            or "blockedfieldgoal" in label
            or "fieldgoalsblocked" in label
            or "blockedpat" in label
            or "extrapointsblocked" in label
            or "blockedkick" in label
        ):
            blocked += to_float(stat.get("value", stat.get("displayValue")))
            seen_labels.add(label)

    return blocked

def defense_from_summary(summary, target_team, game_status):
    target_team = normalize_team(target_team)

    # A defense should not receive the +10 shutout bonus before kickoff.
    if game_status == "pre-game":
        return {
            "points": 0.0,
            "raw": {
                "pointsAllowed": 0,
                "pointsAllowedFantasy": 0.0,
                "sacks": 0.0,
                "interceptions": 0.0,
                "fumbleRecoveries": 0.0,
                "safeties": 0.0,
                "blockedKicks": 0.0,
                "defensiveTD": 0.0,
                "returnTD": 0.0
            },
            "note": "Game has not started; D/ST score remains 0.00."
        }

    scores = game_scores(summary)
    if target_team not in scores:
        return None

    opponent_teams = [team for team in scores if team != target_team]
    opponent = opponent_teams[0] if opponent_teams else None
    points_allowed = scores.get(opponent, 0) if opponent else 0

    team_stats = []
    for team_block in (summary.get("boxscore") or {}).get("teams") or []:
        abbr = normalize_team((((team_block.get("team") or {}).get("abbreviation")) or ""))
        if abbr == target_team:
            team_stats = team_block.get("statistics") or []
            break

    sacks = find_team_stat(team_stats, "sacks")
    interceptions = find_team_stat(team_stats, "interceptions")
    fumble_recoveries = find_team_stat(team_stats, "fumblesrecovered", "fumbles recovered")
    safeties = find_team_stat(team_stats, "safeties")
    blocked_kicks = blocked_kicks_from_team_stats(team_stats)

    defensive_tds, return_tds = player_return_and_defense_tds(summary, target_team)

    score = points_allowed_score(points_allowed)
    score += sacks * 1.0
    score += interceptions * 2.0
    score += fumble_recoveries * 2.0
    score += safeties * 2.0
    score += blocked_kicks * 2.0
    score += defensive_tds * 6.0
    score += return_tds * 6.0

    return {
        "points": round(score + 1e-9, 2),
        "raw": {
            "pointsAllowed": points_allowed,
            "pointsAllowedFantasy": points_allowed_score(points_allowed),
            "sacks": sacks,
            "interceptions": interceptions,
            "fumbleRecoveries": fumble_recoveries,
            "safeties": safeties,
            "blockedKicks": blocked_kicks,
            "defensiveTD": defensive_tds,
            "returnTD": return_tds
        },
        "note": "Full D/ST test: points allowed, sacks, INT, fumble recoveries, safeties, blocked kicks, defensive TDs, return TDs."
    }

def main():
    print("DFFL Step 3B full D/ST scoring test started")
    print(f"Test date: {TEST_DATE}")

    roster_data = json.loads(ROSTER_FILE.read_text(encoding="utf-8"))
    score_data = json.loads(SCORE_FILE.read_text(encoding="utf-8"))

    needed_teams = set()
    defense_teams = set()

    for owner in TARGET_OWNERS:
        for player in roster_data["rosters"][owner]["players"]:
            team = normalize_team(player.get("nflTeam") or "")
            if team:
                needed_teams.add(team)
            if player.get("position") == "DEF" and team:
                defense_teams.add(team)

    print(f"Needed NFL teams: {sorted(needed_teams)}")
    print(f"Defense teams: {sorted(defense_teams)}")

    board = fetch_json(SCOREBOARD_URL, {"dates": TEST_DATE, "limit": 100})
    events = board.get("events", [])
    print(f"ESPN events found: {len(events)}")

    summaries = []
    relevant_statuses = []
    summary_by_team = {}
    status_by_team = {}

    for event in events:
        teams = event_teams(event)
        if not (teams & needed_teams):
            continue

        event_id = str(event.get("id") or "")
        if not event_id:
            continue

        print(f"Relevant event: {event.get('name')} | id={event_id}")
        summary = fetch_json(SUMMARY_URL, {"event": event_id})
        summaries.append(summary)
        relevant_statuses.append(event_status(event))

        game_status = event_status(event)
        for team in teams:
            summary_by_team[team] = summary
            status_by_team[team] = game_status

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

            if position == "DEF":
                summary = summary_by_team.get(team)
                game_status = status_by_team.get(team, "pre-game")
                defense = defense_from_summary(summary, team, game_status) if summary else None

                if defense:
                    points = defense["points"]
                    found = True
                    raw = defense["raw"]
                else:
                    points = 0.0
                    found = False
                    raw = {}

                rows.append({
                    "position": position,
                    "name": name,
                    "nflTeam": team,
                    "points": points,
                    "foundInFeed": found,
                    "raw": raw,
                    "note": defense.get("note", "Full D/ST scoring.") if defense else "No game data found."
                })

                total += points
                print(f"{position:4} {name}: {points:.2f} | found={found} | raw={raw}")
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
        print(f"{owner} total including basic D/ST: {total:.2f}")

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
        "testStage": "two-owner-offense-plus-full-defense",
        "owners": TARGET_OWNERS,
        "defenseIncluded": True,
        "defenseNote": "D/ST includes points allowed, sacks, INT, fumble recoveries, safeties, blocked kicks, defensive TDs and kick/punt return TDs."
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
    print("DFFL Step 3B full D/ST completed successfully")

if __name__ == "__main__":
    main()
