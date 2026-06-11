import json
import time
import urllib.request
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.models.elo_predictor import EloPredictor

TEAM_MAP_TO_POLY = {
    "USA": "United States",
    "Congo DR": "DR Congo",
}
POLY_TEAM_TO_OURS = {
    "United States": "USA",
    "DR Congo": "Congo DR",
    "Cape Verde": "Cabo Verde",
    "Ivory Coast": "C\u00f4te d'Ivoire",
    "Democratic Republic of Congo": "Congo DR",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
}

HEADERS = {"User-Agent": "Mozilla/5.0"}
API_BASE = "https://gamma-api.polymarket.com"
TAG_ID_FIFWC = 102232
TOURNAMENT_WINNER_EVENT_ID = 30615

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
FIXTURES_PATH = os.path.join(DATA_DIR, 'fixtures_wc2026.json')
RATINGS_PATH = os.path.join(DATA_DIR, 'team_ratings.json')
PREDICTIONS_DIR = os.path.join(os.path.dirname(__file__), '..', 'predictions')
OUTPUT_PATH = os.path.join(PREDICTIONS_DIR, 'latest.json')

def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def get_all_tag_events(tag_id=TAG_ID_FIFWC):
    all_events = []
    offset = 0
    limit = 100
    while True:
        url = "%s/events?tag_id=%d&active=true&closed=false&limit=%d&offset=%d&order=start_date&ascending=true" % (
            API_BASE, tag_id, limit, offset)
        batch = fetch_json(url)
        if not batch:
            break
        all_events.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
        time.sleep(0.3)
    return all_events

def strip_accent(s):
    return s.replace("\u00e7", "c").replace("\u00f6", "o").replace("\u00fc", "u") \
            .replace("\u00c7", "C").replace("\u00d6", "O").replace("\u00dc", "U") \
            .replace("\u015e", "S").replace("\u015f", "s").replace("\u0130", "I")

def parse_prices(prices):
    if isinstance(prices, list):
        return prices
    if isinstance(prices, str):
        try:
            return json.loads(prices)
        except (json.JSONDecodeError, TypeError):
            pass
    return []

def extract_match_markets(events):
    match_map = {}
    for ev in events:
        markets = ev.get("markets", [])
        if len(markets) != 3:
            continue
        title = ev.get("title", "")
        slug = ev.get("slug", "")
        if " vs. " not in title:
            continue
        parts = title.split(" vs. ")
        home_name = parts[0].strip()
        away_name = parts[1].strip()

        home_win = away_win = draw_price = None
        for m in markets:
            q = m.get("question", "")
            raw_prices = m.get("outcomePrices", [])
            prices = parse_prices(raw_prices)
            if not prices or len(prices) < 2:
                continue
            price = float(prices[0])
            if "end in a draw" in q:
                draw_price = price
            elif "win on 20" in q:
                team = q.replace("Will ", "").split(" win on 20")[0].strip()
                if strip_accent(team).lower() == strip_accent(home_name).lower():
                    home_win = price
                elif strip_accent(team).lower() == strip_accent(away_name).lower():
                    away_win = price
        if home_win is not None and away_win is not None and draw_price is not None:
            match_map[slug] = {
                "home_name": strip_accent(home_name),
                "away_name": strip_accent(away_name),
                "poly_home": home_win,
                "poly_draw": draw_price,
                "poly_away": away_win,
                "slug": slug,
            }
    return match_map

def extract_tournament_markets(events):
    for ev in events:
        ev_id = str(ev.get("id", ""))
        if ev_id == str(TOURNAMENT_WINNER_EVENT_ID):
            markets = ev.get("markets", [])
            result = {}
            for m in markets:
                q = m.get("question", "")
                raw_prices = m.get("outcomePrices", [])
                prices = parse_prices(raw_prices)
                if not prices or len(prices) < 1:
                    continue
                team = q.replace("Will ", "").replace(" win the 2026 FIFA World Cup?", "").strip()
                if team in ("Any Other Team",) or team.startswith("Team "):
                    continue
                price = float(prices[0])
                if price > 0:
                    result[team] = price
            return result
    return {}

