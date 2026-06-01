# Investigación: APIs, Librerías y Datasets para Predicción de Fútbol

> Fecha: 2026-05-31

---

## 1. APIs de Datos de Fútbol

### 1.1 football-data.org

- **URL**: https://www.football-data.org/
- **Documentación**: https://docs.football-data.org/
- **Qué ofrece**: API RESTful con fixtures, resultados, tablas, alineaciones, sustituciones, estadísticas avanzadas, odds.
- **Planes**:
  | Plan | Precio | Requests/min | Datos |
  |------|--------|-------------|-------|
  | Free | €0/mes | 10 req/min | 12 competiciones, datos básicos |
  | Free + Deep Data | €29/mes | — | Alineaciones, sustituciones, plantillas |
  | ML Pack Light | €29/mes | — | Tendencias avanzadas, forma |
  | Paid superiores | €49-199/mes | 30-60 req/min | Más competiciones y datos profundos |
  | Odds Add-On | +€15/mes | — | Cuotas de apuestas |
  | Statistic Add-On | +€15/mes | — | Estadísticas avanzadas |
- **Rate limit**: Free: 10 req/min. Planes de pago: 30-60 req/min.
- **Cobertura**: Liga Profesional Argentina, A-League, Bundesliga, Jupiler Pro League, Premier League, La Liga, Serie A, Ligue 1, Champions League, Europa League, etc.
- **Notas**: Creado por una persona (daniel@football-data.org). Plan Free永久 gratuito para 12 competiciones top.

### 1.2 API-Football (api-football.com)

- **URL**: https://www.api-football.com/
- **Documentación**: https://www.api-football.com/documentation-v3
- **Qué ofrece**: 1226+ ligas y copas. Endpoints: countries, seasons, leagues, standings, teams, livescore, fixtures, head2head, events, lineups, top scorers, players, transfers, trophies, sidelined, injuries, in-play odds, pre-match odds, statistics, predictions.
- **Planes**:
  | Plan | Precio | Requests/día |
  |------|--------|-------------|
  | Free | $0/mes | 100 req/día |
  | Pro | $19/mes | 7,500 req/día |
  | Ultra | $29/mes | 75,000 req/día |
  | Mega | $39/mes | 150,000 req/día |
  | Custom | Variable | Hasta 1,500,000 req/día |
- **Características clave**: Todos los planes incluyen TODOS los endpoints y competiciones. El plan Free solo limita temporadas históricas. No se requiere tarjeta de crédito para el plan Free. Acceso también a APIs de otros deportes (NBA, NFL, F1, rugby, etc.).
- **Rate limit**: 100 req/día en Free, 7,500/día en Pro, etc.
- **Cobertura**: 1226 ligas en 200+ países.
- **Notas**: El plan Free es suficiente para desarrollo y prototipado. Todos los endpoints disponibles en todos los planes.

### 1.3 Sportmonks

- **URL**: https://www.sportmonks.com/football-api/
- **Planes y precios**: https://www.sportmonks.com/football-api/plans-pricing/
- **Documentación**: https://docs.sportmonks.com/v3/
- **Qué ofrece**: Fixtures, live scores, eventos, plantillas, standings, brackets, estadísticas de jugadores, datos históricos, odds.
- **Planes**:
  | Plan | Precio | Ligas | Requests/hora |
  |------|--------|-------|-------------|
  | Starter | €29/mes (€24 anual) | 5 ligas | 2,000/hora |
  | Growth | €99/mes (€79 anual) | 30 ligas | 2,500/hora |
  | Pro | €249/mes (€199 anual) | 120 ligas | 3,000/hora |
  | Enterprise | Custom | 2300+ ligas | 5,000/hora |
- **Free trial**: 14 días gratis en planes de pago. También hay un plan gratuito con acceso a Danish Superliga y Scottish Premiership.
- **Add-ons**: Datos históricos (+€29 one-time), ligas extra (+€4/mes), odds premium (+€129/mes).
- **Cobertura**: 2300+ ligas mundiales.
- **Notas**: Todos los planes incluyen las mismas características de datos; la diferencia es número de ligas y rate limit.

### 1.4 Understat

- **URL**: https://understat.com/
- **Qué ofrece**: Estadísticas avanzadas: xG (goles esperados), xGBuildup, xGChain, eventos de tiro con xG asociado.
- **Ligas**: Top 5 europeas (Premier League, La Liga, Bundesliga, Serie A, Ligue 1) + ligas adicionales.
- **Acceso**: No tiene API oficial. Se accede via scraping. La librería `soccerdata` tiene scraper integrado (`sd.Understat`).
- **Costos**: Gratuito.
- **Calidad de datos**: Alta para xG, referencia en analytics de fútbol.

