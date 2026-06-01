# Plan de Implementación: Partidos Hoy — v1.0

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> 
> **v1.0 = Copa del Mundo 2026 (104 partidos, 48 selecciones).** Después del 19 de julio se expandirá a más ligas bajo la marca Partidos Hoy.

**Goal:** v1.0 enfocada exclusivamente en la **Copa del Mundo 2026**. Pipeline Python en GitHub Actions genera predicciones ELO desde fixtures hardcodeados (`data/fixtures_wc2026.json`) + ratings de eloratings.net (`data/team_ratings.json`). Plugin WordPress consume el JSON vía shortcode con Freemius. Producto: **Partidos Hoy - Pronósticos de Fútbol**, alojado en partidoshoy.futbol.

**Architecture:** Fuente única de datos: fixtures hardcodeados en `data/fixtures_wc2026.json` (104 partidos del Mundial). Ratings ELO de selecciones desde eloratings.net (scraping de `World.tsv`, 244 equipos). Predictor ELO con fórmula clásica (home advantage +100, K=400) genera probabilidades 1X2 y expected goals. Sin dependencias de APIs externas ni rate limits. Sin ML. v2.0 post-Mundial añadirá XGBoost con datos históricos de ligas regulares.

**Tech Stack:** Python 3.12, pandas, numpy, requests (scraping eloratings.net), GitHub Actions, PHP 8.x, WordPress 6.x, Freemius SDK

**Estructura del repositorio:**
```
partidos-hoy/
├── .github/workflows/
│   └── worldcup-pipeline.yml         # Único workflow: cada 6h durante Jun-Jul
├── src/
│   ├── __init__.py
│   ├── config.py                      # Config ELO + rutas de datos
│   └── models/
│       ├── __init__.py
│       └── elo_predictor.py           # Predictor ELO (producción)
├── data/
│   ├── fixtures_wc2026.json           # 104 fixtures hardcodeados
│   └── team_ratings.json              # ELO ratings de 48 selecciones
├── scripts/
│   ├── build_ratings.py               # Scrapea eloratings.net
│   ├── extract_elo.py                 # Extrae ELO ratings
│   ├── fix_ratings.py                 # Corrige nombres de equipos
│   └── test_elo.py                    # Prueba local del predictor
├── predictions/
│   └── test_latest.json               # Output de prueba local
├── wp-plugin/
│   ├── partidos-hoy.php               # Plugin principal
│   ├── includes/
│   │   ├── class-data-client.php      # Cliente HTTP para JSON
│   │   ├── class-shortcode.php        # Shortcode y renderizado
│   │   └── class-admin.php            # Admin settings
│   ├── assets/
│   │   └── css/
│   │       └── frontend.css           # Estilos del shortcode
│   ├── vendor/freemius/               # Freemius SDK
│   └── readme.txt                     # WordPress.org readme
├── requirements.txt                    # pandas, numpy, requests, pytest
├── .gitignore
└── README.md
```

---

## Fase 1: Fundación Python

### Task 1: Configurar repositorio y dependencias

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `README.md`
- Create: `src/__init__.py`
- Create: `src/config.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Crear estructura de directorios**

```bash
mkdir -p partidos-hoy/.github/workflows
mkdir -p partidos-hoy/src/{data,features,models,utils}
mkdir -p partidos-hoy/tests
mkdir -p partidos-hoy/wp-plugin/{includes,assets/css,languages}
cd partidos-hoy
```

- [ ] **Step 2: Crear requirements.txt**

```
# Core
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=2.0.0
catboost>=1.2.0

# Data sources
requests>=2.31.0
ratelimit>=2.2.1
soccerdata>=0.4.0              # FBref/ClubElo scraping (fallback)

# Testing
pytest>=7.4.0
pytest-mock>=3.11.0
```

- [ ] **Step 3: Crear .gitignore**

```
__pycache__/
*.pyc
.env
data/raw/
data/processed/
mlruns/
.vscode/
.idea/
*.egg-info/
dist/
build/
```

- [ ] **Step 4: Crear src/config.py**

```python
import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    # ─── v1.0: SOLO Mundial 2026 ───────────────────────────────
    # Post-Mundial (julio 2026+) se expandirá a ligas regulares.
    # World Cup 2026: league=1, season=2026
    # 48 teams, 12 groups of 4, 104 matches, June 11 - July 19
    worldcup_league_id: int = 1
    worldcup_season: int = 2026

    # ─── Fuente Primaria: API-Football ──────────────────────────
    api_football_key: str = os.getenv("API_FOOTBALL_KEY", "")
    api_football_base: str = "https://v3.football.api-sports.io"
    api_football_rate_limit: int = 10  # requests per minute (free tier)
    api_football_daily_limit: int = 100

    # ─── Fallback 1: FBref vía soccerdata ───────────────────────
    # scraping, sin rate limit. Usa soccerdata (gratis, MIT)
    # URL base para scraping manual: https://fbref.com/en/comps/1/2026/schedule/
    fbref_wc_url: str = "https://fbref.com/en/comps/1/2026/schedule/2026-World-Cup-Schedule"

    # ─── Fallback 2: football-data.org ──────────────────────────
    football_data_org_key: str = os.getenv("FOOTBALL_DATA_ORG_KEY", "")
    football_data_org_base: str = "https://api.football-data.org/v4"
    football_data_org_rate_limit: int = 10  # req/min (free tier)
    # Nota: football-data.org no tiene World Cup completa en free tier
    # (solo 12 competiciones top). Usar como fallback parcial.

    # ─── Datos históricos para entrenamiento ────────────────────
    # football-data.co.uk no cubre selecciones nacionales.
    # Para el Mundial, los datos históricos se obtienen de:
    # - ClubElo (vía soccerdata)
    # - Kaggle European Soccer Database
    # - API-Football fixtures históricos
    historical_data_dir: str = "data/historical"

    # ─── Directorios ───────────────────────────────────────────
    data_dir: str = "data"
    raw_dir: str = "data/raw"
    processed_dir: str = "data/processed"
    predictions_dir: str = "predictions"
    model_dir: str = "models/weights"

    # ─── Entrenamiento ─────────────────────────────────────────
    min_matches_for_training: int = 50   # menos partidos para selecciones
    test_size: float = 0.15
    random_state: int = 42

    # ─── Thresholds ────────────────────────────────────────────
    brier_threshold: float = 0.22
    psi_threshold: float = 0.25

    prediction_cache_ttl: int = 21600  # 6 hours in seconds


config = Config()
```

- [ ] **Step 5: Commit**

```bash
git init
git add -A
git commit -m "chore: initial repo structure with config and dependencies"
```

---

### Task 2: Rate Limiter utilitario

**Files:**
- Create: `src/utils/rate_limiter.py`
- Test: `tests/test_rate_limiter.py`

- [ ] **Step 1: Escribir el test**

```python
import time
from src.utils.rate_limiter import RateLimiter


def test_rate_limiter_enforces_limit():
    limiter = RateLimiter(max_per_minute=60)
    start = time.time()
    for _ in range(60):
        limiter.wait_if_needed()
    elapsed = time.time() - start
    assert elapsed < 2.0, "60 calls should complete quickly under 60/min limit"


def test_rate_limiter_slows_down():
    limiter = RateLimiter(max_per_minute=2)
    start = time.time()
    for _ in range(4):
        limiter.wait_if_needed()
    elapsed = time.time() - start
    assert elapsed >= 60.0, "4 calls at 2/min should take at least 60s"
```

- [ ] **Step 2: Verificar que falla**

Run: `python -m pytest tests/test_rate_limiter.py -v`
Expected: FAIL (RateLimiter not defined)

- [ ] **Step 3: Implementar RateLimiter**

```python
import time
import threading


class RateLimiter:
    def __init__(self, max_per_minute: int = 10):
        self.max_per_minute = max_per_minute
        self.timestamps: list[float] = []
        self.lock = threading.Lock()

    def wait_if_needed(self):
        with self.lock:
            now = time.time()
            cutoff = now - 60.0
            self.timestamps = [t for t in self.timestamps if t > cutoff]
            if len(self.timestamps) >= self.max_per_minute:
                sleep_time = self.timestamps[0] + 60.0 - now
                if sleep_time > 0:
                    time.sleep(sleep_time)
            self.timestamps.append(time.time())
```

- [ ] **Step 4: Verificar que pasa**

Run: `python -m pytest tests/test_rate_limiter.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/utils/rate_limiter.py tests/test_rate_limiter.py
git commit -m "feat: add rate limiter for API calls"
```

---

### Task 3: Cliente API-Football (fuente primaria)

**Propósito:** Fuente primaria de datos vivos del Mundial. En caso de fallar, el DataCascade (Task 3d) intentará FBref primero, football-data.org después. El APIFootballClient se mantiene limpio: solo habla con API-Football.

**Files:**
- Create: `src/data/api_football_client.py`
- Modify: `src/config.py`
- Test: `tests/test_api_football_client.py`

- [ ] **Step 1: Escribir el test**

```python
import json
import pytest
from src.data.api_football_client import APIFootballClient
from src.config import config


def test_fetch_fixtures_returns_list(mocker):
    mock_response = {
        "response": [
            {"fixture": {"id": 1, "date": "2026-06-01"},
             "league": {"id": 9, "name": "Premier League"},
             "teams": {"home": {"name": "Arsenal"}, "away": {"name": "Chelsea"}}}
        ]
    }
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=200,
                                          json=lambda: mock_response))
    client = APIFootballClient(api_key="test_key")
    result = client.fetch_fixtures(league_id=9, season=2025)
    assert len(result) == 1
    assert result[0]["teams"]["home"]["name"] == "Arsenal"


def test_fetch_standings_returns_teams(mocker):
    mock_response = {
        "response": [{
            "league": {
                "standings": [[
                    {"rank": 1, "team": {"name": "Arsenal", "id": 42},
                     "points": 85, "goalsDiff": 45}
                ]]
            }
        }]
    }
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=200,
                                          json=lambda: mock_response))
    client = APIFootballClient(api_key="test_key")
    result = client.fetch_standings(league_id=9, season=2025)
    assert len(result) == 1
    assert result[0]["team"]["name"] == "Arsenal"


def test_fetch_worldcup_fixtures(mocker):
    mock_response = {
        "response": [
            {"fixture": {"id": 100, "date": "2026-06-11T21:00:00+00:00"},
             "league": {"id": 1, "name": "FIFA World Cup", "season": 2026},
             "teams": {"home": {"name": "Mexico"}, "away": {"name": "Canada"}}}
        ]
    }
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=200,
                                          json=lambda: mock_response))
    client = APIFootballClient(api_key="test_key")
    result = client.fetch_worldcup_fixtures()
    assert len(result) == 1
    assert result[0]["league"]["id"] == 1
    assert result[0]["teams"]["home"]["name"] == "Mexico"


def test_fetch_multiple_fixtures(mocker):
    mock_response = {"response": [{"fixture": {"id": 1}}, {"fixture": {"id": 2}}]}
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=200,
                                          json=lambda: mock_response))
    client = APIFootballClient(api_key="test_key")
    result = client.fetch_multiple_fixtures([1, 2])
    assert len(result) == 2


def test_fetch_prediction(mocker):
    mock_response = {
        "response": [{
            "predictions": {
                "winner": {"name": "Argentina"},
                "percent": {"home": 45, "draw": 30, "away": 25}
            }
        }]
    }
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=200,
                                          json=lambda: mock_response))
    client = APIFootballClient(api_key="test_key")
    result = client.fetch_prediction(fixture_id=100)
    assert result["predictions"]["winner"]["name"] == "Argentina"


def test_check_coverage(mocker):
    mock_response = {
        "response": [{
            "seasons": [{
                "coverage": {
                    "fixtures": {"events": True, "lineups": True},
                    "standings": True,
                    "predictions": True,
                    "odds": True,
                }
            }]
        }]
    }
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=200,
                                          json=lambda: mock_response))
    client = APIFootballClient(api_key="test_key")
    cov = client.check_coverage(league_id=1, season=2026)
    assert cov["predictions"] is True
    assert cov["odds"] is True


def test_daily_limit_enforced(mocker):
    mock_get = mocker.patch("requests.Session.get",
                            return_value=mocker.Mock(status_code=200,
                                                     json=lambda: {"response": []}))
    client = APIFootballClient(api_key="test_key")
    for _ in range(config.api_football_daily_limit):
        client.fetch_fixtures(league_id=9, season=2025)
    with pytest.raises(RuntimeError, match="Daily limit reached"):
        client.fetch_fixtures(league_id=10, season=2025)
