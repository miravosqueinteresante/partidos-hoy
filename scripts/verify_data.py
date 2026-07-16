import json

with open(r'C:\Users\pc\Desktop\Proyectos\Predicciones Futbol\data\historical_wc_data.json', encoding='utf-8') as f:
    d = json.load(f)

m = d['matches']
print('Top-level keys:', list(d.keys()))
print('Total matches:', len(m))
print('First match keys:', list(m[0].keys()))
print()

# Check specific matchups
pairs = [('Mexico', 'Germany'), ('Argentina', 'Netherlands'), ('Brazil', 'France'), ('England', 'Germany')]
for team1, team2 in pairs:
    found = [x for x in m if (x['home_team'] == team1 and x['away_team'] == team2) or (x['home_team'] == team2 and x['away_team'] == team1)]
    print(f'{team1} vs {team2}: {len(found)} encounters')
    for x in found[:3]:
        s = [p['player'] for p in x['scorers'][:3]]
        print(f'  {x["year"]}: {x["home_team"]} {x["home_score"]}-{x["away_score"]} {x["away_team"]} (scorers: {s})')

# Check a sample match with scorers
print()
print('Sample match with scorers:')
for x in m:
    if x['scorers']:
        print(json.dumps(x, indent=2, ensure_ascii=False)[:500])
        break
