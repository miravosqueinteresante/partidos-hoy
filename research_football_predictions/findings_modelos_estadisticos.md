# Modelos Estadísticos para Predicción de Partidos de Fútbol

## 1. Distribución Poisson para Predicción de Fútbol

### 1.1 Poisson Independiente (Maher, 1982)

- **Qué es**: Modelo que asume que los goles que anota cada equipo en un partido siguen una distribución de Poisson independiente. Desarrollado formalmente por Maher (1982), aunque Moroney (1956) ya había observado que los goles seguían patrones Poisson. La probabilidad conjunta de un marcador (i, j) es simplemente el producto de dos probabilidades Poisson independientes.

- **Fórmula**: 
  - P(X = k) = (λ^k × e^(-λ)) / k!
    donde λ = goles esperados del equipo, k = número de goles, e ≈ 2.71828
  - λ_local = μ × α_local × β_visitante  (goles esperados local = media global × ataque local × defensa visitante)
  - λ_visitante = μ × α_visitante × β_local
  - P(Home=i, Away=j) = P_poisson(i; λ_local) × P_poisson(j; λ_visitante)

- **Datos necesarios**: Historial de partidos con goles anotados por cada equipo. Idealmente 2-5 temporadas de la misma liga. Se necesita identificar equipos local/visitante y goles.

- **Pros**: Simple, interpretable, fácil de implementar (GLM Poisson en R/Python), genera matriz completa de probabilidades de marcadores, de donde se derivan 1X2, BTTS, Over/Under, hándicap asiático.

- **Contras**: Asume independencia entre goles local/visitante (no captura correlación en partidos de pocos goles); subestima empates y marcadores bajos (0-0, 1-1); no captura overdispersion (varianza > media que ocurre en algunos contextos); asume tasa de gol constante durante el partido.

- **Precisión/Referencias**: 
  - Maher (1982) encontró que el modelo Poisson independiente da una descripción "razonablemente precisa" de los marcadores, aunque con pequeñas diferencias sistemáticas. Un modelo Poisson bivariante con correlación de 0.2 entre los goles mejoraba el ajuste.
  - Penn et al. (2022, PLoS ONE) usaron el "double Poisson model" para Euro 2020, ganando la competencia de predicción de la Royal Statistical Society. El modelo predijo con "alta precisión" el número de goles.
  - Un estudio en MDPI Applied Sciences (2024) usó regresión Poisson doble en Premier League 2022-23 con resultados prometedores.
  - Fuentes: https://pubmed.ncbi.nlm.nih.gov/35588428/, https://pmc.ncbi.nlm.nih.gov/articles/PMC9119507/, https://exprysm.com/insights/methodology/dixon-coles-model.html

### 1.2 Poisson Bivariante (Karlis-Ntzoufras, 2003)

- **Qué es**: Extensión que modela conjuntamente los goles de ambos equipos usando una distribución Poisson bivariante, permitiendo correlación entre ellos. En lugar de la independencia, introduce un término de covarianza.

- **Fórmula**: La distribución Poisson bivariante tiene función de probabilidad conjunta que incluye un parámetro de covarianza (cov). La correlación entre X (goles local) e Y (goles visitante) se modela explícitamente. Una alternativa es usar la distribución Skellam (diferencia de goles) que elimina la necesidad de modelar correlación directamente.

- **Datos necesarios**: Mismos que Poisson independiente. Los parámetros se estiman con máxima verosimilitud.

- **Pros**: Captura correlación entre goles de ambos equipos; mejora predicción de empates; más realista que Poisson independiente.

- **Contras**: Más complejo computacionalmente; sigue teniendo limitaciones con overdispersion extrema.

- **Precisión/Referencias**: 
  - Karlis y Ntzoufras (2003, J. Royal Statistical Society) mostraron que "incluso una correlación leve mejora el ajuste del modelo y la predicción del número de empates".
  - Fuente: https://www.jstor.org/stable/4128211

---

## 2. Modelo Elo en Fútbol

### 2.1 World Football Elo Ratings

- **Qué es**: Sistema de rating adaptado del sistema Elo de ajedrez (creado por Arpad Elo) al fútbol de selecciones nacionales. Desarrollado por Bob Runyan en 1997 y actualmente mantenido en eloratings.net. Se diferencia del ranking FIFA tradicional por incluir margen de victoria, importancia del partido y ventaja local.