```

- [ ] **Step 2: Verificar que falla**

Run: `python -m pytest tests/test_api_football_client.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar APIFootballClient**

```python
import json
import os
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import requests

from src.config import config
from src.utils.rate_limiter import RateLimiter


class APIFootballClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.api_football_key
        self.base_url = config.api_football_base
        self._daily_count = 0
        self._daily_reset = date.today()
        self.session = requests.Session()
        self.session.headers.update({
            "x-apisports-key": self.api_key
        })
        self.rate_limiter = RateLimiter(max_per_minute=config.api_football_rate_limit)

    def _request(self, endpoint: str, params: Dict[str, Any]) -> List[Dict]:
        self._check_daily_limit()
        self.rate_limiter.wait_if_needed()
        resp = self.session.get(f"{self.base_url}/{endpoint}", params=params)
        self._daily_count += 1
        if resp.status_code != 200:
            raise RuntimeError(f"API error {resp.status_code}: {resp.text}")
        data = resp.json()
        if data.get("errors") and any(data["errors"].values()):
            raise RuntimeError(f"API error: {data['errors']}")
        return data.get("response", [])

    def _check_daily_limit(self):
        today = date.today()
        if today != self._daily_reset:
            self._daily_count = 0
            self._daily_reset = today
        if self._daily_count >= config.api_football_daily_limit:
            raise RuntimeError("Daily limit reached - free tier allows 100 req/day")

    # ─── Fixtures ───────────────────────────────────────────────

    def fetch_fixtures(self, league_id: int, season: int,
                       date_from: Optional[str] = None,
                       date_to: Optional[str] = None) -> List[Dict]:
        params = {"league": league_id, "season": season}
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to
        return self._request("fixtures", params)

    def fetch_fixtures_by_round(self, league_id: int, season: int,
                                 round_name: str) -> List[Dict]:
        """Filtrar fixtures por ronda (Group stage, Quarter-finals, etc.)"""
        return self._request("fixtures", {
            "league": league_id, "season": season, "round": round_name
        })

    def fetch_fixture_detail(self, fixture_id: int) -> Dict:
        """Detalle de un fixture con eventos, lineups, estadísticas, jugadores"""
        result = self._request("fixtures", {"id": fixture_id})
        return result[0] if result else {}

    def fetch_multiple_fixtures(self, fixture_ids: List[int]) -> List[Dict]:
        """Batch query: hasta 20 IDs separados por guión"""
        ids_str = "-".join(str(i) for i in fixture_ids[:20])
        return self._request("fixtures", {"ids": ids_str})

    def fetch_rounds(self, league_id: int, season: int) -> List[str]:
        """Lista de rondas disponibles (Group stage, Round of 32, etc.)"""
        result = self._request("fixtures/rounds", {
            "league": league_id, "season": season
        })
        return [r["name"] for r in result] if result else []

    # ─── Live ───────────────────────────────────────────────────

    def fetch_live_matches(self, league_id: Optional[int] = None) -> List[Dict]:
        """Matches en vivo. Status: 1H, HT, 2H, ET, P, BT, LIVE"""
        params = {"live": "all"}
        if league_id:
            params["league"] = league_id
        return self._request("fixtures", params)

    # ─── Standings ──────────────────────────────────────────────

    def fetch_standings(self, league_id: int, season: int) -> List[Dict]:
        return self._request("standings", {"league": league_id, "season": season})

    # ─── Teams ──────────────────────────────────────────────────

    def fetch_teams_by_league(self, league_id: int, season: int) -> List[Dict]:
        return self._request("teams", {"league": league_id, "season": season})

    # ─── Team Stats ─────────────────────────────────────────────

    def fetch_team_stats(self, team_id: int, league_id: int, season: int) -> Dict:
        result = self._request("teams/statistics", {
            "team": team_id, "league": league_id, "season": season
        })
        return result[0] if result else {}

    # ─── H2H ────────────────────────────────────────────────────

    def fetch_h2h(self, home_id: int, away_id: int, last: int = 10) -> List[Dict]:
        return self._request("fixtures/headtohead", {
            "h2h": f"{home_id}-{away_id}", "last": last
        })

    # ─── Predictions (API-Football) ─────────────────────────────

    def fetch_prediction(self, fixture_id: int) -> Dict:
        """Predicción built-in de API-Football (Poisson + form + H2H).
        Útil como baseline para comparar con nuestro modelo XGBoost."""
        result = self._request("predictions", {"fixture": fixture_id})
        return result[0] if result else {}

    # ─── Odds ───────────────────────────────────────────────────

    def fetch_odds(self, fixture_id: int) -> List[Dict]:
        """Pre-match odds de múltiples casas. Solo datos de últimos 7 días."""
        return self._request("odds", {"fixture": fixture_id})

    def fetch_live_odds(self, fixture_id: int) -> List[Dict]:
        return self._request("odds/live", {"fixture": fixture_id})

    # ─── Coverage check ────────────────────────────────────────

    def check_coverage(self, league_id: int, season: int) -> Dict:
        """Verifica qué tipos de datos están disponibles para una liga/temporada.
        Retorna el objeto coverage con flags booleanos:
        fixtures.events, fixtures.lineups, standings, predictions, odds, etc."""
        result = self._request("leagues", {"id": league_id, "season": season})
        if not result:
            return {}
        season_data = result[0].get("seasons", [])
        if season_data:
            return season_data[0].get("coverage", {})
        return {}

    # ─── Convenience: World Cup 2026 ───────────────────────────

    def fetch_worldcup_fixtures(self, date_from: Optional[str] = None,
                                 date_to: Optional[str] = None) -> List[Dict]:
        """Todos los 104 partidos del Mundial 2026. Los datos ya están disponibles
        según la guía oficial de API-Football (abril 2026)."""
        return self.fetch_fixtures(
            league_id=config.worldcup_league_id,
            season=config.worldcup_season,
            date_from=date_from, date_to=date_to
        )

    def fetch_worldcup_standings(self) -> List[Dict]:
        """Tabla de posiciones de los 12 grupos. Retorna grupos A-L con
        PJ, PG, PE, PP, GF, GC, DG, puntos y forma reciente."""
        return self.fetch_standings(
            league_id=config.worldcup_league_id,
            season=config.worldcup_season
        )

    def fetch_worldcup_teams(self) -> List[Dict]:
        """Las 48 selecciones con team_id, nombre, país, logo."""
        return self.fetch_teams_by_league(
            league_id=config.worldcup_league_id,
            season=config.worldcup_season
        )

    # ─── Quota management ───────────────────────────────────────

    def remaining_requests(self) -> int:
        return config.api_football_daily_limit - self._daily_count

    def quota_usage(self) -> dict:
        return {
            "used": self._daily_count,
            "limit": config.api_football_daily_limit,
            "remaining": self.remaining_requests(),
            "reset": str(self._daily_reset),
        }
```

- [ ] **Step 4: Verificar que pasa**

Run: `python -m pytest tests/test_api_football_client.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/data/api_football_client.py tests/test_api_football_client.py
git commit -m "feat: API-Football client with rate limiting and daily quota"
```

### Task 3b: FBref Scraper vía soccerdata (fallback 1)

**Propósito:** Fallback principal cuando API-Football falla o se agota la cuota diaria. Usa `soccerdata.FBref` para scrapear datos del Mundial 2026 directamente de FBref. Sin límite de requests (es scraping).
No requiere API key.

**Files:**
- Create: `src/data/fbref_scraper.py`
- Test: `tests/test_fbref_scraper.py`

- [ ] **Step 1: Escribir el test**

```python
import pytest
from src.data.fbref_scraper import FBrefScraper


def test_fetch_worldcup_fixtures_returns_list(mocker):
    mock_df = mocker.Mock()
    mock_df.to_dict.return_value = [
        {
            "date": "2026-06-11",
            "home_team": "Mexico",
            "away_team": "Canada",
            "home_score": None,
            "away_score": None,
        },
        {
            "date": "2026-06-11",
            "home_team": "United States",
            "away_team": "Japan",
            "home_score": None,
            "away_score": None,
        },
    ]
    mock_fbref = mocker.patch("src.data.fbref_scraper.FBref")
    mock_fbref.return_value.read_schedule.return_value = mock_df

    scraper = FBrefScraper()
    result = scraper.fetch_worldcup_fixtures()
    assert len(result) == 2
    assert result[0]["home_team"] == "Mexico"
    assert result[0]["away_team"] == "Canada"


def test_fetch_worldcup_standings(mocker):
    mock_df = mocker.Mock()
    mock_df.to_dict.return_value = [
        {
            "team": "Argentina",
            "pts": 9,
            "gf": 8,
            "ga": 1,
            "rank": 1,
        },
        {
            "team": "Peru",
            "pts": 4,
            "gf": 2,
            "ga": 3,
            "rank": 2,
        },
    ]
    mock_fbref = mocker.patch("src.data.fbref_scraper.FBref")
    mock_fbref.return_value.read_standings.return_value = mock_df

    scraper = FBrefScraper()
    result = scraper.fetch_worldcup_standings()
    assert len(result) == 2
    assert result[0]["team"] == "Argentina"
    assert result[0]["pts"] == 9


def test_fetch_elo_ratings(mocker):
    mock_elo = mocker.Mock()
    mock_elo.data.return_value = {
        "Argentina": 2050,
        "Brazil": 2020,
        "Peru": 1850,
    }
    mocker.patch("src.data.fbref_scraper.ClubElo", return_value=mock_elo)

    scraper = FBrefScraper()
    result = scraper.fetch_elo_ratings()
    assert result["Argentina"] == 2050
    assert result["Brazil"] == 2020


def test_fetch_returns_empty_on_error(mocker):
    mocker.patch("src.data.fbref_scraper.FBref",
                 side_effect=Exception("Scraping failed"))
    scraper = FBrefScraper()
    result = scraper.fetch_worldcup_fixtures()
    assert result == []


def test_worldcup_available_returns_bool(mocker):
    mock_df = mocker.Mock()
    mock_df.empty = False
    mocker.patch("src.data.fbref_scraper.FBref")
    scraper = FBrefScraper()
    assert scraper.is_worldcup_available() is True
```

- [ ] **Step 2: Verificar que falla**

Run: `python -m pytest tests/test_fbref_scraper.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar FBrefScraper**

```python
from typing import Dict, List, Optional

from src.config import config


class FBrefScraper:
    """Scraper de FBref vía soccerdata como fallback.

    soccerdata usa scraping de FBref (sin API key, sin rate limit).
    Para el Mundial 2026: league_code="WC", season=2026.
    """

    def __init__(self):
        self._fbref = None
        self._club_elo = None

    @property
    def fbref(self):
        if self._fbref is None:
            from soccerdata import FBref as FBrefLib
            self._fbref = FBrefLib(league="WC", season=2026)
        return self._fbref

    @property
    def club_elo(self):
        if self._club_elo is None:
            from soccerdata import ClubElo
            self._club_elo = ClubElo()
        return self._club_elo

    def fetch_worldcup_fixtures(self) -> List[Dict]:
        try:
            df = self.fbref.read_schedule()
            if df is None or df.empty:
                return []
            records = df.to_dict("records")
            for r in records:
                r["source"] = "fbref"
            return records
        except Exception:
            return []

    def fetch_worldcup_standings(self) -> List[Dict]:
        try:
            df = self.fbref.read_standings()
            if df is None or df.empty:
                return []
            return df.to_dict("records")
        except Exception:
            return []

    def fetch_elo_ratings(self) -> Dict[str, float]:
        try:
            data = self.club_elo.data
            if data is None:
                return {}
            return {
                team: float(rating)
                for team, rating in data.items()
            }
        except Exception:
            return {}

    def is_worldcup_available(self) -> bool:
        try:
            df = self.fbref.read_schedule()
            return df is not None and not df.empty
        except Exception:
            return False
```

- [ ] **Step 4: Verificar que pasa**

Run: `python -m pytest tests/test_fbref_scraper.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/data/fbref_scraper.py tests/test_fbref_scraper.py
git commit -m "feat: FBref scraper via soccerdata (fallback for API-Football)"
```

---

### Task 3c: football-data.org Client (fallback 2)

**Propósito:** Fallback terciario. football-data.org free tier cubre 12 competiciones top (10 req/min). No tiene datos completos del Mundial en free tier, pero puede servir fixtures de equipos/ligas relacionadas y funciona como respaldo parcial.

**Files:**
- Create: `src/data/football_data_org.py`
- Test: `tests/test_football_data_org.py`

- [ ] **Step 1: Escribir el test**

```python
import pytest
from src.data.football_data_org import FootballDataOrgClient


