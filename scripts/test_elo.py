import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from src.models.elo_predictor import EloPredictor

with open("data/fixtures_wc2026.json", encoding="utf-8") as f:
    fixtures = json.load(f)
df = pd.DataFrame(fixtures)
predictor = EloPredictor("data/team_ratings.json")
output = predictor.generate(df)
parsed = json.loads(output)
print(f"Matches: {len(parsed['matches'])}")
print(f"Generated: {parsed['generated_at']}")
print(f"Model: {parsed['model']}")
print()
for m in parsed["matches"][:10]:
    p = m["probabilities"]
    xg = m["expected_goals"]
    print(f"{m['home']:20s} vs {m['away']:20s}  1:{p['home']*100:5.1f}%  X:{p['draw']*100:5.1f}%  2:{p['away']*100:5.1f}%  xG:{xg['home']:.1f}-{xg['away']:.1f}")
print("...")
# Save a sample
with open("predictions/test_latest.json", "w", encoding="utf-8") as f:
    f.write(output)