- **Fórmula**:
  - R_post = R_pre + K × (S - E[S])
    donde R = rating, K = factor K (máximo 60, ajustable), S = resultado real (1 = victoria, 0.5 = empate, 0 = derrota), E[S] = resultado esperado
  - E[S_local] = 1 / (1 + 10^(-(R_local - R_visitante + h) / 400))
    donde h = ventaja local (~100 puntos Elo)
  - Ajuste por diferencia de goles: la ganancia/pérdida de puntos se multiplica por un factor según la diferencia de goles (GD): factor = ln(GD + 1) × (2.2 / (2.2 + (R_local - R_visitante) × 0.001))
  - Ponderación por importancia: amistoso × 1.0, eliminatoria continental × 2.5, mundial × 3.0

- **Datos necesarios**: Resultados de partidos internacionales, identificando local/visitante/neutral, competición, goles. Se requieren ~30 partidos para que el rating converja.

- **Pros**: Simple, transparente, no requiere datos de eventos (solo resultados); se actualiza automáticamente tras cada partido; funciona bien con datos escasos (selecciones); los ratings Elo tienen "la mayor capacidad predictiva para partidos de fútbol" según estudios comparativos.

- **Contras**: No genera probabilidades de marcador exacto (solo resultado 1X2); no usa información de rendimiento subyacente (xG); no modela la varianza de gol; K-factor es arbitrario y requiere calibración; funciona mejor con selecciones que con clubes (menos partidos por año).

- **Precisión/Referencias**:
  - Un estudio de Virginia Tech (CS 5824) sobre EPL encontró que con K_normal = 25 y K_inicial = 40, y ventaja local h = 100, el modelo mejora ~2.88% en precisión sobre 5 temporadas.
  - Clubelo.com usa Elo para clubes con predicciones publicadas y verificables.
  - ESPN contrató a Nate Silver para crear el SPI basado en principios Elo.
  - Fuentes: https://en.wikipedia.org/wiki/World_Football_Elo_Ratings, https://www.eloratings.net/about, https://courses.cs.vt.edu/cs5824/Fall15/project_reports/sullivan_cronin.pdf

### 2.2 SPI (Soccer Power Index) de ESPN

- **Qué es**: Sistema de rating desarrollado por Nate Silver para ESPN antes del Mundial 2010. Evalúa a los equipos basándose en el rendimiento de sus jugadores tanto en club como en selección, a diferencia del ranking FIFA que solo considera partidos internacionales. Existen versiones para selecciones y para clubes (FiveThirtyEight).

- **Fórmula**: Combina una métrica de fuerza ofensiva y defensiva basada en goles esperados ajustados. Compara a cada equipo con un equipo promedio en campo neutral usando distribución Poisson para estimar puntos esperados. Un equipo con rating 80 obtendría el 80% de los puntos posibles contra el equipo base.

- **Datos necesarios**: Datos de eventos de partidos (goles esperados, tiros, posesión), rendimiento de jugadores en liga local y competiciones internacionales.

- **Pros**: Considera rendimiento de jugadores individuales; captura calidad de liga; se actualiza en tiempo real; más sofisticado que Elo básico.

- **Contras**: Propietario (ESPN/FiveThirtyEight); requiere más datos que Elo; menos transparente (algoritmo no totalmente público).

- **Precisión/Referencias**: FiveThirtyEight publicaba predicciones verificables públicamente para múltiples ligas europeas.
  - Fuentes: https://statsultra.com/football-club-strength-ratings, http://www.nicksonderup.com/espn-spi

---

## 3. Expected Goals (xG)

### 3.1 Definición y Concepto

- **Qué es**: Métrica que asigna una probabilidad a cada disparo de convertirse en gol (valor entre 0 y 1). Un xG de 0.30 significa que, históricamente, el 30% de los disparos con esas características terminan en gol. Se ha convertido en la métrica fundamental del análisis de fútbol moderno.

- **Fórmula**: Modelo de clasificación binaria (¿el disparo termina en gol? Sí/No):
  - P(gol | características del disparo) = 1 / (1 + e^(-(β0 + β1×x1 + β2×x2 + ... + βn×xn)))
    donde x son las características del disparo.
  - Algoritmos comunes: Regresión logística, XGBoost, Random Forest, modelos Bayesianos, redes neuronales.
  - Un estudio de Frontiers (2025) usó un modelo Bayesiano mixto con solo 7 variables (tipo de disparo, posición, oponentes circundantes) logrando AUC = 0.781, comparable al modelo StatsBomb (AUC = 0.801) que usa muchas más variables.