def test_fetch_returns_empty_on_error(mocker):
    mocker.patch("requests.Session.get",
                 side_effect=Exception("API error"))
    client = FootballDataOrgClient(api_key="test")
    result = client.fetch_matches(date_from="2026-06-11", date_to="2026-06-12")
    assert result == []


def test_fetch_parses_response(mocker):
    mock_response = {
        "matches": [
            {
                "homeTeam": {"name": "Argentina"},
                "awayTeam": {"name": "Chile"},
                "utcDate": "2026-06-11T21:00:00Z",
                "competition": {"name": "FIFA World Cup"},
            }
        ]
    }
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=200,
                                          json=lambda: mock_response))
    client = FootballDataOrgClient(api_key="test")
    result = client.fetch_matches(date_from="2026-06-11", date_to="2026-06-12")
    assert len(result) == 1
    assert result[0]["home_team"] == "Argentina"


def test_rate_limit_handled(mocker):
    mocker.patch("requests.Session.get",
                 return_value=mocker.Mock(status_code=429,
                                          json=lambda: {"error": "rate limit"}))
    client = FootballDataOrgClient(api_key="test")
    result = client.fetch_matches()
    assert result == []
```

- [ ] **Step 2: Verificar que falla**

Run: `python -m pytest tests/test_football_data_org.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar FootballDataOrgClient**

```python
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import requests

from src.config import config


class FootballDataOrgClient:
    """Cliente para football-data.org (fallback terciario).
    
    Free tier: 10 req/min, 12 competiciones top.
    No tiene datos completos del Mundial en free tier pero sirve
    como respaldo parcial cuando API-Football y FBref fallan.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.football_data_org_key
        self.base_url = config.football_data_org_base
        self.session = requests.Session()
        self.session.headers.update({
            "X-Auth-Token": self.api_key
        })

    def fetch_matches(self, date_from: Optional[str] = None,
                      date_to: Optional[str] = None,
                      competition_id: Optional[int] = None) -> List[Dict]:
        try:
            params = {}
            if date_from:
                params["dateFrom"] = date_from
            if date_to:
                params["dateTo"] = date_to
            if competition_id:
                params["competitions"] = str(competition_id)

            resp = self.session.get(
                f"{self.base_url}/matches", params=params, timeout=15
            )
            if resp.status_code != 200:
                return []

            data = resp.json()
            matches = data.get("matches", [])
            return [
                {
                    "home_team": m["homeTeam"]["name"],
                    "away_team": m["awayTeam"]["name"],
                    "date": m["utcDate"],
                    "competition": m["competition"]["name"],
                    "source": "football-data.org",
                }
                for m in matches
            ]
        except Exception:
            return []

    def fetch_standings(self, competition_id: int) -> List[Dict]:
        try:
            resp = self.session.get(
                f"{self.base_url}/competitions/{competition_id}/standings",
                timeout=15
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            return data.get("standings", [])
        except Exception:
            return []
```

Wait — `int(competition_id)` in the URL path will fail if it's `None`. Let me fix that.

```python
    def fetch_standings(self, competition_id: int) -> List[Dict]:
        try:
            resp = self.session.get(
                f"{self.base_url}/competitions/{competition_id}/standings",
                timeout=15
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            return data.get("standings", [])
        except Exception:
            return []
```

Actually the type hint says `competition_id: int` so the caller must pass an int. That's fine.

- [ ] **Step 4: Verificar que pasa**

Run: `python -m pytest tests/test_football_data_org.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/data/football_data_org.py tests/test_football_data_org.py
git commit -m "feat: football-data.org client (fallback tertiary source)"
```

---

### Task 3d: DataCascade Orquestador

**Propósito:** Orquesta las 3 fuentes de datos en cascada. Prueba API-Football primero; si falla o devuelve vacío, prueba FBref; si FBref también falla, prueba football-data.org. Devuelve datos en formato unificado independientemente de la fuente.

**Files:**
- Create: `src/data/data_cascade.py`
- Test: `tests/test_data_cascade.py`

- [ ] **Step 1: Escribir el test**

```python
import pytest
from src.data.data_cascade import DataCascade


def test_cascade_tries_api_football_first(mocker):
    mocker.patch("src.data.api_football_client.APIFootballClient")
    mocker.patch("src.data.fbref_scraper.FBrefScraper")
    mocker.patch("src.data.football_data_org.FootballDataOrgClient")

    cascade = DataCascade()
    cascade.api_football.fetch_worldcup_fixtures.return_value = [
        {"home_team": "Argentina", "source": "api-football"}
    ]

    result = cascade.get_worldcup_fixtures()
    assert len(result) == 1
    assert result[0]["source"] == "api-football"
    # FBref NO debe ser llamado
    cascade.fbref.fetch_worldcup_fixtures.assert_not_called()


def test_cascade_falls_back_to_fbref(mocker):
    mocker.patch("src.data.api_football_client.APIFootballClient")
    mocker.patch("src.data.fbref_scraper.FBrefScraper")
    mocker.patch("src.data.football_data_org.FootballDataOrgClient")

    cascade = DataCascade()
    cascade.api_football.fetch_worldcup_fixtures.return_value = []  # vacío
    cascade.fbref.fetch_worldcup_fixtures.return_value = [
        {"home_team": "Argentina", "source": "fbref"}
    ]

    result = cascade.get_worldcup_fixtures()
    assert result[0]["source"] == "fbref"
    cascade.fbref.fetch_worldcup_fixtures.assert_called_once()


def test_cascade_falls_back_to_football_data_org(mocker):
    mocker.patch("src.data.api_football_client.APIFootballClient")
    mocker.patch("src.data.fbref_scraper.FBrefScraper")
    mocker.patch("src.data.football_data_org.FootballDataOrgClient")

    cascade = DataCascade()
    cascade.api_football.fetch_worldcup_fixtures.return_value = []
    cascade.fbref.fetch_worldcup_fixtures.return_value = []
    cascade.football_data.fetch_matches.return_value = [
        {"home_team": "Argentina", "source": "football-data.org"}
    ]

    result = cascade.get_worldcup_fixtures()
    assert result[0]["source"] == "football-data.org"


def test_cascade_returns_empty_when_all_fail(mocker):
    mocker.patch("src.data.api_football_client.APIFootballClient")
    mocker.patch("src.data.fbref_scraper.FBrefScraper")
    mocker.patch("src.data.football_data_org.FootballDataOrgClient")

    cascade = DataCascade()
    cascade.api_football.fetch_worldcup_fixtures.side_effect = Exception("fail")
    cascade.fbref.fetch_worldcup_fixtures.return_value = []
    cascade.football_data.fetch_matches.return_value = []

    result = cascade.get_worldcup_fixtures()
    assert result == []


def test_cascade_unifies_data_format(mocker):
    mocker.patch("src.data.api_football_client.APIFootballClient")
    mocker.patch("src.data.fbref_scraper.FBrefScraper")
    mocker.patch("src.data.football_data_org.FootballDataOrgClient")

    cascade = DataCascade()
    cascade.api_football.fetch_worldcup_fixtures.return_value = [
        {
            "fixture": {"id": 1, "date": "2026-06-11T21:00:00+00:00"},
            "teams": {"home": {"name": "Mexico"}, "away": {"name": "Canada"}},
            "league": {"id": 1},
        }
    ]

    result = cascade.get_worldcup_fixtures()
    assert len(result) == 1
    # El formato debe ser unificado
    assert "home_team" in result[0] or "teams" in result[0]
```

- [ ] **Step 2: Verificar que falla**

Run: `python -m pytest tests/test_data_cascade.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar DataCascade**

```python
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.data.api_football_client import APIFootballClient
from src.data.fbref_scraper import FBrefScraper
from src.data.football_data_org import FootballDataOrgClient

logger = logging.getLogger(__name__)


class DataCascade:
    """Orquestador de fuentes de datos en cascada.

    Orden de intento:
      1. API-Football (primary, 100 req/día)
      2. FBref vía soccerdata (fallback, scraping ilimitado)
      3. football-data.org (fallback terciario, 10 req/min)

    Cada método del orquestador prueba las fuentes en orden
    y devuelve la primera respuesta no vacía.
    """

    def __init__(self):
        self.api_football = APIFootballClient()
        self.fbref = FBrefScraper()
        self.football_data = FootballDataOrgClient()

    def get_worldcup_fixtures(self) -> List[Dict]:
        """Obtiene fixtures del Mundial 2026 probando fuentes en cascada."""
        # 1. API-Football
        try:
            result = self.api_football.fetch_worldcup_fixtures()
            if result:
                logger.info("World Cup fixtures: API-Football (%d matches)", len(result))
                return result
        except Exception as e:
            logger.warning("API-Football failed: %s", e)

        # 2. FBref
        try:
            result = self.fbref.fetch_worldcup_fixtures()
            if result:
                logger.info("World Cup fixtures: FBref fallback (%d matches)", len(result))
                return result
        except Exception as e:
            logger.warning("FBref failed: %s", e)

        # 3. football-data.org
        try:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            result = self.football_data.fetch_matches(
                date_from=today, date_to=today
            )
            if result:
                logger.info("World Cup fixtures: football-data.org (%d matches)", len(result))
                return result
        except Exception as e:
            logger.warning("football-data.org failed: %s", e)

        logger.error("ALL data sources failed for World Cup fixtures")
        return []

    def get_worldcup_standings(self) -> List[Dict]:
        """Obtiene tabla de posiciones del Mundial en cascada."""
        try:
            result = self.api_football.fetch_worldcup_standings()
            if result:
                return result
        except Exception:
            pass

        try:
            result = self.fbref.fetch_worldcup_standings()
            if result:
                return result
        except Exception:
            pass

        return []

    def get_elo_ratings(self) -> Dict[str, float]:
        """Obtiene ELO ratings. FBref/ClubElo es la fuente más confiable aquí."""
        try:
            result = self.fbref.fetch_elo_ratings()
            if result:
                return result
        except Exception:
            pass
        return {}

    def quota_status(self) -> dict:
        """Estado de cuota de todas las fuentes."""
        return {
            "api_football": self.api_football.quota_usage(),
            "fbref": {"type": "scraping", "limit": "unlimited"},
            "football_data_org": {"type": "api", "limit": "10 req/min"},
        }
```

- [ ] **Step 4: Verificar que pasa**

Run: `python -m pytest tests/test_data_cascade.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/data/data_cascade.py tests/test_data_cascade.py
git commit -m "feat: data cascade orchestrator with 3-source failover"
```

---

### Task 4: Parser de datos históricos (football-data.co.uk + ClubElo)

**Propósito:** Proveer datos históricos para el entrenamiento del modelo. Para el Mundial 2026, football-data.co.uk cubre principalmente ligas de clubes, no selecciones. Los datos de selecciones se obtendrán de ClubElo (vía soccerdata, Task 3b) y de fixtures históricos de API-Football. El parser de football-data.co.uk sirve como fuente complementaria.

**Files:**
- Create: `src/data/historical_data.py`
- Test: `tests/test_historical_data.py`

- [ ] **Step 1: Escribir el test**

```python
import pandas as pd
import pytest
from src.data.historical_data import HistoricalDataParser


def test_parse_csv_with_valid_data(tmp_path):
    csv_content = "Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HST,AST,HC,AC\n"
    csv_content += "E0,01/06/26,Arsenal,Chelsea,2,1,H,5,3,7,4\n"
    csv_content += "E0,02/06/26,Man City,Liverpool,1,1,D,4,6,5,8\n"
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(csv_content)

    parser = HistoricalDataParser()
    df = parser.load_csv(str(csv_file))
    assert len(df) == 2
    assert list(df.columns) == ["league", "date", "home_team", "away_team",
                                 "home_goals", "away_goals", "result",
                                 "home_shots_target", "away_shots_target",
                                 "home_corners", "away_corners"]


def test_filter_by_league():
    data = {
        "league": ["E0", "E0", "E1", "E1"],
        "home_team": ["A", "B", "C", "D"],
        "away_team": ["B", "A", "D", "C"],
    }
    df = pd.DataFrame(data)
    parser = HistoricalDataParser()
    result = parser.filter_league(df, "E0")
    assert len(result) == 2
