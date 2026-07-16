import urllib.request, csv, io, json

resp = urllib.request.urlopen("https://www.eloratings.net/en.teams.tsv")
data = resp.read().decode("utf-8")
reader = csv.reader(io.StringIO(data), delimiter="\t")
team_names = {}
for row in reader:
    if row:
        code = row[0]
        name = row[1] if len(row) > 1 else code
        team_names[code] = name

resp = urllib.request.urlopen("https://www.eloratings.net/World.tsv")
data = resp.read().decode("utf-8")
reader = csv.reader(io.StringIO(data), delimiter="\t")
all_ratings = {}
for row in reader:
    if row and len(row) >= 4:
        code = row[2]
        rating = row[3]
        name = team_names.get(code, code)
        all_ratings[name.lower()] = {"name": name, "code": code, "rating": float(rating)}

wc_teams = [
    "Mexico", "South Africa", "Korea Republic", "Czechia",
    "Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland",
    "Brazil", "Morocco", "Haiti", "Scotland",
    "USA", "Paraguay", "Australia", "Turkiye",
    "Germany", "Curacao", "Cote d'Ivoire", "Ecuador",
    "Netherlands", "Japan", "Sweden", "Tunisia",
    "Belgium", "Egypt", "IR Iran", "New Zealand",
    "Spain", "Cabo Verde", "Saudi Arabia", "Uruguay",
    "France", "Senegal", "Iraq", "Norway",
    "Argentina", "Algeria", "Austria", "Jordan",
    "Portugal", "Congo DR", "Uzbekistan", "Colombia",
    "England", "Croatia", "Ghana", "Panama",
]

elo_map = {}
missing = []
for t in wc_teams:
    t_lower = t.lower()
    found = False
    for key, val in all_ratings.items():
        if t_lower in key or val["name"].lower() in t_lower:
            elo_map[t] = val["rating"]
            found = True
            break
    if not found:
        # try partial match
        for key, val in all_ratings.items():
            if t_lower.split()[-1] in key or key.split()[-1] in t_lower:
                elo_map[t] = val["rating"]
                found = True
                break
    if not found:
        missing.append(t)

print(f"Found {len(elo_map)}/48 World Cup teams")
print(f"Missing: {missing}")
print()
for t in sorted(wc_teams, key=lambda x: elo_map.get(x, 0), reverse=True):
    r = elo_map.get(t, "N/A")
    print(f"  {t:30s} -> ELO: {r}")
with open("data/wc_elo_ratings.json", "w", encoding="utf-8") as f:
    json.dump(elo_map, f, indent=2)
