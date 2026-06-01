# Base de Conocimiento: Partidos Hoy — Sistema de Pronósticos de Fútbol

> **Producto:** Partidos Hoy - Pronósticos de Fútbol
> **Dominio:** partidoshoy.futbol
> **v1.0:** Copa del Mundo 2026
> **Generado:** 31 de mayo de 2026 mediante investigación multi-agente
> 
> ⚠️ **Restricción de marca**: Por investigación legal (ver §14), NO usar "FIFA", "World Cup", "Mundial" ni "Copa del Mundo" en branding del producto. Uso descriptivo en contenido OK.

---

## ⚠️ RESTRICCIÓN FUNDAMENTAL: PRESUPUESTO CERO

**TODO el sistema debe implementarse con presupuesto CERO absoluto.** Esto significa:

- **Sin APIs de pago**: No se pagará por football-data.org, API-Football, Sportmonks ni ninguna otra API. Solo se usan planes gratuitos o nulos.
- **Sin servicios cloud de pago**: No AWS, GCP, Azure, ni SaaS que requiera tarjeta de crédito. Todo corre en localhost o GitHub.
- **Sin librerías premium**: Solo open-source (MIT, Apache, BSD, GPL).
- **Sin servidores pagos**: Desarrollo y ejecución 100% local. Frontend desplegable en plataformas gratuitas (Streamlit Cloud, Vercel Free, GitHub Pages).
- **Sin costos recurrentes**: Cero suscripciones, cero microtransacciones.

**Cada decisión tecnológica en este documento está filtrada por esta restricción.** Cuando existan alternativas pago vs gratis, se marca explícitamente y se elige la gratuita. Si una herramienta tiene plan free limitado, se documenta el límite y se diseña alrededor de él.

**Skills de presupuesto cero disponibles**: `last30days-free` (en `30 Dias/`) proporciona una metodología validada de investigación y contenido sin depender de APIs de pago.

---

## 🏠 PLATAFORMA ÚNICA: GITHUB + GITHUB ACTIONS

**GitHub es la plataforma única para TODO el proyecto.** No se usa ninguna otra plataforma de orquestación, CI/CD o despliegue.

| Servicio | Propósito | Costo |
|----------|-----------|-------|
| **GitHub** | Repositorio de código, control de versiones, documentación | $0 |
| **GitHub Actions** | Orquestación del pipeline (reemplaza Airflow/Prefect) | $0 (repositorio público = minutos ilimitados gratis) |
| **GitHub Pages** | Documentación estática si se requiere | $0 |
| **GitHub Issues** | Seguimiento de tareas y bugs | $0 |
| **GitHub Releases** | Versionado de modelos y datasets | $0 |
| **GitHub Secrets** | Almacenamiento de API keys y tokens | $0 |

**Workflow típico en GitHub Actions**:
- Un workflow programado (cron) se ejecuta automáticamente cada día
- Corre el pipeline completo: extraer datos → feature engineering → entrenar modelo → generar predicciones JSON
- El JSON resultante se publica como artifact del workflow o se sube a un branch `gh-pages` para que WordPress lo consuma vía URL pública
- Si el modelo mejora métricas vs la versión anterior, se actualiza automáticamente; si no, se revierte solo

---

---

## Visión General del Sistema (v1.0 REAL)

```
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS                                │
│  Pipeline automático (cada 6h durante Mundial) — $0              │
│                                                                  │
│  DATOS: FUENTE ÚNICA (sin APIs externas)                         │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Fixtures hardcodeados (data/fixtures_wc2026.json)          │ │
│  │  104 partidos: 72 grupo + 32 KO                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                          ↓                                       │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  ELO ratings (data/team_ratings.json)                       │ │
│  │  Scrapeado de eloratings.net/World.tsv                      │ │
│  │  244 equipos nacionales, 48 del WC encontrados              │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                          ↓                                       │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  EloPredictor                                               │ │
│  │  Fórmula ELO clásica: home advantage +100, K=400           │ │
│  │  → probabilidades 1X2 + expected_goals                      │ │
│  │  → Knockout TBD marcados como status: "TBD"                │ │
│  │  → Acentos normalizados (Côte → Cote, Türkiye → Turkiye)   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                          ↓                                       │
│  predictions/latest.json (104 matches, prob 1X2, xG)             │
│     → gh-pages deploy automático                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │  URL pública del JSON
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WORDPRESS PLUGIN                              │
│  (PHP, shortcode [partidos-hoy])                                │
│                                                                  │
│  Lee el JSON desde GitHub Pages (URL pública)                    │
│  Muestra en el sitio web:                                        │
│  ┌─────────────┬──────┬──────┬──────┬──────────────┐            │
│  │ Partido     │  1   │  X   │  2   │  Goles Esp.  │            │
│  ├─────────────┼──────┼──────┼──────┼──────────────┤            │
│  │ México      │ 73%  │ 21%  │  6%  │  2.04-0.35   │            │
│  │ vs Sudáfrica│      │      │      │              │            │
│  └─────────────┴──────┴──────┴──────┴──────────────┘            │
│  + Detalles: expected_goals por equipo                           │
└─────────────────────────────────────────────────────────────────┘
```

**v1.0 = Copa del Mundo 2026.** Post-Copa (19 julio 2026+) se expandirá a ligas regulares bajo la marca Partidos Hoy.

**¿Qué hace?** Un sistema de pronósticos 100% sobre GitHub + GitHub Actions, enfocado en la Copa del Mundo 2026:
1. **Un workflow de GitHub Actions** se ejecuta cada 6 horas (durante Jun-Jul 2026)
2. **Lee fixtures hardcodeados** de `data/fixtures_wc2026.json` (104 partidos)
3. **Carga ELO ratings** de `data/team_ratings.json` (48 selecciones, scrapeado de eloratings.net)
4. **Genera predicciones con fórmula ELO** (home advantage +100, K=400 → probabilidades 1X2 + xG)
5. **Publica `latest.json`** en GitHub Pages para que WordPress lo consuma
6. **El plugin de WordPress** lee ese JSON y lo muestra en el sitio web
7. **No depende de APIs externas**: sin rate limits, sin API keys, sin costos

**Caso de uso típico**: Durante un Mundial, el workflow de Actions se ejecuta cada 6 horas. Calcula probabilidades ELO para cada partido basándose en el rating histórico de cada selección (eloratings.net). Los partidos de eliminatorias aparecen como "TBD" hasta que se definan los clasificados. El plugin de WordPress las muestra automáticamente en tu sitio.

### ⚠️ Nota sobre fuentes de datos

El plan original contemplaba 3 fuentes en cascada (API-Football → FBref → football-data.org). En la práctica:
- **API-Football free tier**: ❌ NO tiene season 2026 (`Free plans do not have access to this season`)
- **FBref vía soccerdata**: ❌ WC 2026 no disponible aún (`is_worldcup_available() = False`)
- **football-data.org free**: ❌ No incluye World Cup
- **ClubElo (soccerdata)**: ❌ Solo clubes, no selecciones nacionales
- **eloratings.net/World.tsv**: ✅ Scraping libre, sin rate limit, 244 equipos nacionales
- **Fixtures hardcodeados**: ✅ 104 partidos del calendario oficial

La arquitectura real v1.0 usa solo las fuentes que ✅ funcionan.

---

## Índice