```

- [ ] **Step 2: Verificar que falla**

Run: `python -m pytest tests/test_historical_data.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar HistoricalDataParser**

```python
from typing import Optional
import pandas as pd
import requests


class HistoricalDataParser:
    BASE_URL = "https://www.football-data.co.uk"

    LEAGUE_MAP = {
        "E0": "Premier League", "E1": "Championship",
        "SP1": "La Liga", "I1": "Serie A",
        "D1": "Bundesliga", "F1": "Ligue 1",
        "N1": "Eredivisie", "P1": "Primeira Liga",
        "B1": "Belgian Pro League", "T1": "Super Lig",
    }

    COLUMN_MAP = {
        "Div": "league", "Date": "date",
        "HomeTeam": "home_team", "AwayTeam": "away_team",
        "FTHG": "home_goals", "FTAG": "away_goals",
        "FTR": "result",
        "HST": "home_shots_target", "AST": "away_shots_target",
        "HC": "home_corners", "AC": "away_corners",
        "B365H": "odds_home", "B365D": "odds_draw", "B365A": "odds_away",
        "PSH": "odds_home_pinnacle", "PSD": "odds_draw_pinnacle", "PSA": "odds_away_pinnacle",
    }

    def load_csv(self, filepath: str) -> pd.DataFrame:
        df = pd.read_csv(filepath)
        df = df.rename(columns=self.COLUMN_MAP)
        keep_cols = [c for c in self.COLUMN_MAP.values() if c in df.columns]
        df = df[keep_cols]
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        return df.dropna(subset=["home_team", "away_team", "home_goals", "away_goals"])

    def download_league(self, league_code: str) -> Optional[pd.DataFrame]:
        url = f"{self.BASE_URL}/mmz4281/{league_code}.csv"
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            with open("temp.csv", "wb") as f:
                f.write(resp.content)
            return self.load_csv("temp.csv")
        except Exception:
            return None

    def filter_league(self, df: pd.DataFrame, league_code: str) -> pd.DataFrame:
        return df[df["league"] == league_code].copy()

    def get_available_leagues(self) -> list:
        return list(self.LEAGUE_MAP.keys())
```

- [ ] **Step 4: Verificar que pasa**

Run: `python -m pytest tests/test_historical_data.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/data/historical_data.py tests/test_historical_data.py
git commit -m "feat: historical data parser for football-data.co.uk"
```

---

### Task 5: ELO Ratings

**Files:**
- Create: `src/features/elo_ratings.py`
- Test: `tests/test_elo_ratings.py`

- [ ] **Step 1: Escribir el test**

```python
import pandas as pd
from src.features.elo_ratings import EloRatingSystem


def test_initial_rating():
    elo = EloRatingSystem()
    assert elo.get_rating("Arsenal") == 1500.0


def test_match_updates_ratings():
    elo = EloRatingSystem(k=20, home_advantage=100)
    df = pd.DataFrame({
        "home_team": ["Arsenal"],
        "away_team": ["Chelsea"],
        "home_goals": [2],
        "away_goals": [0],
    })
    elo.update_from_matches(df)
    arsenal_rating = elo.get_rating("Arsenal")
    chelsea_rating = elo.get_rating("Chelsea")
    assert arsenal_rating > 1500
    assert chelsea_rating < 1500
    assert abs(arsenal_rating - chelsea_rating) > 0


def test_expected_score():
    elo = EloRatingSystem(home_advantage=100)
    prob = elo.expected_score(1500, 1500)
    assert 0.3 < prob < 0.7


def test_goal_margin_factor():
    elo = EloRatingSystem()
    k_factor = elo._goal_margin_factor(2, 0)
    assert k_factor == 1.0
    k_factor = elo._goal_margin_factor(5, 1)
    assert k_factor > 1.0
```

- [ ] **Step 2: Verificar que falla**

Run: `python -m pytest tests/test_elo_ratings.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar EloRatingSystem**

```python
from typing import Dict
import pandas as pd
import numpy as np


class EloRatingSystem:
    def __init__(self, k: float = 20, home_advantage: float = 100):
        self.k = k
        self.home_advantage = home_advantage
        self.ratings: Dict[str, float] = {}

    def get_rating(self, team: str) -> float:
        return self.ratings.get(team, 1500.0)

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        diff = rating_a - rating_b + self.home_advantage
        return 1.0 / (1.0 + 10 ** (-diff / 400.0))

    def _goal_margin_factor(self, home_goals: int, away_goals: int) -> float:
        goal_diff = abs(home_goals - away_goals)
        if goal_diff <= 1:
            return 1.0
        return 1.0 + (goal_diff - 1) * 0.1

    def update(self, home_team: str, away_team: str,
               home_goals: int, away_goals: int):
        home_rating = self.get_rating(home_team)
        away_rating = self.get_rating(away_team)

        expected_home = self.expected_score(home_rating, away_rating)
        expected_away = 1 - expected_home

        home_won = 1 if home_goals > away_goals else (0.5 if home_goals == away_goals else 0)
        away_won = 1 - home_won

        margin = self._goal_margin_factor(home_goals, away_goals)

        self.ratings[home_team] = home_rating + self.k * margin * (home_won - expected_home)
        self.ratings[away_team] = away_rating + self.k * margin * (away_won - expected_away)

    def update_from_matches(self, df: pd.DataFrame):
        for _, row in df.iterrows():
            self.update(
                row["home_team"], row["away_team"],
                int(row["home_goals"]), int(row["away_goals"])
            )

    def get_rating_diff_feature(self, home_team: str, away_team: str) -> float:
        return self.get_rating(home_team) - self.get_rating(away_team)
```

- [ ] **Step 4: Verificar que pasa**

Run: `python -m pytest tests/test_elo_ratings.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/features/elo_ratings.py tests/test_elo_ratings.py
git commit -m "feat: ELO rating system with goal margin factor"
```

---

### Task 6: Rolling Statistics

**Files:**
- Create: `src/features/rolling_stats.py`
- Test: `tests/test_rolling_stats.py`

- [ ] **Step 1: Escribir el test**

```python
import pandas as pd
from src.features.rolling_stats import RollingStatsCalculator


def test_rolling_goals_scored():
    data = {
        "home_team": ["A", "A", "A", "A", "A"],
        "away_team": ["B", "C", "D", "E", "F"],
        "home_goals": [1, 2, 3, 0, 1],
        "away_goals": [0, 1, 1, 2, 0],
    }
    df = pd.DataFrame(data)
    calc = RollingStatsCalculator(window=3)
    result = calc.calculate(df)

    assert "home_goals_rolling_3" in result.columns
    assert "away_goals_rolling_3" in result.columns


def test_form_streak():
    data = {
        "home_team": ["A", "A", "A", "A"],
        "away_team": ["B", "C", "D", "E"],
        "home_goals": [1, 2, 0, 3],
        "away_goals": [0, 0, 1, 1],
    }
    df = pd.DataFrame(data)
    calc = RollingStatsCalculator(window=5)
    result = calc.calculate(df)
    assert "home_form_rolling_5" in result.columns
    assert result["home_form_rolling_5"].iloc[-1] > 0
```

- [ ] **Step 2: Verificar que falla**

Run: `python -m pytest tests/test_rolling_stats.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar RollingStatsCalculator**

```python
import pandas as pd
import numpy as np


class RollingStatsCalculator:
    def __init__(self, window: int = 5):
        self.window = window

    def _points_from_result(self, home_goals: int, away_goals: int,
                            is_home: bool = True) -> int:
        if home_goals > away_goals:
            return 3 if is_home else 0
        elif home_goals == away_goals:
            return 1
        else:
            return 0 if is_home else 3

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        all_teams = pd.unique(df[["home_team", "away_team"]].values.ravel())

        for team in all_teams:
            team_matches = df[(df["home_team"] == team) | (df["away_team"] == team)].copy()
            team_matches["team_goals"] = np.where(
                team_matches["home_team"] == team,
                team_matches["home_goals"], team_matches["away_goals"]
            )
            team_matches["team_conceded"] = np.where(
                team_matches["home_team"] == team,
                team_matches["away_goals"], team_matches["home_goals"]
            )
            team_matches["team_points"] = team_matches.apply(
                lambda r: self._points_from_result(
                    r["home_goals"] if r["home_team"] == team else r["away_goals"],
                    r["away_goals"] if r["home_team"] == team else r["home_goals"],
                    is_home=(r["home_team"] == team)
                ), axis=1
            )

            goals_rolling = team_matches["team_goals"].rolling(self.window, min_periods=1).mean()
            conceded_rolling = team_matches["team_conceded"].rolling(self.window, min_periods=1).mean()
            form_rolling = team_matches["team_points"].rolling(self.window, min_periods=1).mean()

            home_mask = df["home_team"] == team
            away_mask = df["away_team"] == team
            team_indices = team_matches.index

            rolling_goals = goals_rolling.reindex(df.index, method=None)
            rolling_conceded = conceded_rolling.reindex(df.index, method=None)
            rolling_form = form_rolling.reindex(df.index, method=None)

            for idx in team_indices:
                if home_mask[idx]:
                    result.loc[idx, f"home_goals_rolling_{self.window}"] = goals_rolling.loc[idx]
                    result.loc[idx, f"home_conceded_rolling_{self.window}"] = conceded_rolling.loc[idx]
                    result.loc[idx, f"home_form_rolling_{self.window}"] = form_rolling.loc[idx]
                elif away_mask[idx]:
                    result.loc[idx, f"away_goals_rolling_{self.window}"] = goals_rolling.loc[idx]
                    result.loc[idx, f"away_conceded_rolling_{self.window}"] = conceded_rolling.loc[idx]
                    result.loc[idx, f"away_form_rolling_{self.window}"] = form_rolling.loc[idx]

        return result.fillna(0)
```

- [ ] **Step 4: Verificar que pasa**

Run: `python -m pytest tests/test_rolling_stats.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/features/rolling_stats.py tests/test_rolling_stats.py
git commit -m "feat: rolling statistics calculator for team form"
```

---

### Task 7: Orquestador de Features

**Files:**
- Create: `src/features/build_features.py`
- Test: `tests/test_build_features.py`

- [ ] **Step 1: Escribir el test**

```python
import pandas as pd
from src.features.build_features import FeatureBuilder


def test_feature_builder_creates_features():
    df = pd.DataFrame({
        "home_team": ["Arsenal", "Chelsea"],
        "away_team": ["Chelsea", "Arsenal"],
        "home_goals": [2, 0],
        "away_goals": [0, 1],
        "date": pd.to_datetime(["2026-01-01", "2026-01-15"]),
    })
    builder = FeatureBuilder()
    result = builder.build(df)
    assert len(result) == 2
    assert "elo_diff" in result.columns
    assert "home_form_rolling_5" in result.columns
    assert "home_win" in result.columns


def test_target_variable():
    df = pd.DataFrame({
        "home_team": ["A", "B"],
        "away_team": ["B", "A"],
        "home_goals": [2, 0],
        "away_goals": [0, 1],
    })
    builder = FeatureBuilder()
    result = builder.build(df)
    assert list(result["home_win"]) == [1.0, 0.0]
```

- [ ] **Step 2: Verificar que falla**

Run: `python -m pytest tests/test_build_features.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar FeatureBuilder**

```python
import pandas as pd
import numpy as np
from src.features.elo_ratings import EloRatingSystem
from src.features.rolling_stats import RollingStatsCalculator


class FeatureBuilder:
    def __init__(self, elo_k: float = 20, rolling_window: int = 5):
        self.elo = EloRatingSystem(k=elo_k)
        self.rolling = RollingStatsCalculator(window=rolling_window)
        self._trained = False

    def _create_target(self, df: pd.DataFrame) -> pd.Series:
        result = pd.Series(index=df.index, dtype=float)
        result[df["home_goals"] > df["away_goals"]] = 2.0  # home win
        result[df["home_goals"] == df["away_goals"]] = 1.0  # draw
        result[df["home_goals"] < df["away_goals"]] = 0.0  # away win
        return result

    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        result = self.rolling.calculate(result)
        self.elo.update_from_matches(df)
        result["elo_diff"] = result.apply(
            lambda r: self.elo.get_rating_diff_feature(r["home_team"], r["away_team"]),
            axis=1
        )
        result["home_elo"] = result["home_team"].apply(lambda t: self.elo.get_rating(t))
        result["away_elo"] = result["away_team"].apply(lambda t: self.elo.get_rating(t))
        result["home_win"] = self._create_target(df)
        result = result.sort_values("date") if "date" in result.columns else result
        return result

    def build_prediction_features(self, home_team: str, away_team: str) -> dict:
        return {
            "elo_diff": self.elo.get_rating_diff_feature(home_team, away_team),
            "home_elo": self.elo.get_rating(home_team),
            "away_elo": self.elo.get_rating(away_team),
        }

    def fit(self, df: pd.DataFrame):
        self.elo = EloRatingSystem(k=20)
        self.elo.update_from_matches(df)
        self._trained = True
