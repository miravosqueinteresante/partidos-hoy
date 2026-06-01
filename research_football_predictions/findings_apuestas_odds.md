# Investigación sobre Modelos de Apuestas y Conversión Odd-Probabilidad para Fútbol

---

## 1. Tipos de Cuotas (Odds) y Conversión

### Decimales (Europeas)
- Formato estándar en Europa, Australia, Canadá.
- Representan el retorno total por cada 1 unidad apostada (incluye el stake).
- Ejemplo: 2.50 → por cada $1 apostado, retorno total = $2.50 ($1.50 de ganancia + $1 de stake).
- **Probabilidad implícita**: `P = 1 / odds_decimales`

### Fraccionarias (Británicas)
- Comunes en UK e Irlanda (especialmente hípica).
- Muestran ganancia relativa al stake: 3/1 → ganas $3 por cada $1 apostado.
- **Probabilidad implícita**: `P = denominador / (numerador + denominador)`
- **A decimal**: `(numerador/denominador) + 1`

### Americanas (Moneyline)
- Formato estándar en EE.UU.
- **Negativas (-150)**: muestra cuánto hay que apostar para ganar $100.
- **Positivas (+200)**: muestra cuánto se gana con una apuesta de $100.
- **Probabilidad implícita** (negativas): `P = |odds| / (|odds| + 100)`
- **Probabilidad implícita** (positivas): `P = 100 / (odds + 100)`

### Tabla de conversión rápida
| Americana | Decimal | Fraccionaria | Prob. Implícita |
|-----------|---------|--------------|-----------------|
| -200      | 1.50    | 1/2          | 66.7%           |
| -150      | 1.67    | 2/3          | 60.0%           |
| -110      | 1.91    | 10/11        | 52.4%           |
| +100      | 2.00    | 1/1          | 50.0%           |
| +150      | 2.50    | 3/2          | 40.0%           |
| +200      | 3.00    | 2/1          | 33.3%           |
| +500      | 6.00    | 5/1          | 16.7%           |

**Fuentes:**
- https://marketmath.io/tools/odds-converter
- https://oddsindex.com/guides/how-to-convert-odds
- https://www.covers.com/tools/odds-converter

---

## 2. Probabilidad Implícita, Overround/Vig/Juice y Métodos para Quitarlo

### Overround (Vig / Juice)
- Es el margen de beneficio que incorpora la casa de apuestas.
- Se calcula sumando las probabilidades implícitas de todos los resultados. El exceso sobre 100% es el margen.
- Ejemplo: mercado -110/-110 → 52.38% + 52.38% = 104.76% → margen del 4.76%.

### Métodos para quitar el vig (Devigging)

#### 1. Método Multiplicativo (Basic / Normalización)
- Divide cada prob. implícita por la suma total.
- `P_justa = P_implícita / suma(P_implícitas)`
- **Ventaja**: Simple, funciona bien en mercados balanceados.
- **Desventaja**: Ignora el *favorite-longshot bias* (sesgo favorito-longshot).

#### 2. Método Power (Logarítmico)
- Eleva cada prob. implícita a una potencia `k` hasta que sumen 1.
- `P_justa = (P_implícita)^k`, donde `Σ(P_implícita)^k = 1`
- La `k` se resuelve numéricamente (Newton o búsqueda binaria).
- **Ventaja**: Corrige el favorite-longshot bias. Asigna más probabilidad al favorito.
- **Recomendado**: Por defecto para la mayoría de mercados, especialmente con odds disparejos.

#### 3. Método de Shin (1992)
- Modela la presencia de apostadores con información privilegiada (insiders).
- Estima un parámetro `z` (fracción de insider trading, típicamente 0.01-0.10).
- Fórmula: `P_justa = (√(z² + 4(1-z)·q_i²/B) - z) / (2(1-z))`
- **Ventaja**: Gold standard académico. Mejor para mercados con favorite-longshot bias pronunciado (hípica, mercados multi-resultado).
- **Desventaja**: Complejidad computacional. Puede fallar en mercados de 3 vías como fútbol.