0. [Visión General del Sistema](#visión-general-del-sistema)
1. [Skills y Agentes Disponibles en Proyectos](#1-skills-y-agentes-disponibles-en-proyectos)
2. [Modelos Estadísticos Clásicos](#2-modelos-estadísticos-clásicos)
3. [Machine Learning para Predicción Deportiva](#3-machine-learning-para-predicción-deportiva)
4. [APIs, Datos y Librerías](#4-apis-datos-y-librerías)
5. [Modelos de Apuestas y Odds](#5-modelos-de-apuestas-y-odds)
6. [Herramientas y Sistemas Existentes](#6-herramientas-y-sistemas-existentes)
7. [Validación Competitiva: Plugins WordPress](#7-validación-competitiva-plugins-wordpress-de-predicciones)
8. [Arquitectura de Sistema Recomendada](#8-arquitectura-de-sistema-recomendada)
9. [MLOps y Buenas Prácticas](#9-mlops-y-buenas-prácticas)
10. [Stack Tecnológico Recomendado](#10-stack-tecnológico-recomendado)
11. [Referencias](#11-referencias)
12. [Validación de Viabilidad 2026](#12-validación-de-viabilidad-2026--investigación-completa)
13. [Referencias Agregadas en Validación 2026](#13-referencias-agregadas-en-validación-2026)

---

## 1. Skills y Agentes Disponibles en Proyectos

### Skills de Investigación y Contenido

| Skill | Ubicación | Propósito |
|-------|-----------|-----------|
| **last30days** (v2.9.5) | `30 Dias/last30days-skill/SKILL.md` | Motor de investigación profunda cubriendo Reddit, X, YouTube, TikTok, HN, Polymarket, Bluesky, Truth Social. Útil para monitorear tendencias de fútbol y conversación social |
| **last30days-free** (v1.2.0) | `30 Dias/last30days-skill/SKILL_FREE.md`, `Web Pulso Paraguay/SKILL_FREE.txt`, `Web Pulso Paraguay/Frigomás/SKILL_FREE.txt` | Versión gratuita con 4 fases: Research, Strategy, Generation, QC. Sin dependencias de pago |

### Skills de Sistema (OpenCode)

Skills disponibles globalmente a través del sistema superpowers: brainstorming, web-research, dispatching-parallel-agents, systematic-debugging, test-driven-development, writing-plans, etc.

### The Agency — Agentes para Desarrollo (agency-agents/)

Repositorio completo `agency-agents/` (msitarzewski/agency-agents, MIT) con ~180 agentes AI especializados. Los relevantes para el proyecto:

| Agente | Archivo | Rol en el proyecto |
|--------|---------|--------------------|
| **Data Engineer** 🔧 | `engineering/engineering-data-engineer.md` | Pipeline de datos: extracción, limpieza, transformación |
| **AI Engineer** 🤖 | `engineering/engineering-ai-engineer.md` | Modelo ML: features, entrenamiento, calibración |
| **Software Architect** 🏛️ | `engineering/engineering-software-architect.md` | Diseño del sistema, ADRs, decisiones técnicas |
| **CMS Developer** 🧱 | `engineering/engineering-cms-developer.md` | Plugin WordPress: shortcodes, REST API, custom post types |
| **Rapid Prototyper** ⚡ | `engineering/engineering-rapid-prototyper.md` | Validación rápida del pipeline antes de pulirlo |
| **Backend Architect** 🏗️ | `engineering/engineering-backend-architect.md` | API design, esquema de datos, estructura del repo |
| **Code Reviewer** 👁️ | `engineering/engineering-code-reviewer.md` | Code quality, seguridad, mantenibilidad |
| **Senior Developer** 💎 | `engineering/engineering-senior-developer.md` | Implementación avanzada (Laravel/Livewire si se usa) |

**Además en strategy/coordination:**
- `agent-activation-prompts.md` — Plantillas para activar cualquier agente dentro del flujo de desarrollo
- `handoff-templates.md` — Para pasar contexto entre agentes

**Además en strategy/runbooks:**
- `scenario-startup-mvp.md` — Runbook de 4-6 semanas para construir un MVP desde cero (aplica directamente a este proyecto)

---

## 2. Modelos Estadísticos Clásicos

### 2.1 Poisson Independiente (Maher, 1982)

- **Fórmula**: P(X = k) = (λ^k × e^(-λ)) / k!
- **Goles esperados**: λ_local = μ × α_local × β_visitante, λ_visitante = μ × α_visitante × β_local
- **Precisión**: ~45-50% en 1X2
- **Limitaciones**: Subestima empates y marcadores 0-0, 1-1; no captura correlación local-visitante

### 2.2 Dixon-Coles (1997) — Estándar de la Industria

- Extiende Poisson con factor τ (rho) para dependencia en marcadores bajos
- **Factor τ**: corrige probabilidades para 0-0, 0-1, 1-0, 1-1
- **Ponderación temporal**: pesos exponenciales w(t) = e^(-ξ × (t_actual - t_partido))
- **Precisión**: ~48-53% en 1X2, con ~3-5% mejora sobre Poisson básico

### 2.3 Poisson Bivariante (Karlis-Ntzoufras, 2003)

- Modela conjuntamente goles con covarianza explícita
- Mejor que Poisson independiente para predicción de empates

### 2.4 Sistema Elo para Fútbol

- **Fórmula**: E[S_local] = 1 / (1 + 10^(-(R_local - R_visitante + h) / 400))
- **Actualización**: R_post = R_pre + K × (S - E[S])
- **Ajustes**: diferencia de goles, importancia del partido
- **Precisión**: ~55-60% en selecciones
- **World Football Elo**: eloratings.net; **ClubElo**: clubelo.com

### 2.5 Expected Goals (xG)

- Modelo de clasificación binaria P(gol | características del disparo)
- Variables: coordenadas, distancia, ángulo, parte del cuerpo, tipo de jugada
- **AUC típico**: ~0.78-0.80 (StatsBomb: 0.801, Bayesiano 7 variables: 0.781)
- **Proveedores**: Understat, StatsBomb, Opta, Wyscout

### 2.6 Distribución Skellam (Karlis-Ntzoufras)

- Modela DIFERENCIA de goles con distribución Skellam
- Ventaja: no necesita modelar correlación explícitamente
- Ideal para hándicap asiático

### 2.7 Negative Binomial

- Alternativa a Poisson que maneja overdispersion
- Útil para ligas de alta anotación, tarjetas y córners

### Precisión Comparativa

| Modelo | Precisión 1X2 | Notas |
|--------|--------------|-------|
| Poisson independiente | 45-50% | Baseline |
| Dixon-Coles | 48-53% | +3-5% sobre Poisson |
| Elo | 55-60% selecciones | No da marcadores exactos |
| xG + Poisson | 50-55% | Requiere datos de calidad |
| XGBoost/CatBoost | 50-58% | State-of-the-art actual |

---

## 3. Machine Learning para Predicción Deportiva

### 3.1 Algoritmos — Estado del Arte

**Gradient Boosting (XGBoost, CatBoost, LightGBM)** es el state-of-the-art actual:

| Algoritmo | Accuracy | Contexto |
|-----------|----------|----------|
| XGBoost | ~65% | Ligas europeas, datasets históricos |
| CatBoost + pi-ratings | 55.82% | 2023 Soccer Prediction Challenge (714+ partidos) |
| Random Forest | ~59% | Superado por boosting |
| Regresión Logística | 52-55% | Excelente baseline calibrada |
| MLP (3 capas) | 62.5% | Premier League, datos largos |
| LSTM | ~55% | Premier League 08-19, Stanford CS230 |
| HIGFormer (Graph Transformer) | 52.19% | KDD 2025, estado del arte en DL |

**Conclusión**: Deep learning NO supera consistentemente a gradient boosting en datos tabulares de fútbol. LSTM/GRU aportan valor solo con datos secuenciales (odds cambiantes).

### 3.2 Feature Engineering

#### Categorías de Features

| Categoría | Features | Fuente |
|-----------|----------|--------|
| **Fuerza** | ELO_home, ELO_away, ΔELO, pi-rating, ranking | Exprysm, ClubElo |
| **Forma reciente** | FormDiff, rolling GF/GC (3, 5, 10 partidos), DifPts | football-data.co.uk |
| **Localía** | HFA (50-100 pts ELO), rendimiento L/V separados | Histórico |
| **Head-to-Head** | Últimos N enfrentamientos, diff goles H2H | football-data.org |
| **Avanzadas** | xG, xT, posesión, fatiga (días desde último partido) | Understat, Opta |
| **Contextuales** | Fase de temporada, congestión fixtures, rotación | Programación |

#### Pi-Ratings (mejora sobre Elo)

Separación de fuerza en 4 componentes: pi_att_home, pi_def_home, pi_att_away, pi_def_away. Actualización independiente. Mejor rendimiento probado con CatBoost.

### 3.3 Prevención de Data Leakage

**Regla #1**: Split cronológico, NUNCA aleatorio. TimeSeriesSplit de scikit-learn.

**Checklist anti-leakage:**
- [ ] Rolling averages calculados solo con datos anteriores al match
- [ ] Normalización por ventana de entrenamiento, no global
- [ ] Target encoding con smoothing y solo datos disponibles
- [ ] ELO ratings actualizados secuencialmente
- [ ] Validación en temporada completa hold-out
- [ ] Backtest con ROI contra odds reales

**Señales de alarma**: Accuracy > 70% = sospechoso de leakage; gap train-test > 10%; rendimiento cae entre temporadas.

### 3.4 Métricas de Evaluación

| Prioridad | Métrica | Fórmula | Propósito |
|-----------|---------|---------|-----------|
| 1 | **Brier Score** | (1/N)Σ(f_t - o_t)² | Calibración general. < 0.20 bueno, < 0.18 excelente |
| 2 | **Log Loss** | -(1/N)Σ(y·log(p)+(1-y)·log(1-p)) | Penaliza sobreconfianza |
| 3 | **Accuracy × clase** | correctas/total | Diagnóstico H/D/A. Draw < 30% recall típico |
| 4 | **ECE** | Σ|acc(bin)-conf(bin)|×peso | Calibración por bins. < 0.05 bueno |
| 5 | **ROI simulado** | (Σretornos-Σstakes)/Σstakes | Validación financiera vs odds reales |
| 6 | **CLV** | (odds_apostadas / fair_odds_cierre) - 1 | Edge real vs Pinnacle |

---

## 4. APIs, Datos y Librerías

### 4.1 APIs de Datos

> **Filtro de presupuesto cero**: Solo las opciones marcadas como "GRATIS" o con plan free viable son aceptables. Sportmonks y planes de pago de otras APIs quedan descartados automáticamente.
>
> **v1.0 = SOLO Mundial 2026.** ⚠️ Realidad verificada: las 3 fuentes previstas (API-Football, FBref, football-data.org) **NO funcionan para WC 2026** en plan free. La fuente real es **eloratings.net** (scraping de World.tsv, 244 equipos) + fixtures hardcodeados en `data/fixtures_wc2026.json` (104 partidos). Las fuentes de ligas regulares se integrarán en v2.0 post-Mundial.

| Fuente | Costo/mes Real | Cobertura (plan free) | Rate Limit | Rol en v1.0 |
|--------|---------------|----------------------|------------|-------------|
| **API-Football** | $0 (Free) | 1226 ligas, **pero season=2026 NO disponible en free tier** | 100 req/día | ❌ Para WC 2026 |
| **eloratings.net** | **$0** (scraping) | **World Football Elo Ratings de TODAS las selecciones** | Sin límite | 🥇 Primaria |
| **FBref (vía soccerdata)** | **$0** (scraping) | Mundial 2026 **aún no disponible** (Jun 2026) | Sin límite | ❌ Hoy, 🔒 Post-torneo |
| **ClubElo (vía soccerdata)** | **$0** | Solo clubes, NO selecciones nacionales | Sin límite | ❌ |
| **football-data.org** | €0 (Free) | 12 competiciones top, **sin Mundial en free** | 10 req/min | ❌ |
| **football-data.co.uk** | **$0** | 22 divisiones, odds desde 1993 | CSV semanal | 📊 Histórico |
| **StatsBomb Open Data** | **$0** | Eventos detallados selectos | GitHub | 📊 Validación |
| **OpenLigaDB** | **$0** | Ligas alemanas | Sin límite | 🔒 Post-v1.0 |
| **Understat (vía soccerdata)** | **$0** (scraping) | Top 5 europeas, xG | Sin límite | 🔒 Post-v1.0 |
| **TheSportsDB** | $0 (Free) | Multideporte básico | 30 req/min | 🔒 Post-v1.0 |
| **Sportmonks** | €29/mes mínimo real | Sin plan free completo | — | ❌ Descartado |
| **Bzzoiro Sports Data (BSD)** | **$0** | 100+ competiciones, 34 deportes | 100 req/día | 🔒 Post-v1.0 |

### 4.2 Librerías Python Open-Source

| Librería | Función | Fuentes |
|----------|---------|---------|
| **soccerdata** | Scraping unificado | FBref, Understat, WhoScored, ESPN, ClubElo, Sofascore |
| **socceraction** | Análisis event stream (VAEP, xT) | StatsBomb, Wyscout |
| **statsbombpy** | Cliente StatsBomb open-data | StatsBomb |
| **mplsoccer** | Visualización + canchas | StatsBomb, datos propios |
| **betfairlightweight** | API Betfair | Betfair Exchange |
| **openligadb** | Cliente OpenLigaDB | OpenLigaDB |

### 4.3 Datasets Gratuitos Recomendados

| Dataset | Formato | Contenido | Tamaño |
|---------|---------|-----------|--------|
| **European Soccer Database** (Kaggle) | SQLite | 25K+ partidos, 11 países, 2008-2016, +odds | ~500MB |
| **Club Football Match Data 2000-2025** | CSV | ~475K filas, 27 países, 42 ligas, Elo ratings | ~51MB |
| **football-data.co.uk** | CSV | 22 divisiones, desde 1993, odds 10 casas | Actualizado |
| **StatsBomb Open Data** | JSON | Eventos detallados, xG, competiciones selectas | GitHub |

### 4.4 Stack de Datos v1.0 (Real)

`eloratings.net` (scraping World.tsv) + `data/fixtures_wc2026.json` (hardcodeado) + `EloPredictor` (fórmula ELO clásica)

**Para v2.0 (post-Mundial):** `soccerdata` + `API-Football Free` + `mplsoccer` + datasets Kaggle/GitHub + `football-data.co.uk`

---

## 5. Modelos de Apuestas y Odds

### 5.1 Conversión Odd ↔ Probabilidad

- **Decimal → Probabilidad**: P = 1 / odds_decimales
- **Fraccionaria → Probabilidad**: P = denominador / (numerador + denominador)
- **Americana (−)**: P = |odds| / (|odds| + 100)
- **Americana (+)**: P = 100 / (odds + 100)

### 5.2 Overround y Devigging

El overround es el margen de la casa (suma de probabilidades implícitas - 100%).

**Métodos para quitar el vig** (recomendados en orden):

1. **Power Method** — Recomendado por defecto para fútbol 1X2
2. **Método Multiplicativo** — Simple, para mercados balanceados 2-vías
3. **Método de Shin (1992)** — Gold standard para multi-resultado con favorite-longshot bias
4. **Método Aditivo** — Solo histórico, puede dar probabilidades negativas

### 5.3 Value Betting

```
EV = (probabilidad_estimada × odds_decimales) - 1
```

- EV > 0: apuesta con valor positivo
- Las odds de **Pinnacle** son el benchmark de precio justo (margen ~2-3%)
- Usar **Power Method** para quitar vig de Pinnacle y obtener probabilidad de referencia

### 5.4 Calibración de Probabilidades

| Método | Datos necesarios | Ventaja |
|--------|-----------------|---------|
| **Platt Scaling** | 100-500 muestras | Robusto, bajo overfitting |
| **Isotonic Regression** | 500+ muestras | Flexible, corrige patrones complejos |
| **Temperature Scaling** | 100-500 (NN) | Simple para redes neuronales |

**Evidencia**: Calibración con isotonic regression convirtió -8.5% ROI en +32.5% ROI en La Liga 2024-25.

### 5.5 Gestión de Bankroll — Kelly Criterion

```
f* = (p × d - 1) / (d - 1)
```

- **Full Kelly**: Máximo crecimiento, varianza extrema
- **Half Kelly** (recomendado): ~75% del crecimiento con ~50% de varianza
- **Quarter Kelly**: Para modelos no validados

### 5.6 Closing Line Value (CLV)

Métrica más importante para determinar si un modelo tiene edge real.

- CLV > 2% sostenido en 200-500 apuestas = edge genuino
- CLV < 0% = EV negativo a largo plazo
- Benchmark: Pinnacle closing odds sin vig

---

## 6. Herramientas y Sistemas Existentes

### 6.1 Proyectos Open-Source Destacados

| Proyecto | Stack | Accuracy/ROI Reportado |
|----------|-------|----------------------|
| **ProphitBet** (~498⭐) | Python, DNN, Random Forest, Optuna | Múltiples modelos con visualización |
| **FootballGPT** | XGBoost + LSTM, PyTorch | 58-61% win rate, ROI +11-15% |
| **Match Oracle** | FastAPI, React, Docker | 38K partidos, 27 features, 10 ligas |
| **Soca-Scores** | Feast, MLflow, Streamlit | Pipeline MLOps completo |
| **Sport-suite** | LightGBM, TimescaleDB, Airflow, FastAPI | 134 features, 11 APIs odds |
| **EPL Predictor** | Spark, Kafka, MLflow, Kubernetes | Big data pipeline |

### 6.2 Plataformas SaaS

| Plataforma | Precio | Cobertura | Modelo |
|------------|--------|-----------|--------|
| **Forebet** | Gratis | 1200+ ligas | Algoritmo matemático propietario |
| **SoccerPunter** | Gratis + Platinum | 500+ competiciones | Estadístico + comunidad |
| **PredictBet** | Gratuito | Comunidad | Votación colectiva |
| **Windrawwin** | Gratuito | Múltiple ligas | Estadístico + tipsters |

### 6.3 Papers Académicos Clave

| Paper | Año | Aporte |
|-------|-----|--------|
| Maher (1982) | 1982 | Poisson independiente fundacional |
| Dixon & Coles | 1997 | Bivariate Poisson + τ correction + time decay |
| Karlis & Ntzoufras | 2003 | Poisson bivariante con covarianza |
| Koopman & Lit | 2012 | Dynamic Bivariate Poisson (state space) |
| Bunker & Susnjak | 2022 | Taxonomía completa, JAIR |
| Yeung et al. | 2023 | CatBoost + pi-ratings SOTA |
| HIGFormer | 2025 | Graph Transformer, KDD 2025 |

---

## 7. Validación Competitiva: Plugins WordPress de Predicciones

### El mercado actual de WordPress

| Tipo | Plugins | Qué hacen |
|------|---------|-----------|
| **Pools de pronósticos** (gamificación) | Football Pool (800+), World Cup Predictor (70+), JoomSport (80+), Football Predictor (10+) | Usuarios ingresan manualmente sus pronósticos y compiten en rankings. NO generan predicciones automáticas. |
| **Algoritmo de predicción** (nuestro tipo) | GoalGorithm (Poisson + xG, 5 ligas), AnWP AI Writer (OpenAI API) | Generan predicciones automáticas con modelos matemáticos o IA. |
| **CMS de tips** | Football Daily Predictor Pro ($) | El admin ingresa tips manualmente. Sin motor de predicción. |
| **Plataformas externas** | Predizo, KiqIQ, Football Intelligence AI, SportBot AI | Potentes modelos (XGBoost, Poisson) pero NO son plugins WordPress. Son webs externas. |

### Nuestro competidor directo: GoalGorithm

El único plugin WordPress gratuito que genera predicciones con un modelo. Creado en 2026 por tohoanganhai.

| Aspecto | GoalGorithm | Nuestra propuesta |
|---------|-------------|-------------------|
| **Modelo** | Poisson básico (xG de Understat) | XGBoost/CatBoost + Regresión Logística (ensemble) |
| **Calibración** | ❌ No calibra | ✅ Isotonic Regression |
| **Ligas** | Solo Top 5 europeas (Premier, La Liga, Serie A, Bundesliga, Ligue 1) | Ilimitadas: cualquier liga + selecciones + Mundiales |
| **Fuentes** | Solo Understat | soccerdata (FBref/Understat/ClubElo/ESPN) + football-data.co.uk + API-Football Free |
| **Features** | Attack Strength + Defense Strength (2 features) | ELO + pi-ratings + rolling averages + forma + H2H + fatiga + odds benchmark |
| **Actualización** | Bajo demanda (shortcode llama API) | Automática vía GitHub Actions (cron diario) |
| **Value detection** | ❌ No | ✅ Compara predicciones vs odds del mercado |
| **Cobertura selecciones** | ❌ No | ✅ Sí, vía Elo ratings (Paraguay, selecciones sin Europa) |
| **Plugin WordPress** | ✅ Sí, PHP puro (modelo incluido) | ✅ Sí, PHP puro (consume JSON de gh-pages) |
| **Costo** | $0 | $0 |

### El gap que nadie cubre

**En todo el ecosistema WordPress, no existe un plugin gratuito que:**
1. Use **XGBoost/CatBoost** (gradient boosting, estado del arte) en vez de Poisson básico
2. **Calibre probabilidades** para que sean precisas y accionables
3. Cubra **ligas no europeas** (Sudamérica, África, Asia, selecciones)
4. Incorpore **odds reales del mercado** para detección de value
5. Se **actualice automáticamente** sin intervención manual (pipeline CI/CD)

**Nuestra ventaja**: Combinamos un motor de predicción ELO con un pipeline autónomo (GitHub Actions) y lo servimos a WordPress de forma simple (JSON → shortcode). Todo gratis, para uso personal.

---

## 8. Arquitectura de Sistema Recomendada

```
┌─────────────────────────────────────────────────────────────┐
│              REPOSITORIO DE GITHUB                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  .github/workflows/predictions.yml (el orquestador)  │   │
│  │  # Se ejecuta con cron: "0 6 * * *" (diario 6 AM)   │   │
│  │  # También se puede trigger manual desde la UI       │   │
│  └──────────────────────────────────────────────────────┘   │
│         ↓                                                    │
│  ┌────────────────┐   ┌──────────────┐   ┌──────────────┐  │
│  │ scripts/       │   │ features/    │   │ models/      │  │
│  │ fetch_data.py  │ → │ generate_    │ → │ train.py     │  │
│  │ parse_data.py  │   │ features.py  │   │ predict.py   │  │
│  └────────────────┘   └──────────────┘   └──────────────┘  │
│                                              ↓              │
│                                       ┌──────────────┐     │
│                                       │ predictions/  │     │
│                                       │ predicciones  │     │
│                                       │ .json         │     │
│                                       └──────────────┘     │
└────────────────────────────────────────────────────────────┘
                           │
                           │ JSON se despliega a gh-pages
                           ▼
┌─────────────────────────────────────────────────────────────┐
│   WORDPRESS PLUGIN                                           │
│   https://github.com/tuuser/tuproyecto/blob/gh-pages/...     │
└─────────────────────────────────────────────────────────────┘
```

### Pipeline Completo (todo vive en GitHub Actions)

#### Fase 1: Data Ingestion
- **Orquestación**: GitHub Actions (workflow YAML con trigger schedule + manual)
- **Fuentes primarias**: football-data.co.uk (resultados + odds), API-Football (estructurado), soccerdata (scraping FBref/Understat)
- **Frecuencia**: Diaria (workflow cron). También se puede ejecutar manualmente desde la UI de GitHub
- **Formato**: Scripts Python en `scripts/` que descargan CSVs, llaman APIs, scrapean

#### Fase 2: Storage
- **Almacenamiento**: Archivos CSV/Parquet dentro del repo o como artifact de Actions
- **Cache**: GitHub Actions cache para datasets pesados
- **Esquema**: Los scripts de Python leen, limpian y guardan datos procesados

#### Fase 3: Feature Engineering
- **Herramientas**: pandas, numpy, scikit-learn (todo Python, sin dbt ni Feast — se evita complejidad innecesaria)
- **Features a generar**:
  - ELO ratings actualizados tras cada partido
  - Rolling averages (3, 5, 10 partidos) de goles F/C
  - Forma reciente (puntos últimos 5 partidos)
  - Pi-ratings (ataque/defensa separados L/V)
  - Head-to-head histórico
  - Días de descanso, distancia viaje
  - xG acumulado (si disponible)
  - Cuotas de apuestas con vig removido (benchmark)

#### Fase 4: Model Training
- **Experiment tracking**: MLflow logging a archivos locales (dentro del repo)
- **Modelo primario**: XGBoost/CatBoost con rating features
- **Modelo secundario**: Regresión Logística (baseline calibrada)
- **Validación**: Walk-forward validation (TimeSeriesSplit)
- **Calibración**: Isotonic Regression (500+ muestras) o Platt Scaling
- **Output**: Probabilidades 1X2 calibradas en JSON

#### Fase 5: Publicación
- El workflow genera `predictions/predicciones.json`
- Se despliega a `gh-pages` para que WordPress lo consuma vía URL pública
- Sin API propia, sin servidor — solo un JSON estático servido por GitHub Pages

#### Fase 6: Monitoreo
- **Model drift**: Script que calcula PSI entre features de train y últimas predicciones
- **Performance**: Brier Score, Log Loss calculados al final de cada workflow
- **Auto-rollback**: El workflow compara métricas vs la última versión aceptada; si empeoran, no publica el nuevo JSON
- **Alerting**: Notificaciones vía email de GitHub Actions si falla el workflow

---

## 9. MLOps y Buenas Prácticas

### 9.0 Skills de Presupuesto Cero Disponibles

El proyecto `30 Dias/last30days-skill/SKILL_FREE.md` (y sus copias en `Web Pulso Paraguay/`) contiene una **metodología validada de 4 fases para investigación sin depender de APIs de pago**:

1. **Research** — Uso de operadores `site:` en search web, extracción de Reddit/X/YouTube/HN/Bluesky
2. **Strategy** — Identificación de ángulos, selección de tono, detección de idioma
3. **Generation** — Plantillas multicanal (Twitter, LinkedIn, Instagram)
4. **QC** — Verificación contra alucinaciones, sin pedir logins, 100% anónimo

Esta skill es directamente aplicable para la fase de monitoreo de tendencias y análisis de conversación sobre fútbol.

### Estrategia de Retraining (sobre GitHub Actions)

| Tipo | Trigger | Descripción |
|------|---------|-------------|
| **Diario** | Cron `0 6 * * *` | Workflow morning: extrae resultados de ayer, reentrena, genera predicciones |
| **Manual** | `workflow_dispatch` | Desde la UI de GitHub, ejecutar cuando hay una fecha importante (Mundial, clásicos) |
| **Por drift** | Script en workflow | Si el script de drift detection encuentra PSI > 0.25, fuerza retrain completo |

### Model Versioning (Git + MLflow)

- **Git**: Cada commit es un snapshot del código + features + pipeline. Las predicciones publicadas quedan versionadas por commit.
- **MLflow**: Logging a `mlruns/` dentro del repo (sin servidor externo). Cada workflow registra params, métricas, y paths de modelos.
- **Promotion gates**: El workflow compara Brier Score del modelo nuevo vs el actual. Si el nuevo es peor, no publica.

### Monitoring de Drift (Scripts Python en Actions)

| Tipo | Detección | Acción |
|------|-----------|--------|
| Data drift | PSI entre features de entrenamiento y nuevas | Si PSI > 0.25, forzar retrain |
| Performance | Brier Score, Log Loss en últimas N predicciones | Si empeora > 5%, no publicar JSON |
| Labelshift | Distribución de resultados reales vs esperados | Alerta en logs del workflow |

### Anti-Leakage Checklist
- [ ] Split cronológico (NUNCA aleatorio)
- [ ] Rolling window hacia atrás (solo datos disponibles)
- [ ] Normalización intra-ventana de entrenamiento
- [ ] Cálculo de features secuencial (sin mirar futuro)
- [ ] Embargo window entre train/test
- [ ] Validación en temporada completa hold-out

---

## 10. Stack Tecnológico Recomendado

| Capa | Tecnología | Por qué |
|------|-----------|---------|
| Orquestación | **GitHub Actions** | Único orquestador. Cron diario + trigger manual. No necesita Airflow |
| Repositorio | **GitHub** | Código, modelos, features, datasets pequeños, documentación |
| Almacenamiento | **CSV/Parquet + Git LFS** | Datos se guardan como archivos dentro del repo. Sin base de datos |
| Cache | **GitHub Actions Cache** | Datasets pesados cacheados entre workflows |
| Features | **pandas + numpy** | Sin dbt, sin Feast — scripts Python directos |
| Modelo principal | **XGBoost / CatBoost** | State-of-the-art en datos tabulares |
| Baseline | **scikit-learn (Regresión Logística)** | Referencia de calibración |
| Deep Learning | **PyTorch (LSTM opcional)** | Solo si se usan secuencias de odds |
| Calibración | **scikit-learn (Isotonic Regression)** | Probabilidades calibradas |
| Experimentación | **MLflow (logging a archivos)** | Sin servidor, todo en el repo |
| Publicación JSON | **GitHub Pages (gh-pages)** | URL pública estática sin servidor |
| Plugin WordPress | **PHP + shortcode** | Consume JSON desde gh-pages |
| Monitoreo | **Scripts Python en Actions** | Drift, PSI, Brier Score calculados en cada ejecución |

### Validación de Presupuesto CERO

| Recurso | Tecnología | Costo real | Tarjeta |
|---------|-----------|-----------|---------|
| Repositorio | GitHub (público) | $0 | No |
| CI/CD | GitHub Actions (repo público = ilimitado) | $0 | No |
| Hosting JSON | GitHub Pages | $0 | No |
| Almacenamiento | GitHub + LFS (1GB gratis) | $0 | No |
| Cómputo | GitHub Actions runner | $0 | No |
| Cache | GitHub Actions Cache | $0 | No |
| Modelos | XGBoost, scikit-learn, PyTorch | $0 (open-source) | No |
| Datos | soccerdata, football-data.co.uk, API-Football Free | $0 | No |
| Plugin | WordPress (PHP puro) | $0 | No |

**Stack de datos gratuito definitivo (v1.0: Mundial 2026):**
- `eloratings.net/World.tsv` (World Football Elo Ratings, scraping) — $0 ✅ FUNCIONA
- `data/fixtures_wc2026.json` (104 fixtures hardcodeados del calendario) — $0 ✅ FUNCIONA
- `football-data.co.uk` (resultados históricos + odds, CSV) — $0 🔒 Post-v1.0
- ~~`API-Football Free` (100 req/día, primary) — season=2026 NO disponible en free~~ ❌
- ~~`soccerdata.FBref` (scraping FBref, fallback 1) — WC 2026 no disponible aún~~ ❌
- ~~`soccerdata.ClubElo` (ELO ratings de selecciones) — solo clubes~~ ❌
- ~~`football-data.org` (10 req/min, fallback 2) — sin Mundial en free~~ ❌

**Pendientes para v2.0 (post-Mundial):**
- `soccerdata` (FBref/Understat/ClubElo para ligas regulares)
- `StatsBomb Open Data` (eventos detallados)
- `mplsoccer` (visualización)
- `OpenLigaDB` (Bundesliga sin API key)

**Cómputo**: GitHub Actions runner (2 CPUs, 7GB RAM). Para entrenamientos locales grandes: Google Colab (GPU gratis).

---

## 11. Referencias

### URLs Clave por Categoría

**Modelos Estadísticos**
- Dixon-Coles explicado: https://exprysm.com/insights/methodology/dixon-coles-model.html
- World Football Elo: https://www.eloratings.net/about
- Comparativa de modelos: https://pena.lt/y/2025/03/10/which-model-should-you-use-to-predict-football-matches
- Guía R modelos: https://www.r-bloggers.com/2026/02/football-betting-model-in-r-step-by-step-guide-2026/

**ML y Feature Engineering**
- CatBoost + pi-ratings SOTA: https://arxiv.org/abs/2309.14807
- Data-driven prediction: https://link.springer.com/article/10.1186/s40537-024-01008-2
- Feature engineering + calibración: https://www.foresportia.com/en/blog/technical-note-2-ai-football-prediction-model.html
- ELO Ratings: https://exprysm.com/insights/methodology/elo-ratings-football.html
- Brier Score: https://www.oddsaccuracy.com/research/what_is_brier_score.html
- CS230 Stanford (LSTM): https://cs230.stanford.edu/projects_spring_2020/reports/38854780.pdf

**APIs y Datos**
- football-data.org: https://www.football-data.org/
- API-Football: https://www.api-football.com/
- soccerdata (PyPI): https://pypi.org/project/soccerdata/
- football-data.co.uk: https://www.football-data.co.uk/
- StatsBomb Open Data: https://github.com/statsbomb/open-data
- Club Football Match Data: https://github.com/xgabora/Club-Football-Match-Data-2000-2025

**Apuestas y Odds**
- Devigging guide: https://comparenbet.org/guide-devigging-methods
- Pinnacle wisdom: https://www.football-data.co.uk/blog/pinnacle_wisdom.php
- CLV guide: https://probwin.com/guides/closing-line-value-clv-ultimate-metric-measure-your-edge/
- Kelly Criterion: https://www.bettingexpert.com/academy/advanced-betting-theory/kelly-criterion-explained
- Model calibration: https://exprysm.com/insights/methodology/model-calibration.html
- Favorite-longshot bias: https://statsbet.org/blog/prediction-market-odds-efficiency

**Herramientas y Proyectos**
- ProphitBet: https://github.com/kochlisGit/ProphitBet-Soccer-Bets-Predictor
- FootballGPT: https://github.com/FootballGPT/football-model
- soccerdata GitHub: https://github.com/probberechts/soccerdata
- Automated Sports Prediction: https://trainmyai.net/automated-sports-prediction-pipelines-from-data-sourcing-to-

**Papers**
- Dixon & Coles (1997): https://www.ajbuckeconbikesail.net/wkpapers/Airports/MVPoisson/soccer_betting.pdf
- Koopman & Lit (2012): https://papers.tinbergen.nl/12099.pdf
- Bunker & Susnjak Taxonomía: https://www.jair.org/index.php/jair/article/download/13509/26786/

---

## 12. Validación de Viabilidad 2026 — Investigación Completa

> Investigación realizada el 1 de junio de 2026 mediante 7 frentes paralelos (web research + agentes de investigación profundos + skills de seguridad). El objetivo fue determinar si el proyecto es viable técnica, comercial y de seguridad antes de escribir código.

### 12.1 Fuentes de Datos Gratuitas 2026 — Análisis Detallado

#### API-Football (api-football.com) — Recomendado como fuente primaria

| Aspecto | Detalle |
|---------|---------|
| **Plan gratis** | 100 requests/día, 10 req/minuto |
| **Tarjeta de crédito** | No requiere |
| **Endpoints incluidos** | TODOS: fixtures, standings, teams, H2H, odds (pre-match + in-play), statistics, predictions, lineups, injuries, top scorers, transfers, sidelined, countries, leagues, seasons |
| **Cobertura** | 800+ ligas (free: historial limitado a temporadas recientes) |
| **Actualización** | Live scores cada 15 segundos |
| **Upgrade path** | Pro $19/mes (7,500 req/día), Ultra $29/mes (75,000), Mega $39/mes (150,000) |
| **Autenticación** | API key por header |

**Plan de consumo diario para nuestro pipeline:**
| Operación | Requests | Frecuencia |
|-----------|----------|------------|
| Fixtures próximos 7 días x 10 ligas | 10 | 1 vez/día |
| Standings x 10 ligas | 10 | 1 vez/día |
| Team statistics (top partidos) | 30-40 | 1 vez/día |
| H2H para partidos destacados | 10-15 | 1 vez/día |
| **Total estimado** | **60-75 req/día** | ✅ Dentro del límite |

**Conclusión**: 100 req/día alcanza para ~10 ligas optimizando requests. Para producción con todas las ligas, el plan Pro ($19/mes) es el upgrade natural cuando haya revenue.

#### Mundial 2026 en API-Football (league=1, season=2026)

> ⚠️ **ADVERTENCIA VERIFICADA**: La guía oficial de API-Football (abril 2026) describe cobertura completa del Mundial. **PERO EL FREE TIER NO TIENE ACCESO A SEASON=2026.** Error real: `Free plans do not have access to this season, try from 2022 to 2024.` Verificado el 1 de junio de 2026.

La API tiene los datos en planes de pago. El free tier solo cubre temporadas 2022-2024.

**Solución implementada**: Los fixtures se cargan desde `data/fixtures_wc2026.json` (104 partidos hardcodeados del calendario oficial). Las predicciones se generan con World Football Elo Ratings (eloratings.net) en vez de API-Football.

| Aspecto | Detalle |
|---------|---------|
| **League ID** | 1 |
| **Season** | 2026 (calendario, no 2025/2026) |
| **Formato** | 48 selecciones, 12 grupos de 4, 104 partidos |
| **Fechas** | 11 junio - 19 julio 2026 |
| **Sedes** | Canadá, México, Estados Unidos (16 estadios) |
| **Datos disponibles** | En planes de pago. Free tier: ❌ |
| **Alternativa real** | `data/fixtures_wc2026.json` + eloratings.net |

**Endpoints (documentados para referencia, pero NO disponibles en free tier):**
| Endpoint | Parámetros | Disponible en free |
|----------|-----------|-------------------|
| `/fixtures?league=1&season=2026` | league=1, season=2026 | ❌ |
| `/standings?league=1&season=2026` | - | ❌ |
| `/predictions?fixture=FIXTURE_ID` | fixture ID | ❌ |
| `/odds?fixture=FIXTURE_ID` | fixture ID | ❌ |

**Convención de season parameter**: 
- Torneos por año calendario (Mundial, MLS, J.League): `season=2026`
- Torneos por temporada (Premier 2025/2026): `season=2025` (año de inicio)

**Implicación**: Para v1.0 (Mundial 2026), el pipeline usa datos hardcodeados + Elo en vez de API-Football. Para ligas regulares (v2.0), API-Football free tier SÍ funciona con seasons 2022-2024.

#### Fuentes Secundarias (complementarias, sin límite diario)

| Fuente | Costo | Cobertura | Uso en el pipeline |
|--------|-------|-----------|-------------------|
| **football-data.co.uk** | $0 | 22 divisiones, odds 10+ casas desde 1993 | Datos históricos para entrenamiento |
| **Understat** (vía soccerdata) | $0 (scraping) | Top 5 europeas, xG por disparo | Feature engineering (xG) |
| **football-data.org** | $0 | 12 competiciones, 10 req/min | Fuente de respaldo |
| **ClubElo** (vía soccerdata) | $0 | ELO ratings históricos | Feature de fuerza de equipos |
| **StatsBomb Open Data** | $0 | Eventos detallados, competiciones selectas | Investigación y validación |

### 12.2 GitHub Actions — Capacidad para ML Training (2026)

#### Límites del Runner Gratuito (Standard)

| Recurso | Especificación |
|---------|---------------|
| CPU | 2 cores (Intel Xeon Platinum 8370C) |
| RAM | 7 GB |
| SSD | 14 GB |
| Timeout máximo | 6 horas por job |
| Red | ~100 Mbps |

#### Costo 2026

| Tipo de repo | Minutos gratis | Costo adicional |
|-------------|---------------|-----------------|
| **Público** | **Ilimitados (gratis)** | $0 |
| Privado (Free plan) | 2,000 min/mes | $0.008/min Linux |

**Estrategia**: El repositorio de datos/pipeline será **público** — esto hace que TODO el cómputo sea $0. El plugin WordPress (que contiene el código pago) puede estar en repositorio privado separado.

#### Viabilidad para Entrenar XGBoost/CatBoost

| Tarea | Tiempo estimado | RAM requerida |
|-------|-----------------|---------------|
| Feature engineering (50K partidos) | 5-10 min | ~2 GB |
| Entrenar XGBoost (50K filas, 50 features) | 15-30 min | ~3 GB |
| Entrenar CatBoost (50K filas, 50 features) | 20-45 min | ~4 GB |
| Hiperparámetros (Optuna, 50 trials) | 45-90 min | ~4 GB |
| Generar predicciones (100 partidos) | < 1 min | ~500 MB |
| **Pipeline completo** | **~60-120 min** | ✅ Cabe en 7 GB |

**Conclusión**: GitHub Actions puede entrenar modelos XGBoost/CatBoost sin problemas. Sin GPU, pero no se necesita — gradient boosting en CPU es suficiente.

### 12.3 Estándares de Seguridad WordPress Plugins 2026

#### WordPress.org Plugin Guidelines Relevantes

| # | Regla | Implicación |
|---|-------|-------------|
| 1 | GPL-compatible license | Nuestro plugin usará GPLv2+ (compatible con WordPress) |
| 4 | Código human-readable | Sin ofuscación. PHP puro con namespaces |
| 5 | Uso personal | Plugin no publicado en WP.org, solo uso en nuestro sitio |
| 6 | SaaS sí permitido | Consume JSON remoto → es SaaS, permitido |
| 7 | No tracking | Sin tracking de usuarios, sin analytics externos |
| 8 | No código ejecutable vía terceros | Solo consumimos JSON estático de GitHub Pages (seguro) |
| 13 | Usar librerías de WordPress | No incluir jQuery, SimplePie, etc. Usar las de WP |

#### Security Best Practices Checklist (2026)

Cada línea de código del plugin DEBE cumplir:

```
Sanitización de input:
  - [ ] $_GET, $_POST, $_REQUEST pasan por sanitize_text_field(), sanitize_key(), absint()
  - [ ] register_setting() con sanitize_callback
  - [ ] NO acceso directo a superglobales sin sanitizar

Escapado de output:
  - [ ] esc_html(), esc_attr(), esc_url(), wp_kses() en TODA salida al navegador
  - [ ] wp_send_json_success() / wp_send_json_error() para AJAX
  - [ ] NO echo de variables sin escapar

Nonces (CSRF):
  - [ ] wp_nonce_field() en todos los formularios
  - [ ] wp_verify_nonce() o check_admin_referer() en todo estado-cambiante
  - [ ] check_ajax_referer() en handlers AJAX

Capability checks:
  - [ ] current_user_can() en toda operación privilegiada
  - [ ] permission_callback en cada REST route (register_rest_route)
  - [ ] manage_options para páginas de settings

Database:
  - [ ] $wpdb->prepare() en TODAS las queries SQL
  - [ ] Placeholders (%s, %d) en vez de concatenación
  - [ ] Si no usamos custom tables (solo Options API), riesgo mínimo

Protección de archivos:
  - [ ] defined('ABSPATH') || exit; al inicio de cada archivo PHP
  - [ ] index.php vacío en cada directorio
  - [ ] No archivos sueltos .php en root excepto el plugin principal

Headers de seguridad (para el sitio que usa el plugin):
  - [ ] Content-Security-Policy
  - [ ] X-Content-Type-Options: nosniff
  - [ ] X-Frame-Options: SAMEORIGIN
  - [ ] Referrer-Policy: strict-origin-when-cross-origin

Estructura del plugin:
  - [ ] PSR-4 autoloading con Composer
  - [ ] Namespaces (PartidosHoy\Deporte\*)
  - [ ] PHPStan level ≥ 6
  - [ ] WP_DEBUG = true durante desarrollo
  - [ ] No secretos hardcodeados (API keys en wp-config.php o env vars)
```

#### State of WordPress Security 2026 (Patchstack Report)

- **11,334** nuevas vulnerabilidades en ecosistema WP en 2025 (+42% vs 2024)
- **91%** fueron en plugins
- **46%** de vulnerabilidades no recibieron fix antes de divulgación pública
- **Premium components** reciben menos escrutinio = más riesgo (lección: debemos ser aún más rigurosos)
- Atacantes weaponizan vulnerabilidades en **horas**

### 12.5 EU Cyber Resilience Act (CRA) — Referencia

#### ¿Aplica a nuestro proyecto?

**NO.** El plugin es para uso personal en nuestro sitio web. No se vende ni distribuye comercialmente, por lo que CRA no aplica.

#### Buenas prácticas aplicadas (sin obligación CRA)

| Práctica | Estado |
|----------|--------|
| Coordinated Vulnerability Disclosure (CVD) + security.txt | ✅ Implementado |
| Dependabot para actualizaciones de seguridad | ✅ Implementado |
| Nonces, capability checks, sanitize/escape en WordPress | ✅ Implementado |

#### Requisitos para Septiembre 2026

| Requisito | Qué implica | Cómo cumplirlo |
|-----------|-------------|----------------|
| **Vulnerability Disclosure Policy** | Proceso documentado para recibir reportes de seguridad | Publicar security.txt (RFC 9116) en dominio del plugin + policy en sitio web |
| **Security contact** | Punto de contacto designado para investigadores | Email + formulario en sitio web |
| **Respuesta 24-72h** | Responder a vulnerabilidades críticas en 24-72 horas | SLA interno documentado |
| **Separación security patches** | Parches de seguridad separados de features releases | Versionado semántico + changelog claro |
| **Dependency monitoring** | Monitorear vulnerabilidades en librerías de terceros | Dependabot + composer audit + npm audit |
| **SBOM** | Software Bill of Materials (inventario de componentes) | Generar CycloneDX con `cyclonedx-bom` o similar |
| **Incident reporting a ENISA** | Reportar vulnerabilidades activamente explotadas en 24h | Conectarse a plataforma ENISA single reporting |

#### Sanciones por Incumplimiento

- Hasta **€15 millones** o **2.5% del volumen de negocio anual global**
- **Remoción del plugin** si se detectan vulnerabilidades críticas

#### Buenas Noticias

- Uso personal: sin obligaciones CRA, GDPR ni fiscales
- Buenas prácticas de seguridad aplicadas igualmente

#### Costos de Cumplimiento

| Elemento | Costo |
|----------|-------|
| security.txt | $0 (archivo de texto) |
| Vulnerability Disclosure Policy | $0 (template + personalizar) |
| Dependabot + composer audit | $0 (GitHub nativo) |
| SBOM (CycloneDX) | $0 (herramientas open-source) |
| EU Authorized Representative (Dec 2027) | ~€200-500/año (servicio third-party) |
| CE marking | $0 (autodeclaración) |

### 12.6 Validación Comercial y Competitiva

#### Análisis de GoalGorithm (Competidor Directo)

| Aspecto | GoalGorithm (tohoanganhai) | Nuestra propuesta |
|---------|---------------------------|-------------------|
| **Modelo** | Poisson + xG (Understat) | XGBoost/CatBoost + Regresión Logística |
| **Calibración** | ❌ No | ✅ Isotonic Regression |
| **Ligas** | 5 (Premier, La Liga, Serie A, Bundesliga, Ligue 1) | 10+ incluyendo Sudamérica, Asia, selecciones |
| **Fuente datos** | Understat solo | API-Football + football-data.co.uk + soccerdata |
| **Features** | Attack/Defense strength (2) | ELO + pi-ratings + rolling averages + forma + H2H + fatiga + odds |
| **Value detection** | ❌ No | ✅ Contra odds Pinnacle devigged |
| **Frecuencia actualización** | 12h cache | Diaria vía GitHub Actions |
| **MCP Server** | ✅ Sí (MCP para Claude) | ❌ No necesario (es WordPress, no Claude) |
| **Idiomas** | 8 idiomas | 2-3 inicial (ES, EN, PT) |
| **Cobertura selecciones** | ❌ No | ✅ Sí (Paraguay, Conmebol, etc.) |
| **Precio** | $0 (gratis) | $0 (free) + $29/año (premium) |
| **Código** | PHP (modelo incluido en plugin) | Python (modelo en GHA) + PHP (plugin) |

**Diferenciación clave**: ML > Poisson, más ligas (especialmente sudamericanas), calibración, value detection.

#### El Mercado Existe

| Proyecto | Tipo | Precio | Año |
|----------|------|--------|-----|
| **GoalGorithm** | WP Plugin (Poisson) | Free | 2026 |
| **AccaPlanner** | UK betting platform (WordPress + AI + SportMonks) | No revelado | 2026 |
| **World Cup Predictor clone** | WP Plugin (pool de usuarios) | $79 one-time | 2026 |
| **Nuestra propuesta** | WP Plugin (XGBoost, multicobertura) | $29/year | 2026 |

La tendencia 2026 muestra interés real en plugins de predicción con IA/ML para WordPress.

### 12.7 Risk Register

| # | Riesgo | Probabilidad | Impacto | Mitigación |
|---|--------|-------------|---------|------------|
| 1 | API-Football 100 req/día insuficiente | Media | Bajo | No usamos API-Football. Fuente ELO no requiere API. |
| 2 | CRA compliance | Baja | Bajo | Uso personal, sin comercialización. Buenas prácticas aplicadas. |
| 3 | Modelo ELO no preciso | Media | Bajo | ELO clásico da baseline. Mejorable en v2.0 con más datos. |
| 4 | GitHub Actions timeout | Baja | Medio | Pipeline simple (1 script), < 1 minuto de ejecución. |
| 5 | Bandwidth GitHub Pages excedido | Baja | Medio | 100 GB/mes gratis. JSON ~2KB/request. Factor de seguridad: enorme. |
| 6 | eloratings.net cambia formato | Baja | Medio | Scraping de World.tsv. Si cambia, adaptar script. |

### 12.8 Decisión Final: Proyecto VIABLE

```
┌────────────────────────────────────────────────────────────────┐
│                    DECISIÓN DE VALIDACIÓN                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ✅ TÉCNICO: Viable                                            │
│     • GitHub Actions (repo público) → cómputo $0 ilimitado     │
│     • Scraping eloratings.net + fixtures hardcodeados          │
│     • ELO predictor corre en < 10 segundos                      │
│     • JSON estático en gh-pages sin servidor                   │
│                                                                │
│  ✅ SEGURIDAD: Buenas prácticas aplicadas                       │
│     • WordPress: sanitize + escape + nonces + capabilities      │
│     • GitHub: Dependabot, sin credenciales en código            │
│     • Plugin sigue WP Coding Standards                         │
│                                                                │
│  ✅ USO PERSONAL: Sin comercialización                          │
│     • Plugin para nuestro sitio web (partidoshoy.futbol)       │
│     • Sin Freemius, sin ventas, sin WP.org                     │
│     • Sin obligaciones CRA, GDPR, fiscales                     │
│                                                                │
│  ✅ SIN BLOQUERS                                               │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 13. Referencias Agregadas en Validación 2026



### Seguridad WordPress 2026
- Detailed Plugin Guidelines: https://developer.wordpress.org/plugins/wordpress.org/detailed-plugin-guidelines/
- AI-ready Plugin Development Checklist 2026: https://pluginpunch.com/resources/wordpress-plugin-development-expert-tips/
- Plugin Security Best Practices 2026: https://webnotics.org/wordpress-plugin-security-best-practices-2026-protecting-your-custom-code-against-vulnerabilities/
- WordPress Security Auditing: https://keithgreer.dev/wordpress-plugin-security-auditing/
- State of WP Security 2026 (Patchstack): https://patchstack.com/whitepaper/state-of-wordpress-security-in-2026/

### EU Cyber Resilience Act (CRA)
- CRA & WordPress: What Developers Must Do (Sep 2026): https://zerotowp.com/2026-03-21-eu-cyber-resilience-act-wordpress
- Complete CRA Compliance Guide: https://getcraguard.com/blog/cra-compliance-guide
- CRA Guide for Open-Source Vendors (Patchstack): https://patchstack.com/whitepaper/cyber-resilience-act-checklist/
- CRA Implementation (EU Commission): https://digital-strategy.ec.europa.eu/en/factpages/cyber-resilience-act-implementation

### GitHub Actions 2026
- Actions Limits: https://docs.github.com/en/actions/reference/limits
- Pricing Changes 2026: https://github.com/resources/insights/2026-pricing-changes-for-github-actions
- GitHub Blog — Actions 2026: https://github.blog/news-insights/product-news/lets-talk-about-github-actions/

### APIs de Datos
- API-Football Free Plan: https://www.api-football.com/pricing
- API-Football Beginner Guide: https://www.api-football.com/news/post/how-to-get-started-with-api-football-the-complete-beginners-guide
- Bzzoiro Sports Data (BSD): https://sports.bzzoiro.com/free-football-api/

### Competencia
- GoalGorithm Plugin (GitHub): https://github.com/tohoanganhai/goalgorithm-soccer-predictions-bongdanet
- GoalGorithm MCP Server: https://conare.ai/marketplace/mcp/goalgorithm
- AccaPlanner Case Study (2026): https://www.matthewpont.com/2026/04/13/ai-football-betting-platform-wordpress/

---

## 14. Investigación Legal FIFA

> Investigación completada el 1 de junio de 2026 mediante 3 subagentes paralelos (6 subtópicos: marcas FIFA, derechos de datos, gambling, API-Football ToS, precedentes, Paraguay).
> Hallazgos completos en `../research_legal_fifa/` (4 archivos).

### 14.1 Conclusión Principal: Riesgo BAJO si se siguen las reglas

No hay evidencia de que FIFA haya demandado sitios de predicciones (Forebet, PredictZ, SoccerVista). El riesgo legal es manejable con precauciones específicas.

### 14.2 Las 3 Reglas de Oro

| Área | ❌ Prohibido | ✅ Permitido |
|------|-------------|-------------|
| **Branding** | Usar "FIFA", "World Cup", "Mundial" en nombre/descripción/tags del plugin | Branding genérico: "ScoreForge", "MatchPredict", "GoalOracle" |
| **Contenido** | Usar logos de FIFA, selecciones, clubes | Solo texto plano: "Argentina vs Brasil", "World Cup 2026 predictions" como heading descriptivo |
| **Datos** | Vender JSON crudo de API-Football | Usar datos para generar predicciones en el plugin |

FIFA tiene **98+ marcas registradas en US**, **300+ en México** para el Mundial 2026, y ha ganado el **90%** de 500+ casos legales. Pero todas las acciones de FIFA han sido contra **ambush marketing** (empresas que sugieren afiliación oficial), NO contra sitios de predicciones.

### 14.3 Análisis por Área Legal

#### Marcas FIFA
- **"FIFA"**: Marca registrada — no se puede usar en nombre de producto comercial
- **"World Cup"**: Marca registrada en US, Canadá, México y la mayoría de jurisdicciones
- **"World Cup 2026"**: Específicamente registrado por FIFA. No usar en branding
- **Nombres de selecciones**: "Argentina", "Brasil" = nombres de países, no son marcas FIFA. Seguro
- **Nombres de clubes**: Pueden ser marcas de los clubes. Uso descriptivo en predicciones = nominative fair use
- **Derbis**: "El Clásico" (La Liga), "Fla-Flu" (Brasil) pueden ser marcas registradas

#### Derechos de Datos de Fútbol
- **Precedente fundacional**: *NBA v. Motorola (1997)* — los datos deportivos (resultados, estadísticas) son hechos, no copyrightables
- **CJEU confirmó** en *Football Dataco v. Yahoo (2012)* y *Fixtures Marketing v. OPAP (2004)*: los fixture lists no tienen protección sui generis porque la inversión es en *crear* el evento, no en *recolectar* datos preexistentes
- **Riesgo real**: No es FIFA ni copyright — es scraping no autorizado (*Swish Analytics v. OddsJam*, 2024-2025). Nosotros usamos API oficial, no scraping

#### Predictions vs Gambling
- **Prediction-only (nuestro caso)**: No toma stakes, no procesa pagos, no da payouts = **NO es gambling** en ninguna jurisdicción relevante
- **Prediction markets** (Kalshi, Polymarket): Toman stakes + pagan — SÍ son regulados (CFTC en US, UKGC en UK, ilegales en Brasil desde abril 2026)
- **Riesgo real cero** para nuestro modelo de negocio

#### API-Football ToS
- **Sí permite uso comercial** en aplicaciones, websites, fantasy games
- **Prohíbe reventa directa** del JSON crudo a terceros
- **No otorga licencia de publicación** — el usuario debe verificar derechos con ligas/federaciones
- **Betting/fantasy platforms** pueden necesitar licencias adicionales
- **Governing law**: Francesa. Disputas en cortes francesas

#### Precedentes Relevantes
| Caso | Año | Relevancia |
|------|-----|------------|
| NBA v. Motorola/STATS | 1997 | Estadísticas deportivas = hechos, no copyright |
| CBC v. MLB | 2007 | Nombres y stats de jugadores son información pública |
| Football Dataco v. Yahoo (C-604/10) | 2012 | Fixture lists no tienen protección sui generis |
| NCAA v. DraftKings | 2026 | Usar "March Madness" en UI de predicción = riesgo de infracción |
| FIFA v. PUMA | 2022 | FIFA cancela marca de PUMA por "PUMA WORLD CUP" |
| FIFA v. Cencosud | 2013 | FIFA force cease-and-desist por "BRASIL 2014" en promociones |
| Swish Analytics v. OddsJam | 2025 | Scraping de datos deportivos = demanda real |

#### Paraguay — Sin Riesgos Legales Específicos
- No hay leyes que regulen plugins/software específicamente
- Sistema tributario territorial: **0%** sobre ingresos de fuente extranjera
- Sin IVA ni impuestos de ventas (uso personal, no comercial)
- No hay regulación de gambling que afecte predicciones informativas
- Recomendado: registrar RUC en SET y documentar ingresos extranjeros

### 14.4 Cómo lo manejan los competidores (benchmark)

| Sitio/Plugin | Usa "FIFA" o "World Cup"? | Disclaimer legal |
|-------------|--------------------------|-----------------|
| **Forebet** | No en marca. "World Cup" como categoría descriptiva | T&C: "for informational and entertainment purposes only" |
| **SoccerPunter** | No en marca. "World Cup" en URLs descriptivamente | No visible |
| **GoalGorithm** | No en nombre. "Premier League" descriptivamente en shortcode | **NINGUNO** — sin disclaimer, TOS, ni privacy policy |
| **FootballPredictions.com** | No en marca | T&C: "informational and entertainment purposes only" |
| **Nuestra propuesta** | No en marca. "World Cup 2026" como heading descriptivo | ✅ Tendremos disclaimer + TOS + privacy policy |

### 14.5 Checklist de Protección Legal + Branding

- [ ] **Nombre del producto**: "Partidos Hoy - Pronósticos de Fútbol" (sin "FIFA", "World Cup", "Mundial", "Copa del Mundo")
- [ ] **Nombre del plugin (slug WordPress)**: `partidos-hoy` (sin marcas registradas)
- [ ] **Descripción**: "Pronósticos de fútbol con machine learning" (sin marcas FIFA)
- [ ] **Tags en WordPress.org**: sin `fifa`, `world cup`, `mundial`, `copa del mundo`
- [ ] **Dominio**: partidoshoy.futbol (seguro, no contiene marcas registradas)

- [ ] **Nombre del plugin**: sin "FIFA", "World Cup", "Mundial", o cualquier marca registrada de FIFA
- [ ] **Descripción**: sin marcas FIFA ("football predictions", "soccer analytics" OK)
- [ ] **Tags en WordPress.org**: sin `fifa`, `world cup`, `mundial`
- [ ] **Disclaimers**: "For informational and entertainment purposes only" + "no guarantee of accuracy"
- [ ] **Términos y Condiciones**: 18+ age restriction, "as is" warranty disclaimer, governing law clause
- [ ] **Privacy Policy**: GDPR compliance, data collection disclosure
- [ ] **Responsible Gambling notice**: link a GambleAware o equivalente
- [ ] **Logos**: NO usar logos de FIFA, federaciones, selecciones, o clubes
- [ ] **Datos**: NO vender JSON crudo de API-Football — solo predicciones derivadas
- [ ] **API-Football ToS**: Cumplir con términos de uso comercial (+ verificar publicación rights con federaciones si aplica)
- [ ] **Texto legal precautorio**: "Not affiliated with FIFA or any football federation" (footer del plugin/shortcode)
- [ ] **Dominio/URL**: NO comprar dominios como `fifapredictor.com` o `worldcuppredictions.pro`
- [ ] **Hashtags**: No usar #FIFA, #FIFAWorldCup, #FIFAWorldCup2026 en marketing. Usar #WorldCupPredictions es aceptable

### 14.6 Referencias Legales

- FIFA IP Guidelines v2.0 (Jun 2024): https://www.fifadigitalarchive.com/welcome_old/markrequest/Common/documents/FIFA_World_Cup_26tm_IP_Guidelines_English_version_2_0_June_2024.pdf
- The IP Center — Navigating FIFA's World Cup Trademarks: https://theipcenter.com/2024/05/navigating-fifas-world-cup-trademarks/
- WeirFoulds — Don't Get Red-Carded (2026): https://www.weirfoulds.com/dont-get-red-carded-the-fifa-compliance-rules-that-could-derail-your-fifa-world-cup-2026-marketing
- Mondaq — Road To The 2026 World Cup: IP Risks in Mexico: https://webiis05.mondaq.com/mexico/trademark/1750778/road-to-the-2026-world-cup-intellectual-property-risks-and-legal-considerations
- Mondaq — March Madness, Sportsbooks, and Nominative Fair Use (2026): https://www.mondaq.com/unitedstates/trademark/1769934/march-madness-sportsbooks-and-nominative-fair-use-what-the-ncaa-v-draftkings-lawsuit-really-signals
- Dentons — How to avoid IP risks when using sports data: https://www.dentons.com/en/insights/articles/2021/september/30/how-to-avoid-ip-risks-when-using-sports-data-and-statistics-in-your-business
- API-Football Terms of Service: https://www.api-football.com/terms
- EU Database Directive (96/9/EC): https://eur-lex.europa.eu/eli/dir/1996/9/oj
- Football Dataco v. Yahoo (C-604/10): http://mansfield.bailii.org/eu/cases/EUECJ/2012/C60410.html
- BHB v. William Hill (C-203/02): https://www.bailii.org/eu/cases/EUECJ/2004/C20302.html
- Paraguay VAT on Digital Services: https://www.vatcalc.com/paraguay/paraguay-vat-and-inr-on-foreign-digital-services

---

*Documento actualizado el 1 de junio de 2026 con validación completa de viabilidad técnica, seguridad, legal y comercial. Investigación multi-frente con 7 fuentes paralelas + 2 skills instalados (security-review, wordpress-plugin-core) + 1 investigación legal FIFA.*