### 1.5 TheSportsDB

- **URL**: https://www.thesportsdb.com/
- **API**: https://www.thesportsdb.com/api.php
- **Qué ofrece**: Datos de equipos, jugadores, eventos, livescores (soccer y otros deportes).
- **Planes**:
  | Plan | Precio | Requests/min |
  |------|--------|-------------|
  | Free | $0/mes | 30 req/min |
  | Single Developer | $9/mes | 100 req/min |
  | Small Business | $20/mes | 120 req/min |
- **Notas**: API v1 gratuita con funciones básicas. Versión premium (v2) con livescores cada 2 min, highlights de YouTube. Datos limitados comparado con API-Football o Sportmonks.

### 1.6 OpenLigaDB

- **URL**: https://www.openligadb.de/
- **API**: https://api.openligadb.de/
- **Qué ofrece**: Base de datos comunitaria abierta con datos de fútbol alemán (Bundesliga 1, 2, 3), Champions League, DFB-Pokal y otras ligas.
- **Costos**: **Gratuito** y sin autenticación.
- **Licencia**: Open Database License (ODbL).
- **Formato**: API JSON REST. Ejemplo: `https://api.openligadb.de/getmatchdata/bl1/2024`
- **Notas**: Ideal para datos de fútbol alemán. No requiere API key. Community-driven.

### 1.7 football-data.co.uk

- **URL**: https://www.football-data.co.uk/
- **Qué ofrece**: Resultados históricos, estadísticas de partidos y **cuotas de apuestas** en formato CSV/Excel.
- **Cobertura**: 22 divisiones de 11 países europeos. Datos desde 1993/94 (resultados), 2000/01 (odds).
- **Costos**: **Gratuito**.
- **Actualización**: 2 veces por semana.
- **Estadísticas disponibles**: Goles, tiros a puerta, córners, faltas, fueras de juego, tarjetas, árbitros. Cuotas de hasta 10 casas de apuestas.
- **Notas**: Es el dataset más usado para investigación de predicción de fútbol. Datos en CSV listos para análisis.

---

## 2. Librerías Python Open-Source

### 2.1 soccerdata

- **PyPI**: https://pypi.org/project/soccerdata/
- **Documentación**: https://soccerdata.readthedocs.io/
- **GitHub**: https://github.com/probberechts/soccerdata
- **Versión**: 1.9.0
- **Licencia**: Apache-2.0
- **Python**: >=3.10, <3.15
- **Qué hace**: Colección de scrapers para datos de fútbol desde múltiples fuentes.
- **Fuentes soportadas**:
  | Clase | Fuente | Datos |
  |-------|--------|-------|
  | `ClubElo` | clubelo.com | Rating Elo de equipos europeos |
  | `ESPN` | espn.com/soccer | Resultados históricos, estadísticas, alineaciones |
  | `FBref` | fbref.com | Resultados, alineaciones, estadísticas detalladas (basado en Opta) |
  | `MatchHistory` | football-data.co.uk | Resultados, odds, estadísticas |
  | `Sofascore` | sofascore.com | Resultados, schedules, alineaciones, estadísticas |
  | `SoFIFA` | sofifa.com | Ratings de EA Sports FC (FIFA) |
  | `Understat` | understat.com | xG, xGBuildup, xGChain, eventos de tiro |
  | `WhoScored` | whoscored.com | Resultados, previews, datos Opta event stream |
- **Output**: Pandas DataFrames. Nombres de columnas uniformes entre fuentes.
- **Caching**: Datos cacheados localmente en `~/soccerdata`.
- **Notas**: Para WhoScored requiere Selenium + ChromeDriver. Se integra con `socceraction` para análisis de event stream.

### 2.2 football-data (openligadb wrapper)

- **PyPI**: https://pypi.org/project/openligadb/
- **Documentación**: https://openligadb.readthedocs.io/
- **Qué hace**: Cliente Python para la API de OpenLigaDB.
- **Uso**:
  ```python
  from openligadb.api import Connection
  connection = Connection()
  table = connection.get_table("bl1", 2016)
  matches = connection.get_matches("bl1", 2016)
  ```
- **Notas**: Probado con fútbol. Gratuito.

### 2.3 betfairlightweight

