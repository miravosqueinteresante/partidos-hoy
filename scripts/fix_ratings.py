import json
with open("data/team_ratings.json") as f:
    data = json.load(f)
data["Korea Republic"] = {"elo": 1756.0, "eloratings_name": "South Korea"}
data["Bosnia and Herzegovina"] = {"elo": 1591.0, "eloratings_name": "Bosnia and Herzegovina"}
data["Curacao"] = {"elo": 1433.0, "eloratings_name": "Curaçao"}
with open("data/team_ratings.json", "w") as f:
    json.dump(data, f, indent=2)
print(f"Total: {len(data)} teams")
for t in sorted(data, key=lambda x: data[x]["elo"], reverse=True):
    print(f"  {t:30s}  {data[t]['elo']:>5.0f}")
