import json, csv, io, urllib.request

team_name_map = {
    "USA": "United States", "Turkiye": "Turkey",
    "Cote d'Ivoire": "Ivory Coast", "Curacao": "Curacao",
    "Cabo Verde": "Cabo Verde", "Congo DR": "Congo DR",
    "Korea Republic": "Korea Republic", "IR Iran": "IR Iran",
    "Czechia": "Czechia", "Netherlands": "Netherlands",
}

wc_teams_map = {
    "Mexico": "Mexico", "South Africa": "South Africa",
    "Korea Republic": "Korea Rep.", "Czechia": "Czechia",
    "Canada": "Canada", "Bosnia and Herzegovina": "Bosnia-Herzegovina",
    "Qatar": "Qatar", "Switzerland": "Switzerland",
    "Brazil": "Brazil", "Morocco": "Morocco", "Haiti": "Haiti",
    "Scotland": "Scotland", "USA": "United States",
    "Paraguay": "Paraguay", "Australia": "Australia",
    "Turkiye": "Turkey", "Germany": "Germany",
    "Curacao": "Curacao", "Cote d'Ivoire": "Ivory Coast",
    "Ecuador": "Ecuador", "Netherlands": "Netherlands",
    "Japan": "Japan", "Sweden": "Sweden", "Tunisia": "Tunisia",
    "Belgium": "Belgium", "Egypt": "Egypt",
    "IR Iran": "Iran", "New Zealand": "New Zealand",
    "Spain": "Spain", "Cabo Verde": "Cape Verde",
    "Saudi Arabia": "Saudi Arabia", "Uruguay": "Uruguay",
    "France": "France", "Senegal": "Senegal", "Iraq": "Iraq",
    "Norway": "Norway", "Argentina": "Argentina",
    "Algeria": "Algeria", "Austria": "Austria", "Jordan": "Jordan",
    "Portugal": "Portugal", "Congo DR": "Congo DR",
    "Uzbekistan": "Uzbekistan", "Colombia": "Colombia",
    "England": "England", "Croatia": "Croatia",
    "Ghana": "Ghana", "Panama": "Panama",
}

resp = urllib.request.urlopen("https://www.eloratings.net/World.tsv")
reader = csv.reader(io.StringIO(resp.read().decode("utf-8")), delimiter="\t")
resp2 = urllib.request.urlopen("https://www.eloratings.net/en.teams.tsv")
names = {r[0]: r[1] if len(r) > 1 else r[0] for r in csv.reader(io.StringIO(resp2.read().decode("utf-8")), delimiter="\t") if r}

all_elo = {}
for row in reader:
    if row and len(row) >= 4:
        code = row[2]
        all_elo[code] = {"name": names.get(code, code), "rating": float(row[3])}

result = {}
for fixture_name, search_name in wc_teams_map.items():
    code = None
    for c, d in all_elo.items():
        if search_name.lower() in d["name"].lower() or d["name"].lower() in search_name.lower():
            code = c
            break
    if code:
        result[fixture_name] = {
            "elo": all_elo[code]["rating"],
            "eloratings_name": all_elo[code]["name"],
        }
    else:
        print(f"MISSING: {fixture_name} -> {search_name}")

with open("data/team_ratings.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(f"\nSaved {len(result)} teams to data/team_ratings.json")
for t in sorted(result, key=lambda x: result[x]["elo"], reverse=True):
    print(f"  {t:30s}  {result[t]['elo']:>5.0f}")
