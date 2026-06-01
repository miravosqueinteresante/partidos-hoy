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

## 🔒 POLÍTICA DE FUENTES OFICIALES VERIFICADAS (MÁXIMA CRÍTICA)

**MÁXIMA CRÍTICA: Todos los datos factuales (sedes, fixtures, fechas, resultados, alineaciones) deben provenir exclusivamente de fuentes oficiales verificadas (FIFA, federaciones nacionales, Wikipedia citando fuentes primarias de FIFA). Nunca inventar, estimar ni calcular datos con algoritmos heurísticos.**

- **Fuente primaria para fixtures y sedes del Mundial 2026:** Wikipedia (en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_*) — que cita documentos oficiales de FIFA como "FIFA World Cup 26 – Match Schedule" (PDF) y "FIFA World Cup 2026 Regulations" (PDF)
- **Fuente para ratings ELO:** eloratings.net (World.tsv)
- **Nunca** generar datos factuales con scripts algorítmicos de rotación (como el `add_venues.py` original que inventaba sedes)
- **Antes de push:** todo dato factual debe estar verificado contra fuente oficial documentada en el commit o en este documento
- **Si no hay fuente oficial disponible para un dato:** se marca como `TBD` y no se inventan valores

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
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  News Sentiment (Tavily + Groq)                              │ │
│  │  tavily-python → web search → Groq (llama-3.3-70b-versatile) │ │
│  │  → Resumen en español (3 oraciones) por partido              │ │
│  │  → Fuentes reales (ESPN, BBC, Goal, etc.)                   │ │
│  │  → Solo equipos definidos (no TBD)                          │ │
│  │  → API Keys: TAVILY_API_KEY + GROQ_API_KEY (GitHub Secrets) │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                          ↓                                       │
│  predictions/latest.json (104 matches, prob 1X2, xG, news)       │
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
│  ┌─────────────┬──────┬──────┬──────┬──────────────┬──────────┬────────────┐ │
│  │ Partido     │  1   │  X   │  2   │  Goles Esp.  │  Fecha   │  Estadio   │ │
│  ├─────────────┼──────┼──────┼──────┼──────────────┼──────────┼────────────┤ │
│  │ México      │ 73%  │ 21%  │  6%  │  2.04-0.35   │ 11 jun   │ SoFi, LA  │ │
│  │ vs Sudáfrica│      │      │      │              │          │            │ │
│  └─────────────┴──────┴──────┴──────┴──────────────┴──────────┴────────────┘ │
│  + Detalles: expected_goals por equipo                           │
│  + Flags emoji para cada selección (48 equipos)                   │
│  + Fecha + Estadio en banner superior de cada tarjeta             │
│  + Acordeón de noticias con análisis Groq                        │
└─────────────────────────────────────────────────────────────────┘
```

**v1.0 = Copa del Mundo 2026.** Post-Copa (19 julio 2026+) se expandirá a ligas regulares bajo la marca Partidos Hoy.

**¿Qué hace?** Un sistema de pronósticos 100% sobre GitHub + GitHub Actions, enfocado en la Copa del Mundo 2026:
1. **Un workflow de GitHub Actions** se ejecuta cada 6 horas (durante Jun-Jul 2026)
2. **Lee fixtures hardcodeados** de `data/fixtures_wc2026.json` (104 partidos)
3. **Carga ELO ratings** de `data/team_ratings.json` (48 selecciones, scrapeado de eloratings.net)
4. **Genera predicciones con fórmula ELO** (home advantage +100, K=400 → probabilidades 1X2 + xG)
5. **Enriquece con análisis de noticias** vía Tavily (búsqueda web) + Groq (resumen IA con Llama 3.3 70B, 3 oraciones en español) + fuentes reales
6. **Publica `latest.json`** en GitHub Pages para que WordPress lo consuma
7. **El plugin de WordPress** lee ese JSON y lo muestra en el sitio web con banner de fecha/estadio, flags emoji, barras de probabilidad, y acordeón de noticias
8. **API Keys de Tavily + Groq** almacenadas como GitHub Secrets (`TAVILY_API_KEY`, `GROQ_API_KEY`), nunca en código

**Caso de uso típico**: Durante un Mundial, el workflow de Actions se ejecuta cada 6 horas. Calcula probabilidades ELO para cada partido basándose en el rating histórico de cada selección (eloratings.net). Luego, para los partidos con equipos definidos, consulta Tavily (búsqueda web) y Groq (resumen IA en español) para generar resúmenes con fuentes reales. El JSON enriquecido se despliega a gh-pages. El plugin de WordPress las muestra automáticamente en tarjetas premium con banner de fecha/estadio y acordeón de noticias expandible.

### ⚠️ Nota sobre fuentes de datos

El plan original contemplaba 3 fuentes en cascada (API-Football → FBref → football-data.org). En la práctica:
- **API-Football free tier**: ❌ NO tiene season 2026 (`Free plans do not have access to this season`)
- **FBref vía soccerdata**: ❌ WC 2026 no disponible aún (`is_worldcup_available() = False`)
- **football-data.org free**: ❌ No incluye World Cup
- **ClubElo (soccerdata)**: ❌ Solo clubes, no selecciones nacionales
- **eloratings.net/World.tsv**: ✅ Scraping libre, sin rate limit, 244 equipos nacionales
- **Fixtures hardcodeados**: ✅ 104 partidos del calendario oficial, con venue para cada partido
- **Tavily (web search) + Groq (LLM)**: ✅ Búsqueda web gratuita (1000 searches/mes) + resumen IA gratuito (30 req/min, modelo llama-3.3-70b-versatile). Tavily busca noticias recientes y Groq genera resúmenes en español. API keys almacenadas como GitHub Secrets (`TAVILY_API_KEY`, `GROQ_API_KEY`), nunca en código.

La arquitectura real v1.0 usa las fuentes que ✅ funcionan.

## 4. APIs, Datos y Librerías

### 4.1 APIs de Datos

> **Filtro de presupuesto cero**: Solo las opciones marcadas como "GRATIS" o con plan free viable son aceptables. Sportmonks y planes de pago de otras APIs quedan descartados automáticamente.
>
> **v1.0 = SOLO Mundial 2026.** ⚠️ Realidad verificada: las 3 fuentes previstas (API-Football, FBref, football-data.org) **NO funcionan para WC 2026** en plan free. La fuente real es **eloratings.net** (scraping de World.tsv, 244 equipos) + fixtures hardcodeados en `data/fixtures_wc2026.json` (104 partidos). Las fuentes de ligas regulares se integrarán en v2.0 post-Mundial.

| Fuente | Costo/mes Real | Cobertura (plan free) | Rate Limit | Rol en v1.0 |
|--------|---------------|----------------------|------------|-------------|
| **API-Football** | $0 (Free) | 1226 ligas, **pero season=2026 NO disponible en free tier** | 100 req/día | ❌ Para WC 2026 |
| **eloratings.net** | **$0** (scraping) | **World Football Elo Ratings de TODAS las selecciones** | Sin límite | 🥇 Primaria |
| **Tavily (web search)** | **$0** (Free) | **1000 searches/mes** — búsqueda web para noticias de fútbol | 1000/mes | 🥈 News search |
| **Groq (LLM)** | **$0** (Free) | **30 req/min** — modelo llama-3.3-70b-versatile | 30/min | 🥉 AI summaries |
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

`eloratings.net` (scraping World.tsv) + `Tavily` (web search) + `Groq` (llama-3.3-70b-versatile) + `data/fixtures_wc2026.json` (104 partidos con venue) + `EloPredictor` (fórmula ELO clásica)

**Para v2.0 (post-Mundial):** `soccerdata` + `API-Football Free` + `mplsoccer` + datasets Kaggle/GitHub + `football-data.co.uk`

---

## 5. Seguridad y uso de APIs

### 5.1 Tavily + Groq (News Sentiment)

- **Claves de API**: Se almacenan como GitHub Secrets (`TAVILY_API_KEY`, `GROQ_API_KEY`) y nunca se suben a código
- **Desarrollo local**: Se leen de `.env` (gitignored) para pruebas
- **GitHub Actions**: Se inyectan desde `secrets.TAVILY_API_KEY` y `secrets.GROQ_API_KEY` al entorno del workflow
- **Uso responsable**:
  - Solo se usa para enriquecer partidos con equipos definidos (no TBD)
  - Máximo 3 fuentes reales por respuesta
  - Resumen de exactamente 3 oraciones en español
  - No se redistribuyen datos crudos de eloratings.net, Tavily ni Groq
  - Costo: Gratis (Tavily 1000 searches/mes, Groq 30 req/min) para el volumen esperado (<100 llamadas/día)

### 5.2 Protección legal

La integración con Tavily + Groq cumple con:
- **TOS de Tavily**: Uso permitido en aplicaciones no comerciales y comerciales bajo free tier
- **TOS de Groq**: Uso permitido bajo free tier con modelo llama-3.3-70b-versatile
- **Fair use**: Solo resúmenes y enlaces, no reproducción completa de contenido
- **Atribución implícita**: Los enlaces dirigen a las fuentes originales

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
- [ ] **Descripción**: "Pronósticos de fútbol con ELO" (sin marcas FIFA)
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