#### 4. Método Aditivo
- Resta una porción igual del overround a cada resultado.
- `P_justa = P_implícita - (overround / n_resultados)`
- **Desventaja**: Puede producir probabilidades negativas en odds extremos. Principalmente histórico.

### Recomendaciones prácticas
- **Mercados 2-vías balanceados**: Multiplicativo es suficiente.
- **Mercados 2-vías disparejos**: Power method.
- **Fútbol 1X2**: Power o Shin (el empate está ligeramente infravalorado).
- **Mercados multi-resultado (10+)**: Shin es el más preciso.
- **Siempre usar odds de casas sharp** (Pinnacle) como referencia.

**Fuentes:**
- https://comparenbet.org/guide-devigging-methods
- https://thewagertheorem.com/de-vig-odds-methods-guide/
- https://www.sharkbetting.com/blog/devig-explained
- https://cran.r-project.org/web/packages/implied/vignettes/introduction.html

---

## 3. Value Betting y Expected Value (EV)

### ¿Qué es Value Betting?
Es la estrategia de apostar solo cuando las cuotas ofrecidas por la casa son mayores que las cuotas "justas" (basadas en tu probabilidad estimada).

### Cálculo del Expected Value (EV)
```
EV = (probabilidad_estimada × odds_decimales) - 1
```
- **EV > 0**: Apuesta con valor positivo (+EV)
- **EV = 0**: Punto de equilibrio
- **EV < 0**: Apuesta con valor negativo (-EV)

### Ejemplo
- Tu modelo estima 30% de probabilidad de empate.
- La casa ofrece odds 3.50 (prob. implícita 28.6%).
- `EV = (0.30 × 3.50) - 1 = 0.05 = +5%`
- Tienes un 5% de valor esperado positivo.

### Break-even probability
```
P_break_even = 1 / odds_decimales
```
Si tu probabilidad estimada es mayor que la de break-even, tienes EV positivo.

**Fuentes:**
- https://mytimecalculator.com/odds-converter-calculator
- https://agentbets.ai/guides/sports-betting-math-101/

---

## 4. Calibración de Modelos de Probabilidad

### ¿Por qué es importante?
Un modelo puede tener buena exactitud (accuracy) pero probabilidades mal calibradas. Por ejemplo, predecir "70% local" cuando solo gana el 45% de las veces. Para value betting, la calibración es crítica porque el Kelly Criterion depende de probabilidades precisas.

### Platt Scaling
- Método paramétrico que ajusta una regresión logística sobre los outputs del modelo.
- `P_calibrada = 1 / (1 + exp(A × score + B))`
- **Cuándo usarlo**: Datos de calibración limitados (100-500 muestras), sesgo de calibración uniforme.
- **Ventaja**: Simple, robusto, bajo riesgo de overfitting.
- **Desventaja**: Asume que el error de calibración tiene forma sigmoide.

### Isotonic Regression
- Método no paramétrico que aprende una función monótona creciente que mapea predicciones crudas a calibradas.
- **Cuándo usarlo**: Datos abundantes (500+ muestras), errores de calibración complejos/no lineales.
- **Ventaja**: Flexible, corrige cualquier patrón de mala calibración.
- **Desventaja**: Mayor riesgo de overfitting con pocos datos.

### Temperature Scaling
- Escala los logits del modelo dividiendo por un escalar T (temperature).
- `P_calibrada = softmax(logits / T)`, donde T > 1 reduce confianza, T < 1 la aumenta.
- **Cuándo usarlo**: Redes neuronales, datos limitados (100-500).

### Expected Calibration Error (ECE)
- Métrica estándar para medir calibración.
- Agrupa predicciones en bins y calcula la diferencia promedio entre frecuencia predicha y real.
- **ECE < 0.05**: Bien calibrado. **ECE < 0.02**: Excelente.