- **Datos necesarios**: Datos de eventos de partidos (shot-level data) con:
  - Coordenadas (x, y) del disparo
  - Distancia y ángulo al arco
  - Parte del cuerpo (cabeza/pie)
  - Tipo de jugada (penalti, tiro libre, jugada abierta, contraataque)
  - Número de defensores entre el tirador y el arco
  - Asistencia (tipo de pase, si fue cruzado)
  - Secuencia de eventos previos (modelos avanzados incluyen "advancement factor" y secuencias de pases)
  - Posición del portero (tracking data)

- **Pros**: Mucho más predictivo que los goles reales (reduce ruido); permite evaluar rendimiento subyacente de equipos y jugadores; se estabiliza más rápido que los goles (menor varianza muestral); permite detectar "suerte" (sobrerendimiento o subrrendimiento respecto a xG).

- **Contras**: Depende de la calidad del proveedor de datos (Opta, StatsBomb, Wyscout); requiere modelos entrenados con datos etiquetados de alta calidad; diferentes proveedores usan modelos distintos (no hay un xG "universal"); no captura tiros bloqueados ni oportunidades sin remate.

- **Precisión/Referencias**:
  - Cefis & Carpita (2024, J. Operational Research Society) crearon un nuevo modelo xG con datos de tracking + eventos de Serie A 2019/20, superando a Understat en AUC usando regresión logística con ajuste de desbalanceo.
  - Bandara et al. (2024, PLoS ONE) mejoraron xG usando secuencias de eventos previos con Random Forest. Sus características novedosas ("advancement factor", "player position column") mejoraron significativamente la precisión sobre modelos de evento único.
  - Studiod e Frontiers (2025) mostró que un modelo Bayesiano con solo 7 variables logra AUC ~0.78.
  - El modelo StatsBomb (estándar de la industria) reporta AUC ~0.80.
  - Fuentes: https://www.tandfonline.com/doi/full/10.1080/01605682.2024.2323669, https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0312278, https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1504362/full

---

## 4. Modelo Dixon-Coles (1997)

- **Qué es**: Desarrollado por Mark Dixon y Stuart Coles en su paper seminal "Modelling Association Football Scores and Inefficiencies in the Football Betting Market" (1997). Extiende el modelo Poisson independiente con dos mejoras clave: (1) un factor de corrección τ (rho) para capturar dependencia en marcadores bajos, y (2) ponderación temporal (time decay) para dar más peso a partidos recientes.

- **Fórmula**:
  - **Factor τ (corrección por baja anotación)**:
    - τ(x, y, λ_local, λ_vis, ρ) se define como:
      - Si (x=0, y=0): τ = 1 - λ_local × λ_vis × ρ
      - Si (x=0, y=1): τ = 1 + λ_local × ρ
      - Si (x=1, y=0): τ = 1 + λ_vis × ρ
      - Si (x=1, y=1): τ = 1 - ρ
      - Para otros marcadores: τ = 1
    - ρ negativo (típicamente ~ -0.1 a -0.2) indica que partidos unilaterales son más comunes de lo que predice Poisson independiente
  
  - **Probabilidad conjunta**: P(X=x, Y=y) = [e^(-λ_local) × λ_local^x / x!] × [e^(-λ_vis) × λ_vis^y / y!] × τ(x, y, λ_local, λ_vis, ρ)
  
  - **Goles esperados**: λ_local = μ × α_i × β_j × γ_local (γ = ventaja local), λ_vis = μ × α_j × β_i
  
  - **Ponderación temporal** (opcional): Pesos exponenciales w(t) = e^(-ξ × (t_actual - t_partido)), donde ξ controla la tasa de decaimiento. Partidos más recientes pesan más.

- **Datos necesarios**: Historial de partidos con fechas, goles, equipos local/visitante, liga/competición. Se estiman α (ataque), β (defensa), ρ, y γ (home advantage) por máxima verosimilitud.

