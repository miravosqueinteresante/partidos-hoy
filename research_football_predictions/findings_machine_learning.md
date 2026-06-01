# Investigación: Machine Learning para Predicción de Partidos de Fútbol

> Fecha: 31 Mayo 2026
> Propósito: Base de conocimiento técnico para sistema de predicción de resultados futbolísticos

---

## 1. Algoritmos ML Usados en Predicción Deportiva — Estado del Arte

### 1.1 Gradient Boosting (XGBoost, LightGBM, CatBoost) — El estado del arte actual

Los modelos basados en gradient boosting son actualmente los más utilizados y efectivos para predicción de resultados en fútbol. Múltiples estudios y competiciones lo confirman:

- **XGBoost** logra ~65% de accuracy en predicción 1X2 en datasets históricos de ligas europeas (OpenRiver, 2024)
- **CatBoost + pi-ratings** fue el mejor modelo del 2023 Soccer Prediction Challenge con 55.82% de accuracy sobre 714+ partidos (Yeung et al., arXiv 2309.14807)
- **Random Forest + XGBoost en ensemble voting** logra la mayor consistencia entre distintas ligas (Atta Mills et al., Journal of Big Data, 2024)
- **XGBoost + LSTM híbrido** — el XGBoost procesa features estáticas (rankings, clima), el LSTM procesa odds dinámicas (Li et al., IEEE ITME 2024)

**Por qué funcionan bien:**
- Manejan features tabulares heterogéneas (numéricas + categóricas) sin necesidad de normalización exhaustiva
- Capturan interacciones no lineales entre features (forma reciente × localía)
- CatBoost maneja categorías nativamente con *ordered boosting* que reduce overfitting
- Son interpretables mediante SHAP values y feature importance

**Referencias:**
- Yeung et al., "Evaluating Soccer Match Prediction Models" (2023) → https://arxiv.org/abs/2309.14807
- Atta Mills et al., "Data-driven prediction of soccer outcomes" (2024) → https://link.springer.com/article/10.1186/s40537-024-01008-2
- Li et al., "Research on Prediction of Football Match Results Based on XGBoost and LSTM" (2024) → https://ieeexplore.ieee.org/document/10935531
- OpenRiver, "Prediction of Soccer Match Result with ML" → https://openriver.winona.edu/cgi/viewcontent.cgi?article=1559&context=rca

### 1.2 Redes Neuronales (MLP, LSTM, Transformers)

| Arquitectura | Accuracy Reportada | Contexto |
|---|---|---|
| MLP (3 capas, 100 neuronas, Swish) | 62.5% | Premier League, datos largos (Joffrey Mayer, 2023) |
| Feedforward NN | ~66% | Eredivisie, supera a XGBoost en ciertos casos (Atta Mills, 2024) |
| LSTM (secuencia larga, 9840 juegos NBA) | 72.35% | NBA, no fútbol pero relevante (Rios et al., arXiv 2512.08591) |
| XGBoost+LSTM híbrido | Mejora vs XGBoost solo | Fusiona prior knowledge XGBoost con odds sequence LSTM |

**Conclusión:** Las redes neuronales profundas NO superan consistentemente a gradient boosting en predicción tabular de fútbol. La excepción es cuando hay datos secuenciales (odds cambiantes, secuencias de partidos) donde LSTM/GRU aportan valor.

### 1.3 SVM, Regresión Logística, y Modelos Clásicos

- **Regresión Logística**: Sólida baseline (55-58% accuracy). Buena calibración de probabilidades. Ideal para comparar.
- **SVM**: Rendimiento inferior a ensemble methods en tests publicados. Mejora con kernel RBF pero escala mal.
- **Random Forest solo**: ~59% — superado por XGBoost/LightGBM en casi todos los estudios.

### 1.4 Enfoques Híbridos (Recomendados)

La arquitectura híbrida más prometedora:

```
p̂ = f_θ(X_stat, X_context, X_historical)
```