- **URL**: https://github.com/liampauling/betfairlightweight
- **Qué hace**: Cliente Python para la API de Betfair (mercado de apuestas de intercambio).
- **Funcionalidades**: Acceso a cuotas en vivo, historial de mercado, apuestas automáticas.
- **Uso típico**: Trading deportivo, obtención de cuotas en tiempo real para modelos de predicción.
- **Notas**: Requiere cuenta en Betfair y certificados de API. No es gratuito (Betfair cobra comisión).

### 2.4 mplsoccer

- **PyPI**: https://pypi.org/project/mplsoccer/
- **Documentación**: https://mplsoccer.readthedocs.io/
- **GitHub**: https://github.com/andrewRowlinson/mplsoccer
- **Versión**: 1.6.1
- **Licencia**: MIT
- **Stars**: 511+ en GitHub
- **Qué hace**: Librería de visualización de fútbol basada en matplotlib.
- **Funcionalidades**:
  - Dibujar canchas de fútbol (9 tipos)
  - Gráficos radar, pizza (Nightingale), bumpy charts
  - Heatmaps, hexbins, scatter, flechas, líneas cometa
  - Cargar datos de StatsBomb open-data
  - Estandarizar coordenadas de cancha
- **Dependencias**: matplotlib, numpy, pandas, pillow, requests, scipy, seaborn.
- **Uso**:
  ```python
  from mplsoccer import Pitch
  pitch = Pitch(pitch_color='grass', line_color='white', stripe=True)
  fig, ax = pitch.draw()
  ```

### 2.5 Otras librerías relevantes

- **socceraction**: https://github.com/ML-KULeuven/socceraction - Análisis de event stream data (VAEP, xT). Se integra con soccerdata.
- **statsbombpy**: https://github.com/statsbomb/statsbombpy - Cliente Python para datos abiertos de StatsBomb.
- **scrapy**: Framework de scraping. Útil para extraer datos de sitios sin API.
- **selenium**: Automatización de navegador. Necesario para sitios con protección anti-scraping (ej. WhoScored).

---

## 3. Datasets Gratuitos

### 3.1 European Soccer Database (Kaggle)

- **URL**: https://www.kaggle.com/datasets/hugomathien/soccer
- **Formato**: SQLite (`database.sqlite`)
- **Contenido**: +25,000 partidos, +10,000 jugadores, 11 países europeos, temporadas 2008-2016.
- **Datos**: Resultados, atributos de jugadores (de EA Sports FIFA), alineaciones (coordenadas X,Y), cuotas de hasta 10 casas de apuestas, eventos detallados del partido.
- **Notas**: El dataset abierto más usado en Kaggle para predicción de fútbol. Muy citado en papers académicos.

### 3.2 Club Football Match Data 2000-2025

- **GitHub**: https://github.com/xgabora/Club-Football-Match-Data-2000-2025
- **Kaggle**: https://www.kaggle.com/datasets/adamgbor/club-football-match-data-2000-2025
- **Formato**: CSV
- **Contenido**: ~475,000 filas, 27 países, 42 ligas. Temporadas 2000/01 a 2024/25.
- **Datos**: Resultados, estadísticas, odds, ratings Elo.
- **Tamaño**: ~51MB
- **Licencia**: MIT
- **Notas**: El dataset abierto más grande y actualizado de su tipo. Actualizado mensualmente via pipeline Python.

### 3.3 Football Matches 2024/2025 (Top Leagues + UCL)

- **GitHub**: https://github.com/tarekmasryo/Football-Matches-Results-2024-25-Dataset
- **Kaggle**: https://www.kaggle.com/datasets/tarekmasryo/football-matches-20242025-top-5-leagues
- **Formato**: CSV
- **Contenido**: 1,941 partidos, 6 competiciones (Top 5 + UCL).
- **Datos**: Resultados FT/HT, goal difference, total goals, outcome, puntos.
- **Fuente**: football-data.org. Atribución requerida.
- **Licencia**: CC BY 4.0

### 3.4 Football Data from football-data.co.uk

- **URL**: https://www.football-data.co.uk/data.php
- **Formato**: CSV/Excel
- **Contenido**: Datos desde 1993/94. Resultados, cuotas de apuestas, estadísticas (tiros, córners, faltas, tarjetas).
- **Cobertura**: 22 divisiones europeas. Actualizado 2 veces/semana.
- **Costos**: Gratuito.

### 3.5 StatsBomb Open Data

- **URL**: https://github.com/statsbomb/open-data
- **Formato**: JSON (event stream data)
- **Contenido**: Datos de eventos detallados de partidos seleccionados (Mundial 2018, Champions League, La Liga, etc.).
- **Acceso via Python**: `mplsoccer`, `statsbombpy`.
- **Licencia**: MIT (con atribución requerida: "Data provided by StatsBomb").