- **Pros**: Corrige la principal debilidad de Poisson (subestimación de marcadores bajos y empates); el factor temporal mejora precisión ante cambios de forma de equipos; genera probabilidades calibradas para todas las líneas de apuesta; estándar de la industria para predicción de fútbol.

- **Contras**: No corrige overdispersion completamente; sigue asumiendo Poisson marginal; estimación requiere optimización numérica (no hay GLM directo); ρ se estima con alta incertidumbre (intervalos de confianza amplios).

- **Precisión/Referencias**:
  - Dixon & Coles (1997) demostraron que su modelo identificaba ineficiencias en el mercado de apuestas, permitiendo estrategias de value betting rentables.
  - El modelo Dixon-Coles sigue siendo el "estándar de la industria" según múltiples implementaciones modernas (ExPrysm, Football Forecast Pro).
  - Implementaciones modernas combinan Dixon-Coles con Monte Carlo (10,000 iteraciones) y blending 70/30 con otros modelos.
  - Fuentes: https://urazakgul.github.io/datafc-blog/posts/en/post3/better-predictions-for-football-matches-how-does-the-dixon-coles-model-work.html, https://exprysm.com/insights/methodology/dixon-coles-model.html, http://tamnguyen.io/dixon-coles

---

## 5. Modelos Maher, Lee, Karlis-Ntzoufras y Otros Enfoques

### 5.1 Modelo Maher (1982)

- **Qué es**: El modelo fundacional. Maher (1982) fue el primero en formalizar el uso de la distribución Poisson independiente con parámetros de ataque/defensa para modelar resultados de fútbol. Propuso una jerarquía de modelos (desde el más simple hasta el más complejo) y los evaluó con pruebas de bondad de ajuste chi-cuadrado.

- **Fórmula**: λ_local = α_i × β_j, λ_visitante = α_j × β_i, con restricción Σα_i = Σβ_i = n (número de equipos). La probabilidad de un marcador (i,j) es el producto de dos Poisson independientes.

- **Datos necesarios**: Matriz de resultados entre equipos.

- **Pros**: Fundacional, simple, sentó las bases para todos los modelos posteriores.

- **Contras**: Asume independencia, subestima empates como se mencionó.

- **Precisión/Referencias**: Maher encontró "diferencias sistemáticas pequeñas" entre las frecuencias observadas y esperadas bajo Poisson independiente. Una correlación bivariante de 0.2 mejoraba el ajuste.
  - Fuente: https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1467-9574.1982.tb00782.x

### 5.2 Modelo de Lee (1997)

- **Qué es**: Lee propuso un modelo basado en la distribución Normal truncada como alternativa a Poisson. Modela la diferencia de goles (no los goles individuales) usando una distribución Normal con corrección por discretización.

- **Fórmula**: La diferencia de goles D = (goles_local - goles_visitante) ~ N(μ, σ²) truncada y discretizada para producir probabilidades enteras.

- **Datos necesarios**: Resultados de partidos (goles).

- **Pros**: Computacionalmente simple; captura naturally la correlación al modelar diferencia en lugar de goles individuales.

- **Contras**: Menos precisa para probabilidades de marcadores exactos; la aproximación Normal es menos natural que Poisson para datos de conteo.

### 5.3 Modelo Karlis-Ntzoufras (2003) - Skellam

- **Qué es**: Karlis y Ntzoufras propusieron usar la distribución **Skellam** (diferencia de dos variables Poisson) para modelar directamente la diferencia de goles, pero dentro de un marco bayesiano y con extensión bivariante. Esto evita la necesidad de modelar correlación explícitamente porque la distribución de la diferencia ya la incorpora implícitamente.

- **Fórmula**: D = Home_goals - Away_goals ~ Skellam(λ_local, λ_visitante), donde λ_local y λ_visitante tienen la misma estructura que en Maher/Dixon-Coles.

- **Datos necesarios**: Mismos que modelos Poisson.

- **Pros**: Marco bayesiano permite incorporar información a priori; enfoque en diferencia de goles es natural para apuestas de hándicap; maneja mejor la correlación.

- **Contras**: No produce directamente probabilidades de marcadores exactos (solo la diferencia); requiere MCMC para estimación (más lento que máxima verosimilitud).

- **Precisión/Referencias**: 
  - Karlis & Ntzoufras (2003, J. Royal Statistical Society) mostraron que los modelos Poisson bivariantes "mejoran el ajuste del modelo y la predicción del número de empates".
  - Implementación disponible en: https://github.com/giuliofantuzzi/BayesianFootballModelling
  - Fuente: https://www.jstor.org/stable/4128211