### Evidencia empírica
- Un estudio de la Bundesliga 2014-2025 mostró que un modelo xG-Skellam + isotonic regression logró ~10% ROI (15% con mejores odds), mientras que sin calibración solo ~1% ROI.
- Otro estudio (La Liga 2024-25) mostró que la calibración convirtió -8.5% ROI en +32.5% ROI.

**Fuentes:**
- https://exprysm.com/insights/methodology/model-calibration.html
- https://diegogrebate.com/briefs/temperature-vs-isotonic
- https://www.sportbotai.com/blog/sports-model-calibration-explained-1777716121241
- https://journals.sagepub.com/doi/10.1177/22150218261416681

---

## 5. Mercado Asiático

### Asian Handicap
- Sistema que elimina el empate dando un handicap virtual a los equipos.
- Convierte un mercado de 3 resultados (1X2) en uno de 2 resultados.
- **Handicaps enteros** (0, ±1, ±2): Si el resultado ajustado es empate, el stake se devuelve (push).
- **Handicaps medios** (±0.5, ±1.5): No hay empate posible. Ganas o pierdes completamente.
- **Handicaps de cuarto** (±0.25, ±0.75): El stake se divide en dos apuestas (mitad en el entero inferior, mitad en el superior). Posibilidad de ganar/perder la mitad.

### Tabla de handicaps comunes
| Handicap | Significado |
|----------|-------------|
| -0.5     | El equipo debe ganar por 1+ goles |
| -0.25    | Mitad en 0, mitad en -0.5 |
| 0.0      | Draw No Bet (empate = devolución) |
| +0.5     | El equipo no debe perder |
| +0.75    | Mitad en +0.5, mitad en +1.0 |

### Asian Goal Lines (Over/Under)
- Similar al Asian Handicap pero sobre el total de goles.
- Líneas como 2.25, 2.75, etc. dividen el stake.
- Ejemplo: Over 2.25 → $50 en Over 2.0, $50 en Over 2.5.

### Ventajas
- **Menor margen**: Las casas suelen tener márgenes más bajos (2-3% vs 5-7% en 1X2).
- **Menos varianza**: Los handicaps de cuarto suavizan los resultados.
- **Sin empate**: Reduce resultados posibles de 3 a 2.

**Fuentes:**
- https://champsbase.com/en/sports-betting/guide/bet-types/asian-handicap/
- https://www.covers.com/soccer/how-to-bet-asian-handicap
- https://geckoedge.ai/the-art-of-the-hedge-using-asian-handicaps-for-risk-management/
- https://bettoolkit.com/en/guides/asian-handicap-betting-guide

---

## 6. Modelos de Apuestas: Casas Sharp vs Soft y Betfair Exchange

### Sharp Bookmakers
- **Pinnacle**: El estándar de oro. Márgenes de 2-3% en fútbol. No restringe cuentas ganadoras.
- **SBOBet / IBCBet**: Casas asiáticas sharp. Mercados más profundos en Asian Handicap.
- **Características**: Altos límites, márgenes bajos, ajustes rápidos de línea, aceptan apostadores profesionales.

### Soft Bookmakers (Recreacionales)
- **Bet365, William Hill, Ladbrokes, DraftKings, FanDuel, BetMGM**: Ejemplos típicos.
- **Características**: Márgenes altos (5-8%), restringen cuentas ganadoras, ofrecen bonos, más mercados exóticos.
- **Estrategia**: Usar líneas de soft books para encontrar value vs las líneas sharp.

### Betfair Exchange
- Mercado peer-to-peer donde los usuarios apuestan entre sí.
- **Back** (apostar a favor) y **Lay** (apostar en contra).
- Comisión sobre ganancias netas (típicamente 2-5%).
- Sin restricciones a ganadores.
- Líquidez variable según el partido (PL Big Six: spread 3.7-5%; partidos menores: 8-10%).

### Precisión de odds: Bet365 vs Betfair (Estudio 2024-2026)
- **ECE (Expected Calibration Error)**: Bet365: 1.21%, Betfair Exchange: 1.72%.
- **Brier Score**: Bet365: 0.1935, Betfair: 0.1934 (casi idénticos).
- **Conclusión**: Ambos están igualmente bien calibrados. La diferencia real es el **costo**, no la precisión.
- El overround de Bet365 es plano (~5.6%); el de Betfair varía (3.7-9.6% según liquidez) + comisión 2-5%.

