"""
build_historical_data.py — Convierte Fjelstul World Cup Database → historical_wc_data.json
Lee el dataset oficial y extrae partidos + goleadores de todos los mundiales masculinos (1930-2022).
"""

import json
import os
from datetime import datetime

SRC = r"C:\Users\pc\Desktop\Proyectos\Predicciones Futbol\data\worldcup_fjelstul.json"
DST = r"C:\Users\pc\Desktop\Proyectos\Predicciones Futbol\data\historical_wc_data.json"

with open(SRC, "r", encoding="utf-8") as f:
    db = json.load(f)

matches_raw = db["matches"]
goals_raw = db["goals"]

STAGES_FLAT = {
    "group stage", "first round", "second round",
    "group stage 1", "group stage 2"
}

goals_by_match = {}
for g in goals_raw:
    mid = g["match_id"]
    goals_by_match.setdefault(mid, []).append(g)

output_matches = []
for m in matches_raw:
    tname = m["tournament_name"]
    if "Women" in tname:
        continue

    year = int(tname[:4])
    stage = m["stage_name"]
    is_knockout = m["knockout_stage"] == 1

    scorers = []
    match_goals = goals_by_match.get(m["match_id"], [])
    for g in match_goals:
        player = f'{g["given_name"]} {g["family_name"]}'
        minute = g["minute_regulation"]
        extra = g["minute_stoppage"]
        team = "home" if g["home_team"] == 1 else "away"
        own = g["own_goal"] == 1
        pen = g["penalty"] == 1

        entry = {
            "player": player.strip(),
            "minute": minute,
            "team": team,
            "score": None,
        }
        if extra:
            entry["extra_time"] = f"+{extra}"
        if own:
            entry["type"] = "own_goal"
        if pen:
            entry["type"] = "penalty"
        scorers.append(entry)

    entry = {
        "year": year,
        "stage": stage,
        "group": m.get("group_name") or None,
        "round": "knockout" if is_knockout else "group",
        "match_date": m["match_date"],
        "stadium_name": m["stadium_name"],
        "city_name": m["city_name"],
        "country_name": m["country_name"],
        "home_team": m["home_team_name"],
        "away_team": m["away_team_name"],
        "home_score": m["home_team_score"],
        "away_score": m["away_team_score"],
        "extra_time": m["extra_time"] == 1,
        "penalty_shootout": m["penalty_shootout"] == 1,
        "score_penalties": m.get("score_penalties") or None,
        "result": m["result"],
        "scorers": scorers,
    }
    output_matches.append(entry)

output = {
    "meta": {
        "generated_at": datetime.utcnow().isoformat(),
        "source": "Fjelstul World Cup Database (jfjelstul/worldcup)",
        "total_matches": len(output_matches),
        "tournaments_covered": sorted(set(m["year"] for m in output_matches)),
    },
    "matches": output_matches,
}

with open(DST, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

men = [m for m in matches_raw if "Women" not in m["tournament_name"]]
print(f"Matches en dataset: {len(men)}")
print(f"Matches en output:  {len(output_matches)}")
print(f"Goles totales:      {sum(len(m['scorers']) for m in output_matches)}")
print(f"Torneos cubiertos:  {output['meta']['tournaments_covered']}")
print(f"\nArchivo escrito: {DST}")
