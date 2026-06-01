# Investigación: Herramientas y Sistemas de Predicción de Fútbol

> Fecha: 31/05/2026 | Propósito: Base para diseño de sistema propio de predicción

---

## 1. Proyectos Open-Source en GitHub

### Proyectos Destacados

| Proyecto | Estrellas | Stack | Descripción |
|----------|-----------|-------|-------------|
| [ProphitBet](https://github.com/kochlisGit/ProphitBet-Soccer-Bets-Predictor) | ~498 ⭐ | Python, DNN, Random Forest, Optuna | App completa con descarga de datos históricos, múltiples modelos (DNN con Attention, Random Forest, SVM), visualizaciones y predicción de próximos partidos. Licencia MIT. |
| [FootballGPT](https://github.com/FootballGPT/football-model) | ~5 ⭐ | Python, XGBoost + LSTM, PyTorch | Motor de predicción con ensemble XGBoost + LSTM + Bayesian updater. 500K+ eventos, 8 ligas, 11 temporadas. Reporta 58-61% win rate, ROI +11-15%. Incluye modelo xG, PPDA, ELO, form decay. |
| [Match Oracle (ssupshub)](https://github.com/ssupshub/football-prediction-model) | ~0 ⭐ | Python, FastAPI, React, Docker | Backend FastAPI + frontend React. 38K+ partidos, 27 features, 10 ligas. Logistic Regression, Random Forest, XGBoost. Calibración isotónica. |
| [Tip Genius](https://github.com/thg-muc/tip-genius) | ~7 ⭐ | Python, LLMs (Mistral, GPT, DeepSeek), Vercel | Enfoque novedoso: usa LLMs + odds data para predicciones. Serverless en Vercel, GitHub Actions para automatización. UI responsive con Tailwind. |
| [all_leagues_prediction](https://github.com/dagbolade/all_leagues-_prediction) | ~15 ⭐ | Python, Flask, HTML/JS | Plataforma multi-liga con ingesta de datos, entrenamiento y visualizaciones. Hacktoberfest, contribuciones abiertas. |
| [Soca-Scores](https://github.com/Jnyambok/Soca-Scores) | ~0 ⭐ | Python, scikit-learn, Feast, MLflow, Streamlit | Pipeline MLOps completo: feature store (Feast), model registry (MLflow), dashboard Streamlit. CI/CD con GitHub Actions. |
| [Ballistics](https://github.com/ayoabass777/ballistics) | ~0 ⭐ | Python, Airflow, dbt, Postgres, S3 | Pipeline analítico: Airflow orquesta extracción → S3 → Postgres → dbt transforms. Streaks, H2H, performance metrics. |
| [Sport-suite](https://github.com/untitled114/Sport-suite) | ~0 ⭐ | Python, LightGBM, TimescaleDB, Airflow, FastAPI | Producción: 134 features, 11 APIs de casas de apuestas, stacked LightGBM, drift detection, auto-rollback. Discord bot. |
| [EPL Predictor (oussamaelmessaoudi)](https://github.com/oussamaelmessaoudi/EPL-Predictor-Forecasting-with-Machine-Learning) | ~0 ⭐ | Spark, Kafka, MLflow, FastAPI, React | Big data: Spark para procesamiento distribuido, Kafka para streaming, Delta Lake, Kubernetes. |
| [Football Data Pipeline (KwachuQ)](https://github.com/KwachuQ/Football-data-pipeline) | ~0 ⭐ | Airflow, dbt, MinIO, Postgres, Metabase | Arquitectura medallion (Bronze→Silver→Gold). 13 martes analíticos. BI con Metabase. |

### Stack Tecnológico Común

- **Lenguaje**: Python (dominante, ~95% de proyectos)
- **Modelos**: XGBoost, Random Forest, Logistic Regression, LightGBM, LSTM
- **Features típicas**: ELO rating, form points, average goals scored/conceded, rest days, xG, posesión, H2H
- **Frontend**: Streamlit, React, Flask
- **Despliegue**: Docker, Vercel, Render, AWS EC2

---

## 2. Papers Académicos Relevantes

### Modelos Estadísticos Clásicos

| Paper | Año | Enfoque | Link |
|-------|-----|---------|------|
| **Dixon & Coles** - "Modelling Association Football Scores and Inefficiencies in the Football Betting Market" | 1997 | Bivariate Poisson con parámetro de dependencia para scores 0-0, 1-0, 0-1, 1-1. Weighting function para dar más peso a partidos recientes. | [PDF](https://www.ajbuckeconbikesail.net/wkpapers/Airports/MVPoisson/soccer_betting.pdf) |
| **Maher (1982)** | 1982 | Double Poisson independence model - pionero | - |
| **Karlis & Ntzoufras (2003)** | 2003 | Bivariate Poisson distribution con modelado explícito de λ3 (covarianza) | - |
| **Koopman & Lit (2012)** | 2012 | Dynamic Bivariate Poisson con attack/defense strengths que varían en el tiempo (state space + importance sampling). Positive return over bookmaker odds. | [Tinbergen Institute](https://papers.tinbergen.nl/12099.pdf) |
| **Crowder, Dixon, Ledford & Robinson (2002)** | 2002 | Dynamic modelling via state space + MCMC para 92 equipos ingleses | [Wiley](https://rss.onlinelibrary.wiley.com/doi/10.1111/1467-9884.00308) |
| **Groll et al. (2016)** | 2016 | Bivariate Poisson + boosting para UEFA Euro 2016 | [LMU](https://epub.ub.uni-muenchen.de/29028/1/TR_EM2016.pdf) |

### Deep Learning y Nuevos Enfoques (2023-2025)

| Paper | Año | Enfoque | Accuracy |
|-------|-----|---------|----------|
| **HIGFormer** (KDD 2025) | 2025 | Graph Transformer con interacciones jugador-equipo. Dos streams: Player Interaction Network + Team Interaction Network + Match Comparison Transformer. | 52.19% avg, 68.25% loss prediction |
| **FootballNet** (ACM 2025) | 2025 | CNN para predicción. Comparado con Logistic Regression, XGBoost, MLP, Random Forest, SVM | ~95% accuracy (con features limitadas) |
| **Quantum Neural Network** (Nature Scientific Reports 2025) | 2025 | QNN basado en deep learning. Datos 2008-2022 de European Soccer Database | 20.5%+ mejora sobre CNN/LSTM/Transformer |
| **Siamese Neural Networks** (ICAART 2025) | 2025 | Time series + Siamese Networks para capturar dinámicas temporales entre equipos | ~59% overall accuracy |
| **Graph-based Passing Networks** (Journal of Big Data 2025) | 2025 | Grafos de pases para predecir durante el partido (45', 60', 75', 90') | 5-20% mejora sobre baselines |
| **Event Data + XGBoost** (ISSC 2024) | 2024 | StatsBomb event data, features de ubicación, Random Forest/XGBoost/SVM | 65.8% SVM, 64.4% XGBoost |
| **MLP + PCA** (Frontiers 2025) | 2025 | PCA para reducción de dimensionalidad + MLP. 22 technical statistics indicators | 86.7% |
| **CatBoost + pi-ratings** (Soccer Prediction Challenge 2023) | 2023 | Gradient-boosted trees con rating features. Comparado con deep learning (TimesNet + Transformer) | State-of-the-art en W/D/L |

### Taxonomía de Modelos (Bunker & Susnjak, 2022)

1. **Statistical models**: Poisson (bivariate, independent), negative binomial, ordered logistic regression
2. **Machine learning**: Random Forest, XGBoost, CatBoost, SVM, Bayesian Networks
3. **Rating systems**: ELO, pi-ratings, Berrar ratings, GAP ratings, PageRank
4. **Deep learning**: CNN, LSTM, Transformers, Graph Neural Networks, Siamese Networks
5. **Ensemble/Hybrid**: Combinaciones de los anteriores

**Hallazgo clave**: Gradient-boosted tree models (XGBoost, CatBoost) con rating features son actualmente state-of-the-art para predicción W/D/L. Deep learning aún no supera consistentemente a boosted trees en datos tabulares de fútbol.

Referencia: [Bunker & Susnjak - JAIR 2022](https://www.jair.org/index.php/jair/article/download/13509/26786/)

---

## 3. Plataformas SaaS y Herramientas

### Forebet
- **URL**: https://www.forebet.com
- **Modelo**: Algoritmo matemático/estadístico propietario (NO machine learning público)
- **Cobertura**: 1,200+ ligas, 7 deportes
- **Predicciones**: 1X2, correct score, BTTS, Over/Under 2.5 (75-80% accuracy reportada), doble chance, HT/FT
- **Precio**: GRATUITO (no hay suscripciones)
- **Características**: Kelly Criterion, trends, match previews, injured/suspended players, weather, odds comparison
- **Tráfico**: 5M+ visits/mes
- **Desde**: 2009
- **Limitaciones**: Metodología no pública, no hay backtests publicados, accuracy metrics no disponibles

### SoccerPunter
- **URL**: https://www.soccerpunter.com
- **Modelo**: Algoritmo propietario con análisis estadístico
- **Cobertura**: 500+ competiciones, 90+ países
- **Características**: H2H stats, form, tipsters competition, live scores, odds analysis, Asian handicap
- **Precio**: Gratuito + Platinum/VIP (pago)
- **Desde**: 2007
- **Usuarios**: 1M+ visitantes

### PredictBet
- Plataforma de predicciones con comunidad de tipsters
- Basada en votación colectiva y análisis estadístico

### Windrawwin
- Predicciones gratuitas 1X2, correct score
- Estadísticas H2H, form tables
- Community tipsters

### Otras mencionadas
- **Predictz** (6.6 rating)
- **WinDrawWin** (6.6)
- **Betstudy** (5.9)
- **Vitibet** (5.6)
- **Soccervista** (5.1)
- **Zulubet** (4.4)

Fuente: [Comparison of prediction sites](https://betting-tips.today/soccer-prediction-sites/)

---

## 4. Arquitectura de Sistemas de Predicción

### Pipeline Típico (End-to-End)

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Data    │ →  │  Raw     │ →  │  Feature │ →  │  Model   │ →  │  API +   │ →  │ Monitor  │
│ Sources  │    │ Storage  │    │  Engine  │    │ Training │    │ Serving  │    │ & Retrain│
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### Capas Detalladas

#### 1. Data Ingestion
- **Fuentes**: football-data.co.uk (gratuito), API-Football, StatsBomb, Understat (xG), OpenFootball, SofaScore
- **Herramientas**: Airflow, Prefect, custom Python scripts
- **Formato**: Raw JSON/CSV → S3/MinIO (data lake)

#### 2. Storage
- **Raw Lake**: AWS S3 / MinIO (S3-compatible) - particionado por fecha
- **Base de datos**: PostgreSQL (relacional), TimescaleDB (time-series optimizado)
- **Data Warehouse**: Snowflake, Redshift (para analytics pesados)
- **Arquitectura recomendada**: Medallion (Bronze→Silver→Gold)

#### 3. Feature Engineering
- **Herramientas**: dbt (transformaciones SQL), Python (pandas, numpy)
- **Feature Store**: Feast (open-source), Tecton (comercial), Hopsworks, Darwin Feature Store (Dream11)
- **Features típicas**: ELO, form (últimos 5 partidos), average goals, xG, posesión, H2H, rest days, odds, PPDA

#### 4. Model Training
- **Experiment tracking**: MLflow (dominante), Weights & Biases
- **Model Registry**: MLflow Model Registry, Seldon, BentoML
- **Validación temporal**: Walk-forward validation (time-series CV), embargo windows anti-leakage
- **Frameworks**: scikit-learn, XGBoost, LightGBM, CatBoost, PyTorch

#### 5. Serving/API
- **API**: FastAPI (recomendado), Flask
- **Frontend**: Streamlit (rápido), React/Vite (producción)
- **Contenedores**: Docker, Kubernetes
- **Deploy**: Vercel, Render, AWS EC2/ECS, GCP Cloud Run

#### 6. MLOps & Monitoring
- **Orquestación**: Airflow, Prefect, Dagster
- **CI/CD**: GitHub Actions, GitLab CI
- **Monitoring**: Prometheus + Grafana, Evidently (drift), WhyLabs
- **Alerting**: Slack, PagerDuty

### Stack Moderno Recomendado (basado en proyectos reales)

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| Orquestación | Apache Airflow / Prefect | Pipeline scheduling |
| Storage | PostgreSQL / TimescaleDB | Datos estructurados |
| Transform | dbt | Feature engineering SQL |
| Feature Store | Feast | Feature serving + versioning |
| Experimentación | MLflow | Tracking + Registry |
| Modelos | XGBoost / LightGBM + PyTorch (LSTM) | Baseline + Deep Learning |
| API | FastAPI | REST endpoint |
| Frontend | Streamlit / React | Dashboard |
| Container | Docker + Kubernetes | Deploy |
| Monitoring | Prometheus + Grafana + Evidently | Drift + performance |
| CI/CD | GitHub Actions | Automatización |

Referencia: [Automated Sports Prediction Pipelines (2026)](https://trainmyai.net/automated-sports-prediction-pipelines-from-data-sourcing-to-)

---

## 5. Best Practices de MLOps para Deportes

### Feature Store
- **Single source of truth** para features con timestamps explícitos
- **Online/Offline parity**: misma transformación para training y serving
- **Point-in-time joins** para evitar data leakage
- **Herramientas**: Feast (open-source), Darwin Feature Store (Dream11 - 200M requests/min, p99 < 5ms)
- **Feature versioning** y schema management

### Model Versioning
- **MLflow** para tracking de params, metrics, artifacts, git hash
- **Dataset fingerprinting** (MD5 hashes) para reproducibilidad
- **Promotion gates**: shadow → canary (5% traffic) → production
- **Auto-rollback**: si métricas caen debajo de threshold

### Monitoring de Drift
| Tipo | Detección | Threshold |
|------|-----------|-----------|
| Data drift (covariate) | PSI (Population Stability Index), KS test | PSI > 0.25 |
| Concept drift | ADWIN, Page-Hinkley en residuals | Delta conservador |
| Performance decay | Rolling AUC, Brier score, EV | Drop > X% trigger retrain |
| Label shift | Distribución de outcomes | Cambios súbitos |

### Retraining Frequency
- **Light retrain**: nightly (incorporar resultados del día)
- **Full retrain**: semanal (con hyperparameter search)
- **Event-driven**: cuando drift detectors disparan o hay cambios mayores (lesiones, traspasos)
- **Continuous learning**: online learner con learning rate conservador (1e-4 a 1e-3), update budget < 10%

### Otras Prácticas

1. **Time-aware evaluation**: walk-forward validation, nunca random k-fold
2. **Embargo windows**: evitar leakage temporal entre train y test
3. **Calibration**: Platt scaling o isotonic regression para probabilidades calibradas
4. **Business metrics**: Expected Value (EV), ROI, Kelly Criterion, Sharpe ratio
5. **Data quality**: Great Expectations para validación de schemas y rangos
6. **Dead letter queues**: S3 DLQ para fallos de extracción, replay automático
7. **Cost optimization**: spot instances para retraining, autoscaling basado en demanda

Referencias:
- [Continuous Learning Playbook (2026)](https://newdata.cloud/continuous-learning-in-production-the-mlops-playbook-behind-)
- [MLOps for Self-Learning Systems (2026)](https://analysts.cloud/designing-mlops-for-self-learning-prediction-systems-lessons)
- [Reproducible Sports AI Pipelines (2026)](https://smart-labs.cloud/operationalizing-ai-picks-reproducible-pipelines-for-sports-)

---

## Conclusiones y Recomendaciones

1. **Modelo base recomendado**: XGBoost/CatBoost con rating features (ELO, pi-ratings) + engineered features (form, goals avg, rest days). State-of-the-art actual para predicción W/D/L.

2. **Arquitectura**: Airflow (orquestación) → PostgreSQL/TimescaleDB (storage) → dbt (features) → Feast (feature store) → MLflow (experiment tracking) → FastAPI (serving) → Streamlit/React (frontend).

3. **Feature engineering**: ELO, rolling form (5 partidos), average goals/conceded, H2H, rest days, xG si disponible, odds de casas de apuestas como benchmark.

4. **MLOps**: Nightly retrain + weekly full retrain, drift detection (PSI + log-loss), auto-rollback, walk-forward validation.

5. **Datos**: football-data.co.uk (gratuito, 25+ años), API-Football, StatsBomb Open Data, OpenFootball.

6. **Diferenciación**: Combinar ensemble de modelos (XGBoost + LSTM) con calibración bayesiana sobre odds en vivo. Automatización completa del pipeline con Airflow y GitHub Actions.