### Cómo usar esta información
1. Usar **Pinnacle** como referencia de precio justo (quitar su margen con power method).
2. Comparar odds de **soft books** contra la referencia de Pinnacle.
3. Si un soft book ofrece odds > fair odds de Pinnacle → potencial +EV.
4. **Betfair** útil como benchmark independiente, especialmente en mercados líquidos.

**Fuentes:**
- https://www.sharkbetting.com/blog/sharp-books-explained
- https://www.football-data.co.uk/blog/pinnacle_wisdom.php
- https://statsbet.org/blog/prediction-market-odds-efficiency
- https://fanbetodds.com/betting/2026/sharp-vs-soft-bookmakers
- https://agentbets.ai/offshore-sportsbooks/pinnacle/

---

## 7. Kelly Criterion (Gestión de Bankroll)

### Fórmula básica
Para una apuesta binaria con odds decimales `d` y probabilidad estimada `p`:
```
f* = (p × d - 1) / (d - 1)
```
Donde:
- `f*` = fracción del bankroll a apostar
- `p` = probabilidad estimada de ganar
- `d` = odds decimales

### Versión alternativa (edge over odds)
```
f* = p - q/b
```
Donde `q = 1-p`, `b = d-1` (ganancia neta por unidad).

### Ejemplo
- Bankroll: $1000, odds: 3.50, prob. estimada: 30%
- `f* = (0.30 × 3.50 - 1) / (3.50 - 1) = 0.05 / 2.50 = 0.02 = 2%`
- Apuesta recomendada: $20

### Fractional Kelly (Half / Quarter Kelly)
| Estrategia   | Tamaño       | Crecimiento | Var ideal      | Drawdown típico |
|-------------|-------------|-------------|----------------|-----------------|
| Full Kelly  | 100%        | Máximo      | Muy alta       | 50%+            |
| 3/4 Kelly   | 75%         | ~94%        | Moderada-alta  | ~33%            |
| Half Kelly  | 50%         | ~75%        | Moderada       | ~25%            |
| Quarter Kelly | 25%       | ~44%        | Baja           | ~12%            |

- **Half Kelly** es el estándar profesional. Captura ~75% del crecimiento con ~50% de la varianza.
- **Quarter Kelly** recomendado para modelos no validados o principios.

### Propiedades importantes
- Si `f*` ≤ 0, la apuesta es -EV. No apostar.
- Full Kelly tiene 50% de probabilidad de reducir el bankroll a la mitad antes de duplicarlo.
- Half Kelly reduce esa probabilidad a ~11%.
- El Kelly asume apuestas independientes. Para apuestas correlacionadas, reducir el tamaño.

### Gestión práctica de bankroll
- **Límite por apuesta**: 1-5% del bankroll (nunca más del 5%).
- **Límite diario**: 10% del bankroll máximo por día.
- **Unidad estándar**: 1-2% del bankroll.
- **Recalcular** tras cada cambio significativo del bankroll.

**Fuentes:**
- https://en.wikipedia.org/wiki/Kelly_criterion
- https://www.bettingexpert.com/academy/advanced-betting-theory/kelly-criterion-explained
- https://marketmath.io/blog/kelly-criterion-guide
- https://matthewdowney.github.io/uncertainty-kelly-criterion-optimal-bet-size.html

---

## 8. Evaluación del Modelo vs Mercado: Closing Line Value (CLV)

### ¿Qué es CLV?
CLV mide la diferencia entre las odds a las que apostaste y las odds de cierre (closing line) de una casa sharp (Pinnacle).

```
CLV% = (odds_apostadas / fair_odds_cierre - 1) × 100
```

O alternativamente:
```
CLV% = (prob_implícita_cierre - prob_implícita_apuesta) / prob_implícita_apuesta
```