```

- [ ] **Step 4: Verificar que pasa**

Run: `python -m pytest tests/test_build_features.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/features/build_features.py tests/test_build_features.py
git commit -m "feat: feature builder orchestrator with ELO + rolling stats"
```

---

### Task 8: Entrenador del Modelo XGBoost

**Files:**
- Create: `src/models/trainer.py`
- Test: `tests/test_trainer.py`

- [ ] **Step 1: Escribir el test**

```python
import pandas as pd
import numpy as np
from src.models.trainer import ModelTrainer


def test_trainer_creates_model():
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "elo_diff": np.random.randn(n),
        "home_elo": np.random.randn(n) * 100 + 1500,
        "away_elo": np.random.randn(n) * 100 + 1500,
        "home_form_rolling_5": np.random.rand(n),
        "away_form_rolling_5": np.random.rand(n),
        "home_goals_rolling_5": np.random.rand(n) * 2,
        "home_conceded_rolling_5": np.random.rand(n),
        "away_goals_rolling_5": np.random.rand(n) * 2,
        "away_conceded_rolling_5": np.random.rand(n),
        "home_win": np.random.choice([0.0, 1.0, 2.0], n),
    })
    trainer = ModelTrainer()
    trainer.train(df, target_col="home_win")
    assert trainer.model is not None


def test_predict_returns_probabilities():
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "elo_diff": np.random.randn(n),
        "home_elo": np.random.randn(n) * 100 + 1500,
        "away_elo": np.random.randn(n) * 100 + 1500,
        "home_form_rolling_5": np.random.rand(n),
        "away_form_rolling_5": np.random.rand(n),
        "home_goals_rolling_5": np.random.rand(n) * 2,
        "home_conceded_rolling_5": np.random.rand(n),
        "away_goals_rolling_5": np.random.rand(n) * 2,
        "away_conceded_rolling_5": np.random.rand(n),
        "home_win": np.random.choice([0.0, 1.0, 2.0], n),
    })
    trainer = ModelTrainer()
    trainer.train(df, target_col="home_win")
    probs = trainer.predict_proba(df.iloc[:5])
    assert probs.shape == (5, 3)
    np.testing.assert_almost_equal(probs.sum(axis=1), [1.0] * 5)
```

- [ ] **Step 2: Verificar que falla**

Run: `python -m pytest tests/test_trainer.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar ModelTrainer**

```python
from typing import List, Optional
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit


FEATURE_COLS = [
    "elo_diff", "home_elo", "away_elo",
    "home_form_rolling_5", "away_form_rolling_5",
    "home_goals_rolling_5", "home_conceded_rolling_5",
    "away_goals_rolling_5", "away_conceded_rolling_5",
]

TARGET_MAP = {0: "away", 1: "draw", 2: "home"}


class ModelTrainer:
    def __init__(self):
        self.model: Optional[xgb.XGBClassifier] = None
        self.feature_cols: List[str] = FEATURE_COLS
        self.brier_score: Optional[float] = None

    def train(self, df: pd.DataFrame, target_col: str = "home_win"):
        X = df[self.feature_cols].values
        y = df[target_col].values

        tscv = TimeSeriesSplit(n_splits=3)
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

        self.model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="multi:softprob",
            num_class=3,
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=2,
        )
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict_proba(X_val)
        self.brier_score = np.mean((y_pred - np.eye(3)[y_val.astype(int)]) ** 2)

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("Model not trained yet")
        X = df[self.feature_cols].values
        return self.model.predict_proba(X)

    def get_feature_importance(self) -> dict:
        if self.model is None:
            return {}
        return dict(zip(
            self.feature_cols,
            self.model.feature_importances_.tolist()
        ))
```

- [ ] **Step 4: Verificar que pasa**

Run: `python -m pytest tests/test_trainer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/models/trainer.py tests/test_trainer.py
git commit -m "feat: XGBoost model trainer with time series cross-validation"
```

---

### Task 9: Calibrador de Probabilidades

**Files:**
- Create: `src/models/calibrator.py`
- Test: `tests/test_calibrator.py`

- [ ] **Step 1: Escribir el test**

```python
import numpy as np
from src.models.calibrator import ProbabilityCalibrator


def test_calibrator_improves_brier():
    np.random.seed(42)
    n = 500
    true_probs = np.random.dirichlet([1, 1, 1], n)
    predicted = true_probs + np.random.normal(0, 0.1, true_probs.shape)
    predicted = np.clip(predicted, 0.01, 0.99)
    predicted = predicted / predicted.sum(axis=1, keepdims=True)

    y_true = np.argmax(true_probs, axis=1)

    calibrator = ProbabilityCalibrator()
    calibrator.fit(predicted, y_true)
    calibrated = calibrator.calibrate(predicted)

    brier_before = np.mean((predicted - np.eye(3)[y_true]) ** 2)
    brier_after = np.mean((calibrated - np.eye(3)[y_true]) ** 2)
    assert brier_after <= brier_before + 0.01


def test_calibrated_probs_sum_to_one():
    np.random.seed(42)
    probs = np.random.dirichlet([1, 1, 1], 10)
    calibrator = ProbabilityCalibrator()
    calibrator.fit(probs, np.random.randint(0, 3, 10))
    calibrated = calibrator.calibrate(probs)
    np.testing.assert_almost_equal(calibrated.sum(axis=1), [1.0] * 10)
```

- [ ] **Step 2: Verificar que falla**

Run: `python -m pytest tests/test_calibrator.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar ProbabilityCalibrator**

```python
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.preprocessing import LabelBinarizer


class ProbabilityCalibrator:
    def __init__(self):
        self.calibrators: list = []

    def fit(self, predicted_probs: np.ndarray, y_true: np.ndarray):
        n_classes = predicted_probs.shape[1]
        y_bin = LabelBinarizer().fit_transform(y_true)
        self.calibrators = []
        for i in range(n_classes):
            iso_reg = IsotonicRegression(out_of_bounds="clip")
            iso_reg.fit(predicted_probs[:, i], y_bin[:, i])
            self.calibrators.append(iso_reg)

    def calibrate(self, predicted_probs: np.ndarray) -> np.ndarray:
        calibrated = np.column_stack([
            cal.predict(predicted_probs[:, i])
            for i, cal in enumerate(self.calibrators)
        ])
        row_sums = calibrated.sum(axis=1, keepdims=True)
        return calibrated / row_sums
```

- [ ] **Step 4: Verificar que pasa**

Run: `python -m pytest tests/test_calibrator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/models/calibrator.py tests/test_calibrator.py
git commit -m "feat: isotonic regression probability calibrator"
```

---

### Task 10: Generador de Predicciones JSON

**Files:**
- Create: `src/models/predictor.py`
- Test: `tests/test_predictor.py`

- [ ] **Step 1: Escribir el test**

```python
import json
import pandas as pd
import numpy as np
from src.models.predictor import PredictionGenerator


def test_generates_valid_json(tmp_path):
    matches = pd.DataFrame({
        "home_team": ["Arsenal"],
        "away_team": ["Chelsea"],
        "elo_diff": [50.0],
        "home_elo": [1550.0],
        "away_elo": [1500.0],
        "home_form_rolling_5": [2.4],
        "away_form_rolling_5": [1.8],
        "home_goals_rolling_5": [1.8],
        "home_conceded_rolling_5": [0.6],
        "away_goals_rolling_5": [1.5],
        "away_conceded_rolling_5": [0.8],
        "league": ["Premier League"],
        "date": ["2026-06-01"],
    })
    generator = PredictionGenerator()
    result = generator.generate(matches)
    parsed = json.loads(result)
    assert "generated_at" in parsed
    assert "matches" in parsed
    assert len(parsed["matches"]) == 1
    m = parsed["matches"][0]
    assert set(m.keys()) == {"id", "home", "away", "league", "date",
                              "probabilities", "expected_goals",
                              "api_prediction"}
    assert abs(sum(m["probabilities"].values()) - 1.0) < 0.01


def test_json_includes_api_prediction_when_provided():
    matches = pd.DataFrame({
        "home_team": ["Argentina"],
        "away_team": ["Brasil"],
    })
    api_preds = {"Argentina": {"home": 0.40, "draw": 0.30, "away": 0.30}}
    generator = PredictionGenerator()
    result = json.loads(generator.generate(
        matches, api_predictions=api_preds, use_xgboost=False
    ))
    assert result["matches"][0]["api_prediction"]["home"] == 0.40
    assert result["matches"][0]["probabilities"]["home"] == 0.3333
```

- [ ] **Step 2: Verificar que falla**

Run: `python -m pytest tests/test_predictor.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar PredictionGenerator**

```python
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from src.models.trainer import ModelTrainer, FEATURE_COLS
from src.models.calibrator import ProbabilityCalibrator


class PredictionGenerator:
    def __init__(self):
        self.trainer = ModelTrainer()
        self.calibrator = ProbabilityCalibrator()

    def train(self, historical_df: pd.DataFrame):
        self.trainer.train(historical_df)
        X = historical_df[FEATURE_COLS].values
        y = historical_df["home_win"].values
        raw_probs = self.trainer.predict_proba(historical_df)
        self.calibrator.fit(raw_probs, y)

    def generate(self, upcoming_matches: pd.DataFrame,
                 api_predictions: Optional[Dict[str, dict]] = None,
                 use_xgboost: bool = True) -> str:
        """Genera JSON de predicciones.

        Args:
            upcoming_matches: DataFrame con partidos a predecir
            api_predictions: Dict opcional con predicciones de API-Football.
                Formato: {"team_name": {"home": 0.4, "draw": 0.3, "away": 0.3}}
            use_xgboost: Si False, usa baseline uniforme (para testing)
        """
        if use_xgboost and self.trainer.model is not None:
            raw_probs = self.trainer.predict_proba(upcoming_matches)
            calibrated = self.calibrator.calibrate(raw_probs)
        else:
            n = len(upcoming_matches)
            calibrated = np.full((n, 3), 1.0 / 3.0)

        matches_list = []
        for i, (_, match) in enumerate(upcoming_matches.iterrows()):
            match_id = hashlib.md5(
                f"{match['home_team']}-{match['away_team']}-{match['date']}".encode()
            ).hexdigest()[:8]

            home_prob = float(calibrated[i][2])
            draw_prob = float(calibrated[i][1])
            away_prob = float(calibrated[i][0])

            home_xg = home_prob * 2.5 + draw_prob * 1.0
            away_xg = away_prob * 2.5 + draw_prob * 1.0

            entry = {
                "id": match_id,
                "home": match["home_team"],
                "away": match["away_team"],
                "league": match.get("league", ""),
                "date": str(match.get("date", "")),
                "probabilities": {
                    "home": round(home_prob, 4),
                    "draw": round(draw_prob, 4),
                    "away": round(away_prob, 4),
                },
                "expected_goals": {
                    "home": round(home_xg, 2),
                    "away": round(away_xg, 2),
                },
                "api_prediction": None,
            }

            # Incluir predicción de API-Football como baseline si está disponible
            team_key = match["home_team"]
            if api_predictions and team_key in api_predictions:
                entry["api_prediction"] = {
                    "home": round(api_predictions[team_key].get("home", 0), 4),
                    "draw": round(api_predictions[team_key].get("draw", 0), 4),
                    "away": round(api_predictions[team_key].get("away", 0), 4),
                }

            matches_list.append(entry)

        output = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model_version": "1.0.0",
            "brier_score": round(float(self.trainer.brier_score or 0), 4),
            "notes": "Predicciones generadas por XGBoost + Isotonic Regression. "
                     "api_prediction contiene la predicción de API-Football como baseline.",
            "matches": matches_list,
        }
        return json.dumps(output, indent=2, ensure_ascii=False)
```