Donde:
- **X_stat**: fuerza de equipo (ELO, ranking), tendencias de goles, forma, comportamiento local/visitante
- **X_context**: fase de temporada, congestión de partidos, fatiga, riesgo de rotación
- **X_historical**: rendimiento empírico por liga, rango de probabilidad, segmento de confianza

Fuente: Foresportia, "AI football prediction: feature engineering and calibration" → https://www.foresportia.com/en/blog/technical-note-2-ai-football-prediction-model.html

---

## 2. Feature Engineering para Fútbol

### 2.1 Categorías de Features

#### Fuerza del Equipo (Team Strength)
| Feature | Descripción | Fuente |
|---|---|---|
| `ELO_home`, `ELO_away` | Rating ELO actualizado tras cada partido | Exprysm, 2026 |
| `ΔELO = ELO_h - ELO_a` | Diferencia de ELO | Foresportia |
| `pi-rating` | Separación ataque/defensa, local/visitante | 2023 Soccer Challenge |
| `Ranking` | Posición en liga al momento del partido | Sportmonks |

#### Forma Reciente (Recent Form)
```
FormDiff = Form_h - Form_a
Form_h = suma de puntos últimos N partidos (típicamente 5)
```
- Rolling averages de goles: GF, GC, GF_rolling_5, GC_rolling_5
- Diferencia de puntos: `DifPts = Pts_h - Pts_a` hasta el partido actual
- Diferencia de forma: `DifFormPts = FormPts_h(5) - FormPts_a(5)`
- Ventanas temporales recomendadas: 3, 5, 10 partidos

Fuente: Joffrey Mayer (2023) → https://www.joffreymayer.com/project/deep-learning/neural-network-to-predict-football-matches-joffrey-mayer.pdf

#### Localía (Home Advantage)
- Factor HFA típico: 50-100 puntos ELO
- Rendimiento histórico local vs visitante separados
- Distancia de viaje del visitante

#### Head-to-Head
- Últimos N enfrentamientos directos
- Diferencia de goles en H2H
- Ratio de victorias local en H2H

#### Métricas Avanzadas
| Feature | Descripción |
|---|---|
| `xG` (Expected Goals) | Calidad de chances creadas, modelo basado en 300k+ shots |
| `xT` (Expected Threat) | Probabilidad de que una acción genere gol |
| `Posesión` | % de posesión en últimos partidos |
| `Ataque/Defensa` | Fuerza separada por área (pi-ratings) |
| `Fatiga` | Días desde último partido, congestión de fixtures |

### 2.2 ELO Ratings — Fórmula y Adaptación

```
E_home = 1 / (1 + 10^((R_away - R_home - HFA) / 400))

R_new = R_old + K × (S_actual - E_expected)

donde:
S_actual = 1 (local gana), 0.5 (empate), 0 (pierde)
K ≈ 20-40 (factor de sensibilidad)
HFA ≈ 50-100 puntos
```

Fuente: Exprysm, "ELO Ratings in Football" → https://exprysm.com/insights/methodology/elo-ratings-football.html

### 2.3 Pi-Ratings (Mejora sobre ELO)

Separación de fuerza en:
- `pi_att_home`, `pi_def_home`, `pi_att_away`, `pi_def_away`
- Actualización independiente por cada componente
- Mejor rendimiento probado en 2023 Soccer Prediction Challenge con CatBoost

### 2.4 Normalización y Preprocesamiento

- **Min-Max Scaling** para features de rango acotado (posesión, precisión pase)
- **Z-score (StandardScaler)** para distribuciones no acotadas (goles, ELO)
- **Target encoding** para equipos y ligas (con smoothing para evitar leakage)
- **Time-decay weighting**: partidos más recientes pesan más en rolling averages

### 2.5 Datasets Públicos Recomendados

| Dataset | Descripción | Acceso |
|---|---|---|
| football-data.co.uk | Resultados, estadísticas, odds (30+ ligas) | Gratuito |
| StatsBomb Open Data | Event data granular (pases, tiros, xG) | https://github.com/statsbomb/open-data |
| Understat | xG por partido, ligas europeas | Via API |
| Kaggle Soccer Prediction | Múltiples competiciones | https://www.kaggle.com/competitions/prediction-of-results-in-soccer-matches |