### 5.4 Negative Binomial (Alternativa a Poisson)

- **Qué es**: Modelo que reemplaza la distribución Poisson con una Negative Binomial, que incluye un parámetro extra de dispersión. Esto permite que la varianza sea mayor que la media (overdispersion), algo común en ligas de alto gol.

- **Fórmula**: P(X = k) = Γ(k + r) / (k! × Γ(r)) × (p^r × (1-p)^k), donde r y p son parámetros con media = r(1-p)/p y varianza = r(1-p)/p² > media.

- **Datos necesarios**: Mismos que Poisson.

- **Pros**: Maneja overdispersion; mejores predicciones de marcadores extremos (4-2, 5-3); útil para tarjetas y córners.

- **Contras**: No corrige correlación entre equipos; más parámetros que estimar; puede ser innecesario en ligas de baja anotación.

### 5.5 Weibull Count + Copula (PenaltyBlog, 2025)

- **Qué es**: Modelo híbrido que usa la distribución Weibull Count (más flexible que Poisson) y cópulas para modelar la dependencia entre goles. Es uno de los enfoques más modernos.

- **Datos necesarios**: Datos de eventos de alta calidad.

- **Pros**: Máxima flexibilidad; captura tanto overdispersion como dependencia.

- **Contras**: Complejidad computacional alta; requiere datos de alta calidad; menos documentado.

---

## Comparación de Precisión Reportada

| Modelo | Precisión 1X2 reportada | Consideraciones |
|--------|------------------------|-----------------|
| Poisson independiente | ~45-50% | Depende de liga y temporada |
| Dixon-Coles | ~48-53% | Mejora ~3-5% sobre Poisson básico |
| Elo (World Football) | ~55-60% en selecciones | No genera marcadores exactos |
| xG + Poisson | ~50-55% | Mejora con datos de alta calidad |
| ML avanzado (XGBoost, etc.) | ~50-58% | Alto riesgo de overfitting |

**Nota**: La precisión en predicción de fútbol rara vez supera el 55-60% para 1X2 debido a la alta varianza inherente del deporte. Un ROI sostenible en apuestas suele ser de 3-8% anual incluso para los mejores modelos.

---

## URLs de Fuentes Consultadas

- https://pubmed.ncbi.nlm.nih.gov/35588428/ - Penn et al. (2022) Double Poisson para Euro 2020
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9119507/ - Artículo completo PLoS ONE
- https://exprysm.com/insights/methodology/dixon-coles-model.html - ExPrysm Dixon-Coles explicado
- https://en.wikipedia.org/wiki/World_Football_Elo_Ratings - Wikipedia ELO fútbol
- https://www.eloratings.net/about - World Football Elo Ratings oficial
- https://courses.cs.vt.edu/cs5824/Fall15/project_reports/sullivan_cronin.pdf - Estudio Elo Virginia Tech
- https://statsultra.com/football-club-strength-ratings - Strength ratings y SPI
- https://www.tandfonline.com/doi/full/10.1080/01605682.2024.2323669 - Nuevo modelo xG (Cefis & Carpita)
- https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0312278 - xG con secuencias de eventos
- https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1504362/full - xG Bayesiano
- https://urazakgul.github.io/datafc-blog/posts/en/post3/better-predictions-for-football-matches-how-does-the-dixon-coles-model-work.html - Tutorial Dixon-Coles
- https://www.jstor.org/stable/4128211 - Karlis-Ntzoufras (2003) bivariate Poisson
- https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1467-9574.1982.tb00782.x - Maher (1982) original
- https://github.com/giuliofantuzzi/BayesianFootballModelling - Implementación Skellam bayesiano
- https://opisthokonta.net/?p=890 - Dixon-Coles en R (blog)
- https://footballxg.com/xgmodels - xG Models y rentabilidad
- https://www.golsinyali.com/en/blog/statistical-football-predictions - Guía general modelos estadísticos
- https://pena.lt/y/2025/03/10/which-model-should-you-use-to-predict-football-matches - Comparativa de modelos
- https://www.r-bloggers.com/2026/02/football-betting-model-in-r-step-by-step-guide-2026/ - Guía R modelos