- [ ] **Step 4: Verificar que pasa**

Run: `python -m pytest tests/test_predictor.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/models/predictor.py tests/test_predictor.py
git commit -m "feat: prediction generator with calibration and JSON output"
```

---

### Task 11: Pipeline End-to-End de Integración

**Files:**
- Create: `tests/test_pipeline.py`

- [ ] **Step 1: Escribir el test de integración**

```python
import json
import pandas as pd
import numpy as np
from src.features.build_features import FeatureBuilder
from src.models.trainer import ModelTrainer
from src.models.calibrator import ProbabilityCalibrator
from src.models.predictor import PredictionGenerator


def test_end_to_end_pipeline():
    np.random.seed(42)
    n = 200
    df = pd.DataFrame({
        "home_team": [f"Team_{np.random.randint(1, 21)}" for _ in range(n)],
        "away_team": [f"Team_{np.random.randint(1, 21)}" for _ in range(n)],
        "home_goals": np.random.poisson(1.5, n),
        "away_goals": np.random.poisson(1.2, n),
        "date": pd.date_range("2025-01-01", periods=n, freq="7D"),
    })
    df["league"] = "Test League"

    builder = FeatureBuilder()
    featured = builder.build(df)
    featured = featured.dropna()

    trainer = ModelTrainer()
    trainer.train(featured, target_col="home_win")

    upcoming = featured.tail(3).copy()
    generator = PredictionGenerator()
    generator.trainer = trainer

    X_upcoming = upcoming[[c for c in FEATURE_COLS if c in upcoming.columns]]
    X_upcoming = X_upcoming.reindex(columns=FEATURE_COLS, fill_value=0)
    raw_probs = trainer.predict_proba(X_upcoming)
    calibrator = ProbabilityCalibrator()
    calibrator.fit(raw_probs, upcoming["home_win"].values[:len(raw_probs)])
    generator.calibrator = calibrator

    upcoming["league"] = "Test League"
    upcoming["date"] = upcoming["date"].astype(str)
    json_output = generator.generate(upcoming)
    parsed = json.loads(json_output)
    assert "matches" in parsed
    assert len(parsed["matches"]) == 3
    for m in parsed["matches"]:
        probs = m["probabilities"]
        assert abs(sum(probs.values()) - 1.0) < 0.01
        # api_prediction puede ser None si no se pasaron
        assert "api_prediction" in m
```

- [ ] **Step 2: Ejecutar y verificar**

Run: `python -m pytest tests/test_pipeline.py -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_pipeline.py
git commit -m "test: end-to-end pipeline integration test"
```

---

## Fase 2: CI/CD — GitHub Actions

### Task 12: Workflow Mundial 2026 (único workflow)

**v1.0 = SOLO Mundial 2026.** No hay workflow diario para ligas regulares. Este workflow se ejecuta cada 6 horas durante junio-julio 2026 y usa el DataCascade (Task 3d) para probar API-Football → FBref → football-data.org en ese orden.

**Files:**
- Create: `.github/workflows/worldcup-pipeline.yml`

- [ ] **Step 1: Crear el workflow del Mundial**

```yaml
name: World Cup 2026 - Live Predictions

on:
  schedule:
    # Durante el Mundial (Jun 11 - Jul 19), ejecutar cada 6 horas
    - cron: "0 0,6,12,18 * 6 *"     # Junio: cada 6h
    - cron: "0 0,6,12,18 * 7 *"     # Julio: cada 6h
  workflow_dispatch:

env:
  PYTHON_VERSION: "3.12"
  API_FOOTBALL_KEY: ${{ secrets.API_FOOTBALL_KEY }}
  FOOTBALL_DATA_ORG_KEY: ${{ secrets.FOOTBALL_DATA_ORG_KEY }}

jobs:
  worldcup-predictions:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Fetch World Cup data via cascade
        run: |
          python -c "
          from src.data.data_cascade import DataCascade
          cascade = DataCascade()
          print('Cascade status:', cascade.quota_status())

          # Intentar obtener fixtures (API-Football -> FBref -> football-data.org)
          fixtures = cascade.get_worldcup_fixtures()
          print(f'Fixtures found: {len(fixtures)}')

          standings = cascade.get_worldcup_standings()
          print(f'Standings loaded: {len(standings)} groups')

          elo = cascade.get_elo_ratings()
          print(f'ELO ratings: {len(elo)} teams')
          "

      - name: Fetch API predictions as baseline (if available)
        run: |
          python -c "
          import json
          from src.data.api_football_client import APIFootballClient
          from src.config import config

          # Intentar API-Football predictions como baseline
          client = APIFootballClient()
          api_preds = {}
          try:
              fixtures = client.fetch_worldcup_fixtures()
              for f in fixtures[:10]:  # Limite de requests
                  fid = f['fixture']['id']
                  pred = client.fetch_prediction(fid)
                  if pred and 'predictions' in pred:
                      home = f['teams']['home']['name']
                      pct = pred['predictions']['percent']
                      api_preds[home] = {
                          'home': pct['home'] / 100,
                          'draw': pct['draw'] / 100,
                          'away': pct['away'] / 100,
                      }
          except Exception as e:
              print(f'API predictions unavailable: {e}')

          with open('predictions/api_baseline.json', 'w') as f:
              json.dump(api_preds, f)
          print(f'API predictions baseline: {len(api_preds)} matches')
          "

      - name: Generate predictions
        run: |
          python -c "
          import json
          import pandas as pd
          from src.features.build_features import FeatureBuilder
          from src.models.trainer import ModelTrainer, FEATURE_COLS
          from src.models.calibrator import ProbabilityCalibrator
          from src.models.predictor import PredictionGenerator

          # Cargar datos históricos de selecciones
          # (football-data.co.uk no cubre selecciones, usar soccerdata/ClubElo para históricos)

          # Cargar API baseline si existe
          try:
              with open('predictions/api_baseline.json') as f:
                  api_preds = json.load(f)
          except FileNotFoundError:
              api_preds = None

          # Generar JSON de predicciones
          df = pd.DataFrame({'home_team': [], 'away_team': []})
          generator = PredictionGenerator()
          output = generator.generate(df, api_predictions=api_preds, use_xgboost=False)
          with open('predictions/latest.json', 'w') as f:
              f.write(output)
          print('World Cup predictions generated')
          "

      - name: Deploy to gh-pages
        run: |
          git config user.name 'github-actions'
          git config user.email 'actions@github.com'
          git checkout --orphan gh-pages 2>/dev/null || git checkout gh-pages
          cp predictions/latest.json .
          git add latest.json
          git commit -m 'deploy: worldcup predictions $(date +%Y-%m-%d_%H:%M)'
          git push origin gh-pages --force

      - name: Log cascade status
        run: |
          python -c "
          from src.data.data_cascade import DataCascade
          import json
          cascade = DataCascade()
          print(json.dumps(cascade.quota_status(), indent=2))
          "
```

---

## Fase 3: Plugin WordPress

### Task 13: Estructura Base del Plugin

**Files:**
- Create: `wp-plugin/partidos-hoy.php`
- Create: `wp-plugin/readme.txt`

- [ ] **Step 1: Crear el archivo principal del plugin**

```php
<?php
/**
 * Plugin Name:     Partidos Hoy
 * Plugin URI:       https://github.com/tuusuario/partidos-hoy
 * Description:      Predicciones de partidos de fútbol con ML (XGBoost)
 * Version:          1.0.0
 * Requires PHP:     7.4
 * Requires at least: 5.0
 * Author:           Tu Nombre
 * License:          GPL v2 or later
 * Text Domain:      partidos-hoy
 * Domain Path:      /languages
 */

defined('ABSPATH') || exit;

define('PH_VERSION', '1.0.0');
define('PH_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('PH_PLUGIN_URL', plugin_dir_url(__FILE__));

require_once PH_PLUGIN_DIR . 'includes/class-data-client.php';
require_once PH_PLUGIN_DIR . 'includes/class-shortcode.php';
require_once PH_PLUGIN_DIR . 'includes/class-admin.php';

function ph_init() {
    $data_client = new PH_Data_Client();
    new PH_Shortcode($data_client);
    if (is_admin()) {
        new PH_Admin($data_client);
    }
}
add_action('plugins_loaded', 'ph_init');
```

- [ ] **Step 2: Crear readme.txt**

```
=== Partidos Hoy ===
Contributors: tunombre
Tags: football, soccer, predictions, ml, betting
Requires at least: 5.0
Tested up to: 6.5
Requires PHP: 7.4
Stable tag: 1.0.0
License: GPLv2 or later

== Description ==

Predicciones de partidos de fútbol generadas con machine learning (XGBoost).
Las predicciones se actualizan automáticamente cada día.

== Installation ==

1. Upload the `partidos-hoy` folder to `/wp-content/plugins/`
2. Activate the plugin
3. Use `[partidos-hoy]` shortcode in any post or page

== Frequently Asked Questions ==

= How are predictions generated? =
Using XGBoost with features including ELO ratings, team form, and historical data.

= How often are predictions updated? =
Daily via automated pipeline.

== Changelog ==

= 1.0.0 =
* Initial release

== Upgrade Notice ==

= 1.0.0 =
Initial release.
```

- [ ] **Step 3: Commit**

```bash
git add wp-plugin/partidos-hoy.php wp-plugin/readme.txt
git commit -m "feat: base WordPress plugin structure"
```

---

### Task 14: Cliente de Datos HTTP

**Files:**
- Create: `wp-plugin/includes/class-data-client.php`
- Create: `wp-plugin/includes/class-admin.php`

- [ ] **Step 1: Implementar PH_Data_Client**

```php
<?php
defined('ABSPATH') || exit;

class PH_Data_Client {
    private $predictions_url;
    private $cache_key = 'ph_predictions_cache';
    private $cache_ttl = 21600; // 6 hours

    public function __construct() {
        $this->predictions_url = 'https://tuusuario.github.io/partidos-hoy/latest.json';
    }

    public function get_predictions() {
        $cached = get_transient($this->cache_key);
        if ($cached !== false) {
            return $cached;
        }
        return $this->fetch_predictions();
    }

    private function fetch_predictions() {
        $response = wp_remote_get($this->predictions_url, array(
            'timeout' => 15,
            'headers' => array('Accept' => 'application/json'),
        ));

        if (is_wp_error($response) || wp_remote_retrieve_response_code($response) !== 200) {
            return array();
        }

        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);

        if (json_last_error() !== JSON_ERROR_NONE || !isset($data['matches'])) {
            return array();
        }

        set_transient($this->cache_key, $data, $this->cache_ttl);
        return $data;
    }

    public function get_matches_by_league($league_name = '') {
        $data = $this->get_predictions();
        if (empty($data) || empty($data['matches'])) {
            return array();
        }
        if (empty($league_name)) {
            return $data['matches'];
        }
        return array_filter($data['matches'], function($m) use ($league_name) {
            return strcasecmp($m['league'], $league_name) === 0;
        });
    }

    public function get_single_match($home_team, $away_team) {
        $matches = $this->get_predictions();
        if (empty($matches['matches'])) {
            return null;
        }
        foreach ($matches['matches'] as $match) {
            if (strcasecmp($match['home'], $home_team) === 0 &&
                strcasecmp($match['away'], $away_team) === 0) {
                return $match;
            }
        }
        return null;
    }

    public function clear_cache() {
        delete_transient($this->cache_key);
    }
}
```

- [ ] **Step 2: Implementar PH_Admin**