### 3.6 Hugging Face Datasets

- **FootballPredictionDataset**: https://huggingface.co/datasets/AmjadKha/FootballPredictionDataset
- **Formato**: CSV, ~3,000 registros.
- **Licencia**: MIT.
- **Notas**: Dataset pequeño pero listo para usar con Hugging Face Datasets library.

---

## 4. Aspectos Legales

### 4.1 Términos de uso de APIs

| API | Restricciones clave |
|-----|-------------------|
| **football-data.org** | No redistribuir datos crudos. Cacheo permitido. Uso personal/comercial permitido dentro del plan. |
| **API-Football** | Prohibido revender datos directamente. Prohibido tener múltiples cuentas Free. Los logos/imagénes son de terceros. Sujeto a ley francesa. |
| **Sportmonks** | Datos históricos (>3 temporadas) requiere add-on. No redistribuir raw data. |
| **TheSportsDB** | Atribución requerida en apps gratuitas. Prohibido scraping. |
| **OpenLigaDB** | Open Database License (ODbL) - permite uso, modificación y redistribución con atribución. |
| **football-data.co.uk** | Datos gratuitos. Atribución requerida si se redistribuye. |

### 4.2 Legalidad del scraping

- **Scraping NO es ilegal per se**, pero violar términos de servicio (ToS) puede resultar en:
  - Bloqueo de IP y pérdida de acceso a la fuente.
  - Potenciales reclamos legales bajo leyes de acceso no autorizado (ej. CFAA en EE.UU.).
- **Sitios que prohíben scraping explícitamente**: ESPN, WhoScored (tiene protección Incapsula), UEFA, BBC Sport.
- **Sitios que permiten scraping con límites**: FBref, Understat, Football-Data.co.uk.
- **Mejor práctica**: Usar APIs oficiales siempre que sea posible. Si se scrapea, respetar `robots.txt`, rate limits, y no sobrecargar servidores.
- **Datos de apuestas**: Las cuotas de casas de apuestas pueden tener restricciones adicionales.

### 4.3 Atribución requerida

- **football-data.org**: "Football data provided by the Football-Data.org API"
- **StatsBomb**: "Data provided by StatsBomb"
- **football-data.co.uk**: Atribución si se redistribuye.
- **OpenLigaDB**: Licencia ODbL requiere atribución.
- **Kaggle datasets**: Verificar licencia específica de cada dataset (MIT, CC BY 4.0, etc.).

### 4.4 Recomendaciones legales para proyectos de predicción

1. Si usas API-Football o Sportmonks: cumple con sus ToS (no revender datos crudos).
2. Si scrapeas: verifica `robots.txt`, usa rate limiting, no compartas datos scrapeados públicamente.
3. Si publicas datos derivados: atribuye la fuente original.
4. Para uso académico/personal: la mayoría de fuentes son accesibles sin problemas.
5. Para uso comercial: contacta con el proveedor de datos para obtener licencia adecuada.

---

## 5. Resumen Comparativo

| Fuente | Costo Mensual | Cobertura | Rate Limit | Ideal Para |
|--------|--------------|-----------|------------|------------|
| football-data.org | €0-€199 | 12-50+ ligas | 10-60 req/min | Proyectos pequeños/medios |
| API-Football | $0-$39 | 1226 ligas | 100-150k req/día | Proyectos que necesitan máxima cobertura |
| Sportmonks | €0-€249+ | 2300+ ligas | 2k-5k req/hora | Proyectos profesionales |
| OpenLigaDB | **Gratis** | Ligas alemanas | Sin límite | Datos de Bundesliga |
| football-data.co.uk | **Gratis** | 22 divisiones | Sin límite (CSV) | Investigación, datasets históricos |
| TheSportsDB | $0-$20 | Multideporte | 30-120 req/min | Datos básicos multideporte |
| Understat | **Gratis** | Top 5 europeas | Via scraping | xG y estadísticas avanzadas |
| soccerdata (lib) | **Gratis** | Múltiples fuentes | N/A | Scraping unificado en Python |

**Recomendación**: Para empezar un proyecto de predicción de fútbol:
1. Usa **soccerdata** (Python) para obtener datos gratis de FBref, Understat y Football-Data.co.uk.
2. Complementa con **API-Football Free** (100 req/día) para datos estructurados vía API.
3. Usa **mplsoccer** para visualización.
4. El dataset **European Soccer Database** (Kaggle) o **Club Football Match Data 2000-2025** (GitHub) para entrenar modelos offline.

---

*Investigación realizada el 31 de mayo de 2026 mediante búsqueda web.*