def extract_group_markets(events):
    result = {}
    for ev in events:
        title = ev.get("title", "")
        if "Group" not in title or "Winner" not in title:
            continue
        group = title.replace("World Cup Group ", "").replace(" Winner", "")
        for m in ev.get("markets", []):
            q = m.get("question", "")
            raw_prices = m.get("outcomePrices", [])
            prices = parse_prices(raw_prices)
            if not prices:
                continue
            team = q.replace("Will ", "").split(" win Group")[0].strip()
            if team in ("another team",) or not team:
                continue
            price = float(prices[0])
            result["%s:%s" % (group, team)] = price
    return result

def find_match(fixture, match_map):
    home_raw = fixture.get("home_team")
    away_raw = fixture.get("away_team")
    if not home_raw or not away_raw:
        return None
    home = TEAM_MAP_TO_POLY.get(home_raw, home_raw)
    away = TEAM_MAP_TO_POLY.get(away_raw, away_raw)
    h = strip_accent(home).lower()
    a = strip_accent(away).lower()
    candidates = []
    for slug, data in match_map.items():
        dh = strip_accent(data["home_name"]).lower()
        da = strip_accent(data["away_name"]).lower()
        if (dh == h and da == a) or (dh == a and da == h):
            candidates.append((slug, data))
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0][1]
    for slug, data in candidates:
        if strip_accent(data["home_name"]).lower() == h:
            return data
    return candidates[0][1]

def value_pct(elo_p, market_p):
    if market_p <= 0:
        return 0.0
    return round((elo_p - market_p) / market_p * 100, 1)

def elo_to_winner_prob(predictor, team, all_teams):
    r = predictor.get_rating(team)
    if r <= 0:
        return 0.0
    total = sum(max(predictor.get_rating(t), 1) for t in all_teams if t)
    return r / total