---

## 3. Frameworks y Librerías

### 3.1 Pipeline Recomendado (Python)

| Etapa | Librería | Propósito |
|---|---|---|
| Datos | `pandas`, `numpy` | Manipulación y agregación |
| Features | `pandas`, `feature-engine` | Rolling windows, encoding |
| Modelos tradicionales | `scikit-learn` | RF, LR, SVM, métricas |
| Gradient Boosting | `xgboost`, `lightgbm`, `catboost` | Modelos principales |
| Deep Learning | `pytorch` / `tensorflow` | LSTM, MLP (cuando aplica) |
| Evaluación | `scikit-learn`, `scipy` | Brier, log loss, RPS |
| Interpretación | `shap` | SHAP values, feature importance |
| Experimentación | `mlflow` | Tracking de experimentos |

### 3.2 APIs de Datos Deportivos

| API | Coverage | Costo |
|---|---|---|
| API-Football (RapidAPI) | 100+ ligas, eventos en vivo | Freemium |
| Sportmonks | Fútbol global, odds históricos | Paga |
| The Odds API | Odds de múltiples casas | Freemium |
| Football-Data.org | Resultados históricos, 20+ ligas | Freemium (10 req/min free) |

### 3.3 Frameworks Específicos para Deportes

- **sports-betting** (Python): https://github.com/georgedouzas/sports-betting
- **sportslabkit**: Tracking multi-objeto para deportes
- **ggshakeR** (R): Análisis y visualización con datos públicos
- **SoccerMap**: Visualización de rendimiento táctico

---

## 4. Time Series en Fútbol

### 4.1 Naturaleza Secuencial

Los partidos de fútbol NO son i.i.d. — existe dependencia temporal:
- El resultado de un partido depende del estado del equipo (forma, lesiones, moral)
- Los equipos evolucionan en el tiempo (plantilla, entrenador, estilo)
- Las temporadas tienen ciclos (principio, medio, final)

### 4.2 Estrategias de Modelado Temporal

#### Opción A: Features temporales + modelo tabular (RECOMENDADA)
- Rolling averages sobre ventanas de N partidos
- Features de tendencia (pendiente de últimos 5 partidos)
- Momentum (resultados ponderados por recencia)
- Más simple, menos overfitting, mejores resultados prácticos

#### Opción B: LSTM / GRU
- Input: secuencia de features por partido para cada equipo
- Output: probabilidades 1X2
- Problema: requiere muchas temporadas, propenso a overfitting
- Mejor para: odds sequences (XGBoost+LSTM híbrido)

```python
# Pseudocódigo LSTM para secuencia de partidos
model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(n_matches, n_features)),
    Dropout(0.3),
    LSTM(32),
    Dropout(0.2),
    Dense(16, activation='relu'),
    Dense(3, activation='softmax')  # 1X2
])
```

#### Opción C: Atención Temporal / Transformers
- Atención sobre secuencia de partidos recientes
- Captura qué partidos en la historia son más relevantes para el próximo
- Aún experimental en fútbol (más usado en NBA)

### 4.3 Resultados Reportados

| Arquitectura | Dataset | Accuracy |
|---|---|---|
| LSTM (Stanford CS230) | Premier League 08-19 | ~55% |
| LSTM + XGBoost | Partidos + odds | Superior a XGBoost solo |
| GRU + Atención | Experimental | Sin benchmark sólido aún |

Fuente CS230 Stanford: https://cs230.stanford.edu/projects_spring_2020/reports/38854780.pdf

---

## 5. Métricas de Evaluación

### 5.1 Brier Score (Recomendada #1)

```
BS = (1/N) × Σ(f_t - o_t)²

f_t = probabilidad pronosticada, o_t = resultado real (0 o 1)
```

- **Proper scoring rule**: minimizada solo cuando las probabilidades son las verdaderas
- Rango: 0 (perfecto) a 1 (pésimo)
- Benchmark típico en fútbol: BS < 0.20 es bueno, < 0.18 es excelente
- Ventaja: evalúa calibración, no solo acierto binario