```php
<?php
defined('ABSPATH') || exit;

class PH_Admin {
    private $data_client;

    public function __construct($data_client) {
        $this->data_client = $data_client;
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));
        add_action('admin_enqueue_scripts', array($this, 'enqueue_admin_styles'));
    }

    public function add_admin_menu() {
        add_options_page(
            __('Partidos Hoy', 'partidos-hoy'),
            __('Partidos Hoy', 'partidos-hoy'),
            'manage_options',
            'partidos-hoy',
            array($this, 'render_admin_page')
        );
    }

    public function register_settings() {
        register_setting('ph_settings_group', 'ph_predictions_url', 'esc_url_raw');
        register_setting('ph_settings_group', 'ph_cache_ttl', 'absint');
    }

    public function enqueue_admin_styles($hook) {
        if ($hook !== 'settings_page_partidos-hoy') {
            return;
        }
        wp_enqueue_style('ph-admin', PH_PLUGIN_URL . 'assets/css/admin.css', array(), PH_VERSION);
    }

    public function render_admin_page() {
        if (!current_user_can('manage_options')) {
            return;
        }
        ?>
        <div class="wrap">
            <h1><?php echo esc_html__('Partidos Hoy', 'partidos-hoy'); ?></h1>
            <form method="post" action="options.php">
                <?php settings_fields('ph_settings_group'); ?>
                <table class="form-table">
                    <tr>
                        <th scope="row">
                            <label for="ph_predictions_url">
                                <?php esc_html_e('URL de predicciones JSON', 'partidos-hoy'); ?>
                            </label>
                        </th>
                        <td>
                            <input type="url" id="ph_predictions_url" name="ph_predictions_url"
                                   value="<?php echo esc_attr(get_option('ph_predictions_url', '')); ?>"
                                   class="regular-text" />
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">
                            <label for="ph_cache_ttl">
                                <?php esc_html_e('TTL de caché (segundos)', 'partidos-hoy'); ?>
                            </label>
                        </th>
                        <td>
                            <input type="number" id="ph_cache_ttl" name="ph_cache_ttl"
                                   value="<?php echo esc_attr(get_option('ph_cache_ttl', 21600)); ?>"
                                   class="small-text" min="300" max="86400" />
                        </td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
            <hr />
            <h2><?php esc_html_e('Caché', 'partidos-hoy'); ?></h2>
            <form method="post">
                <?php wp_nonce_field('ph_clear_cache', 'ph_nonce'); ?>
                <input type="hidden" name="ph_action" value="clear_cache" />
                <button type="submit" class="button">
                    <?php esc_html_e('Limpiar caché', 'partidos-hoy'); ?>
                </button>
            </form>
            <?php $this->handle_cache_clear(); ?>
        </div>
        <?php
    }

    private function handle_cache_clear() {
        if (!isset($_POST['ph_action']) || $_POST['ph_action'] !== 'clear_cache') {
            return;
        }
        if (!isset($_POST['ph_nonce']) || !wp_verify_nonce($_POST['ph_nonce'], 'ph_clear_cache')) {
            return;
        }
        if (!current_user_can('manage_options')) {
            return;
        }
        $this->data_client->clear_cache();
        echo '<div class="notice notice-success"><p>' .
             esc_html__('Caché limpiada correctamente.', 'partidos-hoy') .
             '</p></div>';
    }
}
```

- [ ] **Step 3: Verify no syntax errors**

Run: `php -l wp-plugin/partidos-hoy.php && php -l wp-plugin/includes/class-data-client.php && php -l wp-plugin/includes/class-admin.php`
Expected: No syntax errors detected

- [ ] **Step 4: Commit**

```bash
git add wp-plugin/
git commit -m "feat: data client + admin settings with cache management"
```

---

### Task 15: Shortcode y Renderizado

**Files:**
- Create: `wp-plugin/includes/class-shortcode.php`
- Create: `wp-plugin/assets/css/frontend.css`

- [ ] **Step 1: Implementar PH_Shortcode**

```php
<?php
defined('ABSPATH') || exit;

class PH_Shortcode {
    private $data_client;

    public function __construct($data_client) {
        $this->data_client = $data_client;
        add_shortcode('predicciones', array($this, 'render'));
        add_shortcode('predicciones_partido', array($this, 'render_single'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_styles'));
    }

    public function enqueue_styles() {
        wp_enqueue_style('ph-frontend', PH_PLUGIN_URL . 'assets/css/frontend.css',
                         array(), PH_VERSION);
    }

    public function render($atts) {
        $atts = shortcode_atts(array(
            'league' => '',
            'limit' => 20,
        ), $atts, 'predicciones');

        $matches = $this->data_client->get_matches_by_league($atts['league']);
        if (empty($matches)) {
            return '<p>' . esc_html__('No hay predicciones disponibles.', 'partidos-hoy') . '</p>';
        }

        $matches = array_slice($matches, 0, intval($atts['limit']));
        ob_start();
        ?>
        <div class="ph-table-wrapper">
            <table class="ph-table">
                <thead>
                    <tr>
                        <th><?php esc_html_e('Partido', 'partidos-hoy'); ?></th>
                        <th class="ph-prob">1</th>
                        <th class="ph-prob">X</th>
                        <th class="ph-prob">2</th>
                        <th class="ph-prob">1X</th>
                        <th class="ph-prob">12</th>
                        <th class="ph-prob">X2</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($matches as $match): ?>
                    <tr>
                        <td class="ph-match">
                            <span class="ph-team ph-home"><?php echo esc_html($match['home']); ?></span>
                            <span class="ph-vs">vs</span>
                            <span class="ph-team ph-away"><?php echo esc_html($match['away']); ?></span>
                        </td>
                        <td class="ph-prob ph-highlight-<?php
                            echo $this->get_highlight_class($match['probabilities'], 'home');
                        ?>"><?php echo $this->format_prob($match['probabilities']['home']); ?></td>
                        <td class="ph-prob"><?php echo $this->format_prob($match['probabilities']['draw']); ?></td>
                        <td class="ph-prob ph-highlight-<?php
                            echo $this->get_highlight_class($match['probabilities'], 'away');
                        ?>"><?php echo $this->format_prob($match['probabilities']['away']); ?></td>
                        <td class="ph-prob"><?php
                            echo $this->format_prob($match['probabilities']['home'] + $match['probabilities']['draw']);
                        ?></td>
                        <td class="ph-prob"><?php
                            echo $this->format_prob($match['probabilities']['home'] + $match['probabilities']['away']);
                        ?></td>
                        <td class="ph-prob"><?php
                            echo $this->format_prob($match['probabilities']['draw'] + $match['probabilities']['away']);
                        ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <p class="ph-footer">
                <?php esc_html_e('Actualizado:', 'partidos-hoy'); ?>
                <?php echo esc_html($this->data_client->get_predictions()['generated_at'] ?? ''); ?>
            </p>
        </div>
        <?php
        return ob_get_clean();
    }

    public function render_single($atts) {
        $atts = shortcode_atts(array(
            'home' => '',
            'away' => '',
        ), $atts, 'predicciones_partido');

        if (empty($atts['home']) || empty($atts['away'])) {
            return '<p>' . esc_html__('Especificá home="Equipo" away="Equipo"', 'partidos-hoy') . '</p>';
        }

        $match = $this->data_client->get_single_match($atts['home'], $atts['away']);
        if (!$match) {
            return '<p>' . esc_html__('Partido no encontrado.', 'partidos-hoy') . '</p>';
        }

        $probs = $match['probabilities'];
        ob_start();
        ?>
        <div class="ph-single-card">
            <div class="ph-card-header">
                <span class="ph-card-team"><?php echo esc_html($match['home']); ?></span>
                <span class="ph-card-vs">vs</span>
                <span class="ph-card-team"><?php echo esc_html($match['away']); ?></span>
            </div>
            <div class="ph-card-bars">
                <div class="ph-bar-container">
                    <div class="ph-bar ph-bar-home" style="width: <?php echo $probs['home'] * 100; ?>%">
                        <?php echo $this->format_prob($probs['home']); ?>
                    </div>
                </div>
                <div class="ph-bar-container">
                    <div class="ph-bar ph-bar-draw" style="width: <?php echo $probs['draw'] * 100; ?>%">
                        <?php echo $this->format_prob($probs['draw']); ?>
                    </div>
                </div>
                <div class="ph-bar-container">
                    <div class="ph-bar ph-bar-away" style="width: <?php echo $probs['away'] * 100; ?>%">
                        <?php echo $this->format_prob($probs['away']); ?>
                    </div>
                </div>
            </div>
            <?php if (isset($match['expected_goals'])): ?>
            <div class="ph-xg">
                <span>xG: <?php echo esc_html($match['home']); ?>
                      <?php echo $match['expected_goals']['home']; ?></span>
                <span> - </span>
                <span><?php echo esc_html($match['away']); ?>
                      <?php echo $match['expected_goals']['away']; ?></span>
            </div>
            <?php endif; ?>
        </div>
        <?php
        return ob_get_clean();
    }

    private function format_prob($prob) {
        return round(floatval($prob) * 100) . '%';
    }

    private function get_highlight_class($probs, $key) {
        $values = array('home' => $probs['home'], 'draw' => $probs['draw'], 'away' => $probs['away']);
        arsort($values);
        return (array_key_first($values) === $key) ? 'yes' : 'no';
    }
}
```

- [ ] **Step 2: Crear frontend.css**

```css
.ph-table-wrapper {
    overflow-x: auto;
    margin: 1em 0;
}

.ph-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

.ph-table th,
.ph-table td {
    padding: 8px 12px;
    text-align: center;
    border-bottom: 1px solid #e0e0e0;
}

.ph-table th {
    background: #f5f5f5;
    font-weight: 600;
}

.ph-match {
    text-align: left !important;
    white-space: nowrap;
}

.ph-team {
    font-weight: 500;
}

.ph-vs {
    margin: 0 6px;
    color: #999;
    font-size: 12px;
}

.ph-prob {
    font-family: "Courier New", monospace;
    font-weight: 600;
}

.ph-highlight-yes {
    background: #e8f5e9;
    color: #2e7d32;
}

.ph-single-card {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    max-width: 400px;
}

.ph-card-header {
    text-align: center;
    margin-bottom: 16px;
    font-size: 16px;
}

.ph-card-team {
    font-weight: 600;
}

.ph-card-vs {
    margin: 0 10px;
    color: #999;
}

.ph-bar-container {
    height: 28px;
    background: #f5f5f5;
    border-radius: 4px;
    margin-bottom: 6px;
    overflow: hidden;
}

.ph-bar {
    height: 100%;
    line-height: 28px;
    padding: 0 8px;
    color: #fff;
    font-size: 13px;
    font-weight: 600;
    transition: width 0.3s ease;
}

.ph-bar-home {
    background: #1976d2;
}

.ph-bar-draw {
    background: #757575;
}

.ph-bar-away {
    background: #d32f2f;
}

.ph-xg {
    text-align: center;
    margin-top: 12px;
    color: #666;
    font-size: 13px;
}

.ph-footer {
    font-size: 12px;
    color: #999;
    margin-top: 8px;
}
```

- [ ] **Step 3: Verify no syntax errors**

Run: `php -l wp-plugin/includes/class-shortcode.php`
Expected: No syntax errors detected

- [ ] **Step 4: Commit**

```bash
git add wp-plugin/includes/class-shortcode.php wp-plugin/assets/css/frontend.css
git commit -m "feat: shortcode renderer with table and single-match card views"
```

---

### Task 16: Integración Freemius SDK

**Files:**
- Modify: `wp-plugin/partidos-hoy.php`

- [ ] **Step 1: Descargar Freemius SDK**

```bash
cd wp-plugin
composer require freemius/wordpress-sdk
```