def main():
    print("Loading fixtures...")
    with open(FIXTURES_PATH, encoding="utf-8") as f:
        fixtures = json.load(f)

    print("Loading ELO predictor...")
    predictor = EloPredictor(RATINGS_PATH)

    print("Fetching all tag=102232 events from Polymarket...")
    all_events = get_all_tag_events()
    print("  Total events: %d" % len(all_events))

    match_map = extract_match_markets(all_events)
    print("  Match events (1X2): %d" % len(match_map))

    tournament_poly = extract_tournament_markets(all_events)
    print("  Tournament winner teams: %d" % len(tournament_poly))

    group_poly = extract_group_markets(all_events)
    print("  Group winner markets: %d" % len(group_poly))

    all_team_names = list(set(
        [m["home_team"] for m in fixtures] + [m["away_team"] for m in fixtures]
    ))

    matches_out = []
    match_count = 0
    for fx in fixtures:
        home = fx["home_team"]
        away = fx["away_team"]
        poly = find_match(fx, match_map)
        probs = predictor.predict_proba(home, away)
        home_xg = probs["home"] * 2.5 + probs["draw"] * 1.0
        away_xg = probs["away"] * 2.5 + probs["draw"] * 1.0

        match_entry = {
            "id": fx["id"],
            "home": home,
            "away": away,
            "league": fx.get("league", ""),
            "date": fx["date"],
            "stage": fx.get("stage", ""),
            "venue": fx.get("venue", ""),
            "group": fx.get("group", ""),
            "probabilities": probs,
            "expected_goals": {"home": round(home_xg, 2), "away": round(away_xg, 2)},
            "model": "elo",
        }

        if poly:
            match_entry["polymarket"] = {
                "home": poly["poly_home"],
                "draw": poly["poly_draw"],
                "away": poly["poly_away"],
            }
            match_entry["value_pct"] = {
                "home": value_pct(probs["home"], poly["poly_home"]),
                "draw": value_pct(probs["draw"], poly["poly_draw"]),
                "away": value_pct(probs["away"], poly["poly_away"]),
            }
            match_count += 1
        else:
            match_entry["polymarket"] = None
            match_entry["value_pct"] = None

        matches_out.append(match_entry)

    # Preserve news_sentiment from previous run so it accumulates across pipeline runs
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            old_by_id = {m.get("id"): m for m in old_data.get("matches", []) if m.get("id")}
            for m in matches_out:
                mid = m.get("id")
                if mid is not None and mid in old_by_id:
                    old = old_by_id[mid]
                    if old.get("news_sentiment"):
                        m["news_sentiment"] = old["news_sentiment"]
                        old_sources = old.get("news_sources", [])
                        m["news_sources"] = [s for s in old_sources if 'example.com' not in s]
        except Exception as e:
            print(f"Warning: could not preserve news_sentiment: {e}")

    tournament_out = {}
    for poly_name, poly_price in sorted(tournament_poly.items()):
        cleaned = strip_accent(poly_name)
        our = POLY_TEAM_TO_OURS.get(cleaned) or POLY_TEAM_TO_OURS.get(poly_name)
        if our is None:
            for k, v in POLY_TEAM_TO_OURS.items():
                if strip_accent(k).lower() == cleaned.lower():
                    our = v
                    break
        if our is None:
            our = cleaned
        if our not in all_team_names:
            continue
        r = predictor.get_rating(our)
        elo_p = elo_to_winner_prob(predictor, our, all_team_names)
        tournament_out[our] = {
            "team": our,
            "elo_rating": r,
            "polymarket_price": poly_price,
            "elo_probability": round(elo_p, 4),
            "value_pct": value_pct(elo_p, poly_price),
        }

    groups_out = {}
    for key, poly_price in group_poly.items():
        parts = key.split(":", 1)
        if len(parts) != 2:
            continue
        group_name, poly_team = parts
        cleaned = strip_accent(poly_team)
        our = POLY_TEAM_TO_OURS.get(cleaned) or POLY_TEAM_TO_OURS.get(poly_team)
        if our is None:
            for k, v in POLY_TEAM_TO_OURS.items():
                if strip_accent(k).lower() == cleaned.lower():
                    our = v
                    break
        if our is None:
            our = cleaned
        groups_out["%s:%s" % (group_name, our)] = {
            "group": group_name,
            "team": our,
            "polymarket_price": poly_price,
        }

    output = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "model": "World Football Elo Ratings (eloratings.net)",
        "model_version": "1.0.0-elo",
        "notes": "Predicciones basadas en Elo ratings. Polymarket odds via gamma-api.polymarket.com.",
        "matches": matches_out,
        "polymarket": {
            "tournament_winner": tournament_out,
            "group_winner": groups_out,
        },
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("Saved to %s" % OUTPUT_PATH)

    matched = sum(1 for m in matches_out if m["polymarket"] is not None)
    print("Matches with Polymarket comparison: %d / %d" % (matched, len(matches_out)))

    top = sorted(
        [m for m in matches_out if m["value_pct"]],
        key=lambda m: max(abs(m["value_pct"]["home"]), abs(m["value_pct"]["draw"]), abs(m["value_pct"]["away"])),
        reverse=True
    )[:15]
    print("\nTop value discrepancies (ELO vs Polymarket):")
    for m in top:
        signs = []
        for out, label in [("home", m["home"]), ("draw", "Draw"), ("away", m["away"])]:
            v = m["value_pct"][out]
            if abs(v) >= 10:
                direction = "UNDER" if v < 0 else "OVER"
                signs.append("%s %s %.1f%%" % (label, direction, abs(v)))
        if signs:
            print("  %s vs %s: %s" % (m["home"], m["away"], " | ".join(signs)))

if __name__ == "__main__":
    main()