Fuente: OddsAccuracy → https://www.oddsaccuracy.com/research/what_is_brier_score.html

### 5.2 Ranked Probability Score (RPS)

```
RPS = (1/(K-1)) × Σ(F_t - O_t)²
donde F_t = CDF de predicción, O_t = CDF del resultado
```

- Sensible al orden: Home Win ≈ Draw > Away Win (en distancia)
- Útil para resultados ordinales (1X2 tiene orden natural)
- **CRÍTICA**: Wheatcroft (2021, JQAS) demuestra que el RPS no aporta vs Brier, y el Ignorance Score (log loss) es superior

Fuente debate: https://ideas.repec.org/a/bpj/jqsprt/v17y2021i4p273-287n1.html

### 5.3 Log Loss / Cross-Entropy

```
LogLoss = -(1/N) × Σ(y_i × log(p_i) + (1-y_i) × log(1-p_i))
```

- Penaliza fuertemente predicciones confiadas pero incorrectas
- Proper scoring rule
- Equivalente al Ignorance Score para comparaciones

### 5.4 Accuracy y Matriz de Confusión

```
Accuracy = correctas / total
```

- **Limitación**: No distingue entre probabilidades 51% vs 99%
- Útil como métrica secundaria
- Esperable: 50-60% para modelos decentes, >65% para modelos excelentes
- **Draw** es siempre la clase más difícil (recall típicamente < 30%)

### 5.5 ROI Simulado (Apuestas)

```
ROI = (Σ retornos - Σ stakes) / Σ stakes × 100%
```

- Evalúa si las predicciones son rentables contra odds reales
- Kelly Criterion para sizing
- Crucial: usar odds de cierre (closing odds) como benchmark

### 5.6 Expected Calibration Error (ECE)

```
ECE = Σ |acc(bin) - conf(bin)| × peso(bin)
```

- Mide si cuando el modelo dice 70%, acierta el 70% de las veces
- Ideal para diagnosticar calibración

### 5.7 Recomendación de Métricas para el Proyecto

| Prioridad | Métrica | Para qué |
|---|---|---|
| 1 | Brier Score | Evaluación principal de calibración |
| 2 | Log Loss | Penalización por sobreconfianza |
| 3 | Accuracy × clase | Diagnóstico por resultado (H/D/A) |
| 4 | ECE | Calibración por bins |
| 5 | ROI simulado | Validación financiera |

---

## 6. Data Leakage y Overfitting en Contexto Deportivo

### 6.1 Temporal Leakage — El Riesgo #1 en Fútbol

El peor error en predicción deportiva es usar información futura para predecir el pasado.

**Ejemplos de temporal leakage en fútbol:**
- Calcular rolling averages usando datos posteriores al partido a predecir
- Normalizar con media/desviación de toda la temporada (incluye datos futuros)
- Usar estadísticas de un partido como feature para predecir ese mismo partido
- Target encoding de equipos usando toda la historia (incluye futuro)
- Hacer train/test split aleatorio en lugar de cronológico

### 6.2 Estrategias de Prevención

#### Split Cronológico (Obligatorio)
```python
# INCORRECTO: random split
X_train, X_test = train_test_split(df, test_size=0.2)

# CORRECTO: split cronológico
train = df[df['date'] < '2025-01-01']
test = df[df['date'] >= '2025-01-01']
```

#### Rolling Window Cross-Validation
```python
# TimeSeriesSplit de scikit-learn
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
```

#### Ventana de Entrenamiento Móvil
- Usar solo últimos 3-5 años de datos (los equipos cambian)
- Reentrenar modelo cada temporada
- Ponderación temporal: partidos recientes pesan más

Fuente: Meegle, "Overfitting In Sports Analytics" → https://www.meegle.com/en_us/topics/overfitting/overfitting-in-sports-analytics

### 6.3 Feature Leakage Específico de Fútbol

| Feature Peligrosa | Problema |
|---|---|
| Resultado del partido | Obvio — es el target |
| Goles del partido | Obvio — es información post-partido |
| Estadísticas del partido (tiros, posesión) | No disponibles antes del partido — solo usar históricos |
| Odds pre-partido | Válidas (disponibles antes) — pero cuidado con cuáles se usan |
| xG del partido | No disponible antes del partido |
| Próximo fixture | Usar solo fixtures pasados para calcular fatiga |