### ¿Por qué es la métrica más importante?
- La **closing line de Pinnacle** es la mejor estimación disponible de la probabilidad real (error de calibración < 1-2%).
- **CLV positivo consistente** = tienes edge real. **CLV negativo** = no tienes edge (aunque ganes apuestas).
- El CLV converge al edge real en **200-500 apuestas**, mientras que el profit/loss necesita **2000+**.
- Las casas usan CLV para identificar y limitar apostadores sharp.

### Benchmarks de CLV
| CLV promedio | Interpretación |
|-------------|----------------|
| < 0%        | EV negativo. Perderás a largo plazo. |
| 0-1%        | Break-even o marginalmente positivo. |
| 1-2%        | Moderadamente rentable. |
| 2-3%        | Fuertemente rentable. Edge real. |
| 3-5%        | Excepcional. Serás limitado rápidamente. |
| > 5%        | Extremadamente raro. Posible error de medición. |

### Relación CLV → ROI esperado (odds -110)
| CLV  | ROI Esperado |
|------|-------------|
| +1%  | ~1.9%       |
| +2%  | ~3.8%       |
| +3%  | ~5.7%       |
| +5%  | ~9.5%       |

### Cómo evaluar si tu modelo tiene edge
1. Genera predicciones para partidos futuros.
2. Antes del inicio, compara tus odds justas con las de Pinnacle.
3. Si Pinnacle ofrece odds mayores que tus justas → potencial +EV.
4. Deposita la apuesta y registra las odds de Pinnacle al cierre.
5. Calcula CLV retrospectivamente.
6. Después de 200-500 apuestas: si CLV promedio > 2% → tu modelo tiene edge genuino.

### Errores comunes
- **Medir CLV contra soft books**: Sus líneas de cierre no son eficientes. Siempre usar Pinnacle.
- **Confundir una apuesta con CLV alto con edge**: El CLV promedio en 200+ apuestas es lo que importa.
- **No quitar el vig**: Siempre usar probabilidades sin margen para calcular CLV.

### Favorite-Longshot Bias (FLB)
- Fenómeno documentado: los mercados sobreprecian a los longshots y subprecian a los favoritos.
- En Premier League: odds que implican ~67% → ganan ~70% (3% infravalorado).
- Odds que implican ~12% → ganan ~9% (3% sobrevalorado).
- Afecta tanto a casas tradicionales como a Betfair Exchange (es un sesgo del apostador, no de la casa).

**Fuentes:**
- https://agentbets.ai/guides/closing-line-value-clv/
- https://probwin.com/guides/closing-line-value-clv-ultimate-metric-measure-your-edge/
- https://www.pinnacle.com/betting-resources/en/betting-strategy/using-the-closing-line-to-test-your-skill-in-betting/7e6jwjm5ykejuwkq
- https://bet2invest.com/blog/Using-The-Closing-Line-To-Test-Your-Skills
- https://statsbet.org/blog/prediction-market-odds-efficiency
- https://www.football-data.co.uk/blog/pinnacle_wisdom.php

---

## Resumen de Recomendaciones Prácticas

1. **Benchmark de probabilidad**: Usar Pinnacle como referencia. Quitar su vig con **Power Method**.
2. **Detección de value**: Comparar odds de soft books vs Pinnacle no-vig. Si odds > fair odds → +EV.
3. **Calibración del modelo**: Usar **Isotonic Regression** si tienes 500+ muestras; **Platt Scaling** si tienes menos.
4. **Tamaño de apuesta**: Usar **Half Kelly** (50% del Kelly completo). Para modelos no validados, Quarter Kelly.
5. **Métrica de desempeño**: Rastrear **CLV contra Pinnacle**. Si CLV promedio > 2% tras 200-500 apuestas, tienes edge.
6. **Mercados preferidos**: Asian Handicap (menores márgenes, menos varianza). Usar casas asiáticas para líneas más sharp.
7. **Limitar sesgos**: El favorite-longshot bias es real y consistente. Ajustar estimaciones para favoritos y longshots.