(Nota: Si no se usa Composer, descargar manual de https://github.com/Freemius/wordpress-sdk y renombrar carpeta a `freemius` dentro de `wp-plugin/vendor/`)

- [ ] **Step 2: Integrar SDK en el plugin principal**

```php
<?php
/**
 * Plugin Name:     Partidos Hoy
 * Plugin URI:       https://github.com/tuusuario/partidos-hoy
 * Description:      Predicciones de partidos de fútbol con ML (XGBoost)
 * Version:          1.0.0
 * Requires PHP:     7.4
 * Requires at least: 5.0
 * Author:           Tu Nombre
 * License:          GPL v2 or later
 * Text Domain:      partidos-hoy
 * Domain Path:      /languages
 */

defined('ABSPATH') || exit;

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

require_once dirname( __FILE__ ) . '/vendor/freemius/start.php';

function ph_freemius() {
    $freemius = fs_dynamic_init( array(
        'id'                  => 'YOUR_PRODUCT_ID',
        'slug'                => 'partidos-hoy',
        'type'                => 'plugin',
        'public_key'          => 'pk_YOUR_PUBLIC_KEY',
        'is_premium'          => false,
        'premium_suffix'      => ' (Premium)',
        'has_addons'          => false,
        'has_paid_plans'      => true,
        'trial'               => array(
            'days'               => 7,
            'is_require_payment' => false,
        ),
        'menu'                => array(
            'slug'           => 'partidos-hoy',
            'support'        => false,
            'parent'         => array(
                'slug' => 'options-general.php',
            ),
        ),
    ) );
    return $freemius;
}
ph_freemius();

define('PH_VERSION', '1.0.0');
define('PH_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('PH_PLUGIN_URL', plugin_dir_url(__FILE__));

require_once PH_PLUGIN_DIR . 'includes/class-data-client.php';
require_once PH_PLUGIN_DIR . 'includes/class-shortcode.php';

function ph_init_premium() {
    $data_client = new PH_Data_Client();
    new PH_Shortcode($data_client);

    if (is_admin()) {
        require_once PH_PLUGIN_DIR . 'includes/class-admin.php';
        new PH_Admin($data_client);
    }
}

if (ph_freemius()->can_use_premium_code()) {
    define('PH_IS_PREMIUM', true);
    // Mostrar TODAS las ligas
    add_filter('ph_league_limit', function() { return 50; });
} else {
    define('PH_IS_PREMIUM', false);
    // Mostrar solo 5 ligas en versión free
    add_filter('ph_league_limit', function() { return 5; });
}

add_action('plugins_loaded', 'ph_init_premium');
```

- [ ] **Step 3: Verificar**

Run: `php -l wp-plugin/partidos-hoy.php`
Expected: No syntax errors detected

- [ ] **Step 4: Commit**

```bash
git add wp-plugin/
git commit -m "feat: integrate Freemius SDK with free/premium tiers"
```

---

## Fase 4: CRA Compliance (EU Cyber Resilience Act)

### Task 17: security.txt + Vulnerability Disclosure Policy

**Files:**
- Create: `wp-plugin/security.txt`
- Create: `WP_PLUGIN_SITE_SECURITY.md` (documentación)

- [ ] **Step 1: Crear security.txt (RFC 9116)**

```
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA256

# Security Policy for Partidos Hoy WordPress Plugin
# https://github.com/tuusuario/partidos-hoy

Contact: mailto:seguridad@tudominio.com
Contact: https://tudominio.com/security
Expires: 2027-06-01T00:00:00.000Z
Preferred-Languages: es, en
Encryption: https://tudominio.com/pgp-key.txt
Policy: https://tudominio.com/.well-known/security.txt
Canonical: https://tudominio.com/.well-known/security.txt
-----BEGIN PGP SIGNATURE-----

(Your PGP signature here)
-----END PGP SIGNATURE-----
```

Una vez publicado, este archivo debe estar accesible en `https://tudominio.com/.well-known/security.txt` y `https://tudominio.com/security.txt`.

- [ ] **Step 2: Crear Vulnerability Disclosure Policy**

```markdown
# Vulnerability Disclosure Policy — Partidos Hoy

## Scope
This policy applies to the Partidos Hoy WordPress plugin (all versions).

## Reporting a Vulnerability
Send details to: seguridad@tudominio.com
Expected response time: 24-72 hours

## What to include
- Plugin version
- Steps to reproduce
- Potential impact
- Any proof of concept (non-destructive)

## Our commitment
- Acknowledge receipt within 24 hours
- Provide regular updates on fix progress
- Credit researchers (with permission) in release notes
- Release security patches separate from feature updates

## Safe harbor
We will not take legal action against researchers who:
- Follow this disclosure policy
- Make a good faith effort to avoid privacy violations
- Do not exploit vulnerabilities beyond what is necessary to demonstrate them
```

- [ ] **Step 3: Configurar Dependabot en el repo**

Crear `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

  - package-ecosystem: "composer"
    directory: "/wp-plugin"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
```

- [ ] **Step 4: Commit**

```bash
git add wp-plugin/security.txt .github/dependabot.yml
git commit -m "chore: CRA compliance - security.txt, VDP, Dependabot"
```

---

## Resumen de Tareas — v1.0 REAL (lo que realmente se implementó)

| # | Task | Estado | Notas |
|---|------|--------|-------|
| 1 | Config + fixtures hardcodeados | ✅ | `fixtures_wc2026.json` + `config.py` simplificado |
| 2 | **eloratings.net scraper** | ✅ | Scraping de `World.tsv` → `team_ratings.json` (244 equipos) |
| 3 | **EloPredictor (fórmula ELO clásica)** | ✅ | Home advantage +100, K=400 → 1X2 + expected_goals |
| 4 | 104 fixtures hardcodeados | ✅ | `data/fixtures_wc2026.json` — 72 grupo + 32 KO |
| 5 | Workflow GHA (cada 6h) | ✅ | Sin steps de diagnóstico, sin API keys |
| 6 | Plugin WordPress | ✅ | Freemius, shortcodes, admin, data client |
| 7 | CRA compliance | ✅ | security.txt + VDP + Dependabot |

**Código legacy eliminado** (existía en el plan original pero NO en producción):
- API-Football client (free tier no tiene season 2026)
- FBref scraper vía soccerdata (WC 2026 no disponible)
- football-data.org client (sin World Cup en free tier)
- DataCascade orquestador (todas las fuentes fallan)
- XGBoost trainer, calibrator, predictor (para v2.0)
- Rate limiter (ya no se usan APIs externas)
- Historical data parser, feature builder, ELO ratings class, rolling stats
- Tests legacy (14 archivos de módulos eliminados)
- Research docs

---

---

## 🔴 REALITY CHECK: Lo que el plan asumió vs. la realidad

Este plan se escribió con suposiciones que NO se cumplieron. Aquí está la verdad:

### Suposiciones Fallidas

| Suposición del Plan | Realidad | Impacto |
|---------------------|----------|---------|
| API-Football free tier tiene season=2026 | ❌ `Free plans do not have access to this season, try from 2022 to 2024.` | Fuente primaria INSERVIBLE |
| FBref vía soccerdata tendrá fixtures del Mundial 2026 | ❌ `is_worldcup_available() = False` | Fallback 1 vacío |
| ClubElo tiene ratings de selecciones nacionales | ❌ ClubElo es solo para clubes, no selecciones | ELO de selecciones no disponible |
| football-data.org tiene World Cup en free tier | ❌ Solo 12 competiciones top, sin Mundial | Fallback 2 vacío |
| XGBoost puede entrenarse con datos históricos de selecciones | ❌ No hay dataset histórico de selecciones accesible gratis | Modelo ML sin entrenar |

### Lo que SÍ funciona

| Recurso | Estado | Cómo se usa |
|---------|--------|-------------|
| **eloratings.net/World.tsv** | ✅ **Scraping libre, sin rate limit** | ELO ratings de TODAS las selecciones nacionales |
| **data/fixtures_wc2026.json** | ✅ 104 partidos del Mundial | Fixtures hardcodeados desde el calendario oficial |
| **ELO formula** | ✅ Probabilidades 1X2 reales | `EloPredictor` usa ELO + home advantage → 3-way |
| **data/team_ratings.json** | ✅ 48 selecciones con ELO | Scrapeado de eloratings el 1 Jun 2026 |
| **Plugin WordPress** | ✅ Consume JSON desde gh-pages | Sin cambios, mismo formato de `latest.json` |

### Arquitectura Real (v1.0)

```
Fixtures: data/fixtures_wc2026.json (hardcodeado)
  + Ratings: eloratings.net scrape → data/team_ratings.json
  + Modelo: ELO formula (sin entrenamiento)
  → predictions/latest.json (104 partidos con probabilidades)
  → gh-pages deploy
  → WordPress consume JSON
```

### Lo que queda para v2.0 (post-Mundial)

- XGBoost/CatBoost con datos históricos de ligas (football-data.co.uk, soccerdata)
- API-Football para ligas regulares (season=2024-2025 sí funciona en free tier)
- Actualización ELO automática post-partido
- Value detection vs odds del mercado

---

**Cobertura del spec (v1.0 REAL):**
- ✅ **v1.0 enfocado exclusivamente en Copa del Mundo 2026** 
- ✅ **Producto: Partidos Hoy - Pronósticos de Fútbol** (partidoshoy.futbol)
- ✅ **Branding sin marcas FIFA**: no usa "FIFA", "World Cup", "Mundial" ni "Copa del Mundo" en nombre del producto
- ✅ Pipeline Python completo (fixtures JSON → EloPredictor → JSON → gh-pages)
- ✅ **Fuente única de datos**: eloratings.net (scraping) + fixtures hardcodeados
- ✅ GitHub Actions CI/CD (1 workflow: worldcup-pipeline cada 6h, sin API keys)
- ✅ Plugin WordPress con shortcode y admin
- ✅ Freemius integración free/premium
- ✅ CRA compliance (security.txt + VDP + Dependabot)
- ✅ Seguridad WordPress (nonces, capability checks, sanitize, escape)
- ✅ Protección legal FIFA (branding sin marcas, disclaimers, checklists)
- ✅ Presupuesto cero (solo GitHub repo público + scraping eloratings.net)
- ✅ Timeline realista para llegar al Mundial (11 junio)
- ✅ Acentos normalizados (Côte d'Ivoire, Türkiye, Curaçao → lookup correcto)
- ✅ Knockout stages marcados como `status: TBD` en vez de NaN

**Arquitectura final (v1.0):**
```
data/fixtures_wc2026.json ──→ EloPredictor ──→ predictions/latest.json ──→ gh-pages ──→ WordPress
data/team_ratings.json ────────↕              (104 matches, prob 1X2, xG)
(eloratings.net scrape)
```

---

## Checklist de Protección Legal (FIFA/Cumplimiento)

> **Fuente**: Investigación legal FIFA completa en KNOWLEDGE_BASE.md §14 y `../research_legal_fifa/`. Riesgo FIFA: BAJO si se siguen estas reglas.

### Tarea pre-lanzamiento: Verificar cada item antes de publicar

- [ ] **Plugin name**: no contiene "FIFA", "World Cup", "Mundial" ni variantes
- [ ] **Description**: sin marcas registradas. Usar "football predictions", "soccer analytics"
- [ ] **Tags (readme.txt)**: sin `fifa`, `world cup`, `mundial`. Tags seguros: `football`, `soccer`, `predictions`, `ml`, `analytics`
- [ ] **Disclaimers**: agregar en admin/footer del plugin: "For informational and entertainment purposes only. Not affiliated with FIFA or any football federation."
- [ ] **readme.txt**: incluir disclaimer legal en la descripción
- [ ] **Privacy Policy**: crear página (necesaria para GDPR + Freemius)
- [ ] **Términos y Condiciones**: crear página (18+, "as is", sin garantía)
- [ ] **Responsible Gambling**: link a GambleAware o equivalente en el shortcode output
- [ ] **Datos**: NO vender JSON crudo de API-Football — solo predicciones derivadas
- [ ] **Logos**: NO usar logos de FIFA, federaciones, selecciones, o clubes en el plugin
- [ ] **URL/Dominio**: NO comprar dominios que contengan "FIFA" o "World Cup"
- [ ] **Marketing**: NO usar hashtags #FIFA, #FIFAWorldCup, #FIFAWorldCup2026
- [ ] **CRA compliance**: security.txt + VDP (ya cubierto en Task 17)
- [ ] **Texto precautorio visible**: en footer del shortcode agregar "Not affiliated with FIFA"
- [ ] **API-Football ToS**: Verificar que no resellemos datos crudos (predicciones derivadas = OK)
- [ ] **Revisión anual**: marcas FIFA pueden cambiar para 2027+ o próximos mundiales

### Notas de Implementación

| Check | Dónde implementarlo |
|-------|-------------------|
| Disclaimer en footer | `class-shortcode.php:render()` — agregar `<p class="ph-disclaimer">` |
| Disclaimers en admin | `class-admin.php:render_admin_page()` |
| readme.txt disclaimer | En `== Description ==` y `== Frequently Asked Questions ==` |
| Privacy Policy + TOS | Páginas separadas en WordPress (contenido estático) |
| Tag checking | Revisar `readme.txt` líneas 1798-1804 antes de publicar en WP.org |
| "Not affiliated" | Constante en `partidos-hoy.php` header comment + shortcode |

### Ejemplo de Disclaimer para el Shortcode

```php
// Agregar al final del método render() en class-shortcode.php
$disclaimer = sprintf(
    '<p class="ph-disclaimer" style="font-size:11px;color:#999;margin-top:12px">' .
    '%s — %s</p>',
    esc_html__('Predicciones generadas por ML para fines informativos y de entretenimiento', 'partidos-hoy'),
    esc_html__('No afiliado con FIFA ni ninguna federación de fútbol', 'partidos-hoy')
);
return ob_get_clean() . $disclaimer;
```