### 6.4 Señales de Alarma de Overfitting

- Accuracy > 70% en test — sospechoso en fútbol (el ruido es inherente)
- Accuracy en entrenamiento >> accuracy en test (gap > 10%)
- Rendimiento cae drásticamente entre temporadas
- Features con importancia imposible (ej: "día de la semana" como top feature)
- El modelo no generaliza a otras ligas

### 6.5 Checklist Anti-Leakage

- [ ] Split cronológico (NUNCA aleatorio)
- [ ] Rolling averages calculados solo con datos anteriores al match
- [ ] Normalización por ventana de entrenamiento, no global
- [ ] Target encoding con smoothing y solo datos disponibles
- [ ] ELO ratings actualizados secuencialmente (sin mirar el futuro)
- [ ] Feature importance revisada por sentido futbolístico
- [ ] Validación en temporada completa hold-out
- [ ] Backtest con ROI contra odds reales

Fuente: IBM, "What is data leakage in ML?" → https://www.ibm.com/think/topics/data-leakage-machine-learning

---

## 7. Conclusiones y Recomendaciones

### Stack Técnico Recomendado

```
Modelo primario:     CatBoost o XGBoost (gradient boosting)
Modelo secundario:   Regresión Logística (calibración baseline)
Deep Learning:       Solo si hay datos secuenciales de odds
Features:            ELO + rolling averages + pi-ratings + forma
Métrica principal:   Brier Score
Validación:          TimeSeriesSplit cronológico
Datos mínimos:       3-5 temporadas por liga
```

### Accuracy Esperable (Realista)

| Nivel | Accuracy 1X2 | Brier Score |
|---|---|---|
| Baseline (siempre local) | ~45% | ~0.22 |
| Regresión Logística | 52-55% | ~0.20 |
| XGBoost/CatBoost bueno | 55-60% | ~0.18 |
| Excelente (top papers) | 60-65% | ~0.17 |
| Sospechoso de leakage | >70% | <0.15 |

### Áreas Abiertas para Investigación

1. **Graph Neural Networks** para modelar interacciones plantilla ↔ rival (Al-Bustami, 2025)
2. **Atención temporal** sobre secuencias de partidos con positional encoding
3. **Fusión multimodal**: stats + texto (lesiones, noticias) + odds mercado
4. **xG como feature intermedio** en lugar de solo goles reales
5. **Modelos por liga** vs modelo global con meta-learners

---

## Referencias Clave

1. Yeung et al. (2023) — "Evaluating Soccer Match Prediction Models" → https://arxiv.org/abs/2309.14807
2. Atta Mills et al. (2024) — "Data-driven prediction of soccer outcomes" → https://link.springer.com/article/10.1186/s40537-024-01008-2
3. Li et al. (2024) — "XGBoost and LSTM for Football Prediction" → https://ieeexplore.ieee.org/document/10935531
4. Wheatcroft (2021) — "Evaluating probabilistic forecasts: case against RPS" → https://ideas.repec.org/a/bpj/jqsprt/v17y2021i4p273-287n1.html
5. Stanford CS230 — "Football Match Prediction using Deep Learning" → https://cs230.stanford.edu/projects_spring_2020/reports/38854780.pdf
6. Foresportia — "Feature engineering and calibration" → https://www.foresportia.com/en/blog/technical-note-2-ai-football-prediction-model.html
7. Exprysm — "ELO Ratings in Football" → https://exprysm.com/insights/methodology/elo-ratings-football.html
8. IBM — "Data leakage in machine learning" → https://www.ibm.com/think/topics/data-leakage-machine-learning
9. Sportmonks — "Algorithm (Predictive Modeling)" → https://www.sportmonks.com/glossary/algorithm-predictive-modeling
10. OddsAccuracy — "Brier Score in Football Predictions" → https://www.oddsaccuracy.com/research/what_is_brier_score.html
