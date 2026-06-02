# Plan de Implementación: Partidos Hoy — v1.0

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> 
> **v1.0 = Copa del Mundo 2026 (104 partidos, 48 selecciones).** Después del 19 de julio se expandirá a más ligas bajo la marca Partidos Hoy.

**Goal:** v1.0 enfocada exclusivamente en la **Copa del Mundo 2026**. Pipeline Python en GitHub Actions genera predicciones ELO desde fixtures hardcodeados (`data/fixtures_wc2026.json`) + ratings de eloratings.net (`data/team_ratings.json`). Plugin WordPress consume el JSON vía shortcode para nuestro sitio. Producto: **Partidos Hoy - Pronósticos de Fútbol**, alojado en partidoshoy.futbol.

**Architecture:** Fuente única de datos: fixtures hardcodeados en `data/fixtures_wc2026.json` (104 partidos del Mundial). Ratings ELO de selecciones desde eloratings.net (scraping de `World.tsv`, 244 equipos). Predictor ELO con fórmula clásica (home advantage +100, K=400) genera probabilidades 1X2 y expected goals. Sin dependencias de APIs externas ni rate limits. Sin ML. v2.0 post-Mundial añadirá XGBoost con datos históricos de ligas regulares.

**⚠️ POLÍTICA DE FUENTES OFICIALES VERIFICADAS:** Todos los datos factuales (sedes, fixtures, fechas) provienen exclusivamente de fuentes oficiales — **Wikipedia (citando FIFA primary sources)** para sedes del Mundial 2026, **eloratings.net** para ratings ELO. Nunca inventar datos algorítmicamente. Las sedes incorrectas en `fixtures_wc2026.json` fueron corregidas contra Wikipedia Groups A-L (mayo 2026).

**Tech Stack:** Python 3.12, pandas, numpy, requests (scraping eloratings.net), GitHub Actions, PHP 8.x, WordPress 6.x

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

- [ ] **Step 1: Crear estructura de directorios**

```bash
mkdir -p partidos-hoy/.github/workflows
mkdir -p partidos-hoy/src/{models,data}
mkdir -p partidos-hoy/wp-plugin/{includes,assets/css}
mkdir -p partidos-hoy/scripts
cd partidos-hoy
```

- [ ] **Step 2: Crear requirements.txt**

```
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
pytest>=7.4.0
```

- [ ] **Step 3: Crear .gitignore**

```
__pycache__/
*.pyc
.env
.vscode/
.idea/
*.egg-info/
dist/
build/
```

- [ ] **Step 4: Crear src/config.py** (solo ELO, sin APIs externas)

```python
import os
from dataclasses import dataclass


@dataclass
class Config:
    # v1.0: Solo Mundial 2026. Sin APIs externas.
    # Fuente única de fixtures: data/fixtures_wc2026.json
    # Fuente única de ratings: eloratings.net → data/team_ratings.json
    data_dir: str = "data"
    predictions_dir: str = "predictions"

    # ELO
    k_factor: int = 400
    home_advantage: int = 100

    # Pipeline
    prediction_cache_ttl: int = 21600  # 6 horas


config = Config()
```

- [ ] **Step 5: Commit**

```bash
git init
git add -A
git commit -m "chore: initial repo structure with ELO config and dependencies"
```

---

### Tasks 2–11 (Eliminadas)

Estas tareas del plan original describían módulos que **no se implementaron** porque las APIs/sources no estaban disponibles para el Mundial 2026:

- **Task 2**: Feature definitions (pospuesto a v2.0)
- **Task 3–3d**: API-Football client, FBref scraper, football-data.org client, DataCascade orchestrator — todas las fuentes fallaron para WC 2026
- **Task 4**: Historical data parser (football-data.co.uk no cubre selecciones nacionales)
- **Task 5**: ELO ratings class (reemplazado por EloPredictor simple en `src/models/elo_predictor.py`)
- **Task 6**: Rolling statistics (pospuesto a v2.0 con datos históricos)
- **Task 7**: Feature orchestrator (pospuesto a v2.0)
- **Task 8**: XGBoost trainer (pospuesto a v2.0, sin datos de entrenamiento disponibles)
- **Task 9**: Probability calibrator (pospuesto a v2.0)
- **Task 10**: Prediction generator (integrado en `elo_predictor.py`)
- **Task 11**: End-to-end pipeline (integrado en worldcup-pipeline.yml)

**Código legacy eliminado del repositorio**: `src/data/`, `src/features/`, `src/utils/`, `tests/`, `research_football_predictions/`, `src/models/predictor.py`, `trainer.py`, `calibrator.py`. Ver KNOWLEDGE_BASE.md §4 para el reality check completo.

---

## Fase 2: CI/CD — GitHub Actions

### Task 12: Workflow Mundial 2026 (único workflow)

**v1.0 = SOLO Mundial 2026.** No hay workflow diario para ligas regulares. Este workflow se ejecuta cada 6 horas durante junio-julio 2026 y genera predicciones ELO desde datos locales (fixtures hardcodeados + team_ratings.json). Sin dependencias de APIs externas.

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

permissions:
  contents: write

env:
  PYTHON_VERSION: "3.12"

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

      - name: Generate predictions JSON (ELO-based)
        run: |
          python -c "
          import json
          import pandas as pd
          from src.models.elo_predictor import EloPredictor

          with open('data/fixtures_wc2026.json') as f:
              fixtures = json.load(f)
          df = pd.DataFrame(fixtures)
          predictor = EloPredictor('data/team_ratings.json')
          output = predictor.generate(df)
          with open('predictions/latest.json', 'w') as f:
              f.write(output)
          parsed = json.loads(output)
          print(f'World Cup predictions generated: {len(parsed[\"matches\"])} matches')
          print(f'Model: {parsed[\"model\"]}')
          total_preds = sum(1 for m in parsed['matches'] if m.get('model') == 'elo')
          total_tbd = sum(1 for m in parsed['matches'] if m.get('status') == 'TBD')
          print(f'Predictions: {total_preds}, TBD (knockout): {total_tbd}')
          "

      - name: Deploy to gh-pages
        run: |
          git config user.name 'github-actions'
          git config user.email 'actions@github.com'
          git remote set-url origin https://x-access-token:\${{ secrets.GITHUB_TOKEN }}@github.com/\${{ github.repository }}.git
          git checkout --orphan gh-pages 2>/dev/null || git checkout gh-pages
          cp -r predictions/latest.json .
          git add latest.json
          git commit -m 'deploy: worldcup predictions \$(date +%Y-%m-%d_%H:%M)'
          git push origin gh-pages --force
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
 * Plugin URI:       https://github.com/miravosqueinteresante/partidos-hoy
 * Description:      Pronósticos de fútbol con ranking ELO para el torneo 2026
 * Version:          1.0.0
 * Requires PHP:     7.4
 * Requires at least: 5.0
 * Author:           partidoshoy.futbol
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
Contributors: partidoshoy
Tags: football, soccer, predictions, analytics
Requires at least: 5.0
Tested up to: 6.5
Requires PHP: 7.4
Stable tag: 1.0.0
License: GPLv2 or later

== Description ==

Pronósticos de fútbol generados con el sistema de ranking ELO.
Las predicciones se actualizan automáticamente cada 6 horas.

For informational and entertainment purposes only. Not affiliated with FIFA or any football federation.

== Installation ==

1. Upload the `partidos-hoy` folder to `/wp-content/plugins/`
2. Activate the plugin
3. Use `[partidos-hoy]` shortcode in any post or page

== Frequently Asked Questions ==

= How are predictions generated? =
Using the World Football ELO rating system, which evaluates team strength based on match results, goal differential, and competition importance.

= How often are predictions updated? =
Every 6 hours via automated pipeline.

= Are you affiliated with FIFA? =
No. This plugin is not affiliated with FIFA or any football federation.

== Changelog ==

= 1.0.0 =
* Initial release

== Upgrade Notice ==

= 1.0.0 =
Initial release.
```

---

### Task 14: Cliente de Datos HTTP

**Files:**
- Create: `wp-plugin/includes/class-data-client.php`

- [ ] **Step 1: Implementar PH_Data_Client**

```php
<?php
defined('ABSPATH') || exit;

class PH_Data_Client {
    private $predictions_url;
    private $cache_key = 'ph_predictions_cache';
    private $cache_ttl = 21600;

    public function __construct() {
        $this->predictions_url = 'https://miravosqueinteresante.github.io/partidos-hoy/latest.json';
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
        add_shortcode('partidos-hoy', array($this, 'render'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_styles'));
    }

    public function enqueue_styles() {
        wp_enqueue_style(
            'ph-frontend',
            PH_PLUGIN_URL . 'assets/css/frontend.css',
            array(),
            PH_VERSION
        );
    }

    public function render($atts = array()) {
        $atts = shortcode_atts(array(
            'league' => '',
            'home'   => '',
            'away'   => '',
        ), $atts);

        ob_start();

        if (!empty($atts['home']) && !empty($atts['away'])) {
            $this->render_single_match($atts['home'], $atts['away']);
        } elseif (!empty($atts['league'])) {
            $this->render_league($atts['league']);
        } else {
            $this->render_all();
        }

        $disclaimer = sprintf(
            '<p class="ph-disclaimer">%s &mdash; %s</p>',
            esc_html__('Predicciones generadas por ELO para fines informativos y de entretenimiento', 'partidos-hoy'),
            esc_html__('No afiliado con FIFA ni ninguna federación de fútbol', 'partidos-hoy')
        );

        return ob_get_clean() . $disclaimer;
    }

    private function render_all() {
        $matches = $this->data_client->get_predictions();
        if (empty($matches) || empty($matches['matches'])) {
            echo '<p>' . esc_html__('No predictions available.', 'partidos-hoy') . '</p>';
            return;
        }
        echo '<div class="ph-table-wrap">';
        echo '<table class="ph-table">';
        echo '<thead><tr>';
        echo '<th>' . esc_html__('Date', 'partidos-hoy') . '</th>';
        echo '<th>' . esc_html__('Home', 'partidos-hoy') . '</th>';
        echo '<th>' . esc_html__('Away', 'partidos-hoy') . '</th>';
        echo '<th>' . esc_html__('1', 'partidos-hoy') . '</th>';
        echo '<th>' . esc_html__('X', 'partidos-hoy') . '</th>';
        echo '<th>' . esc_html__('2', 'partidos-hoy') . '</th>';
        echo '<th>' . esc_html__('xG', 'partidos-hoy') . '</th>';
        echo '</tr></thead><tbody>';

        foreach ($matches['matches'] as $match) {
            $this->render_match_row($match);
        }

        echo '</tbody></table>';
        printf(
            '<p class="ph-updated">%s: %s | %s</p>',
            esc_html__('Updated', 'partidos-hoy'),
            esc_html($matches['generated_at']),
            esc_html($matches['model'])
        );
        echo '</div>';
    }

    private function render_league($league_name) {
        $matches = $this->data_client->get_matches_by_league($league_name);
        if (empty($matches)) {
            echo '<p>' . sprintf(
                esc_html__('No predictions available for %s.', 'partidos-hoy'),
                esc_html($league_name)
            ) . '</p>';
            return;
        }
        echo '<div class="ph-table-wrap">';
        echo '<table class="ph-table">';
        echo '<thead><tr>';
        echo '<th>' . esc_html__('Date', 'partidos-hoy') . '</th>';
        echo '<th>' . esc_html__('Home', 'partidos-hoy') . '</th>';
        echo '<th>' . esc_html__('Away', 'partidos-hoy') . '</th>';
        echo '<th>' . esc_html__('1', 'partidos-hoy') . '</th>';
        echo '<th>' . esc_html__('X', 'partidos-hoy') . '</th>';
        echo '<th>' . esc_html__('2', 'partidos-hoy') . '</th>';
        echo '<th>' . esc_html__('xG', 'partidos-hoy') . '</th>';
        echo '</tr></thead><tbody>';

        foreach ($matches as $match) {
            $this->render_match_row($match);
        }

        echo '</tbody></table></div>';
    }

    private function render_single_match($home_team, $away_team) {
        $match = $this->data_client->get_single_match($home_team, $away_team);
        if ($match === null) {
            echo '<p>' . sprintf(
                esc_html__('No prediction found for %s vs %s.', 'partidos-hoy'),
                esc_html($home_team), esc_html($away_team)
            ) . '</p>';
            return;
        }
        echo '<div class="ph-single-match">';
        $this->render_match_row($match);
        echo '</div>';
    }

    private function render_match_row($match) {
        echo '<tr>';
        echo '<td>' . esc_html($match['date']) . '</td>';
        echo '<td class="ph-home">' . esc_html($match['home']) . '</td>';
        echo '<td class="ph-away">' . esc_html($match['away']) . '</td>';

        if (isset($match['probabilities'])) {
            $p = $match['probabilities'];
            echo '<td class="ph-prob">' . sprintf('%.1f%%', $p['home'] * 100) . '</td>';
            echo '<td class="ph-prob">' . sprintf('%.1f%%', $p['draw'] * 100) . '</td>';
            echo '<td class="ph-prob">' . sprintf('%.1f%%', $p['away'] * 100) . '</td>';
        }

        if (isset($match['expected_goals'])) {
            $xg = $match['expected_goals'];
            echo '<td>' . sprintf('%.2f - %.2f', $xg['home'], $xg['away']) . '</td>';
        }

        echo '</tr>';
    }
}
```

- [ ] **Step 2: Encolar estilos frontend**

- [ ] **Step 3: Crear frontend.css**

```css
.ph-table-wrap {
    overflow-x: auto;
    margin: 20px 0;
}
.ph-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}
.ph-table th,
.ph-table td {
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}
.ph-table th {
    background: #f5f5f5;
    font-weight: 600;
}
.ph-table tr:hover {
    background: #f9f9f9;
}
.ph-home { font-weight: 600; }
.ph-away { font-weight: 600; }
.ph-prob { font-family: monospace; text-align: right; }
.ph-updated {
    font-size: 11px;
    color: #999;
    margin-top: 8px;
}
.ph-disclaimer {
    font-size: 11px;
    color: #999;
    margin-top: 12px;
}
```

---

### Task 16: Admin de Configuración

**Files:**
- Create: `wp-plugin/includes/class-admin.php`

- [ ] **Step 1: Implementar PH_Admin**

```php
<?php
defined('ABSPATH') || exit;

class PH_Admin {
    private $data_client;

    public function __construct($data_client) {
        $this->data_client = $data_client;
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_enqueue_scripts', array($this, 'enqueue_admin_styles'));
    }

    public function enqueue_admin_styles($hook) {
        if ($hook !== 'toplevel_page_partidos-hoy') {
            return;
        }
        wp_enqueue_style(
            'ph-admin',
            PH_PLUGIN_URL . 'assets/css/admin.css',
            array(),
            PH_VERSION
        );
    }

    public function add_admin_menu() {
        add_menu_page(
            __('Partidos Hoy', 'partidos-hoy'),
            __('Partidos Hoy', 'partidos-hoy'),
            'manage_options',
            'partidos-hoy',
            array($this, 'render_admin_page'),
            'dashicons-chart-area'
        );
    }

    public function render_admin_page() {
        if (!current_user_can('manage_options')) {
            return;
        }

        $predictions = $this->data_client->get_predictions();

        echo '<div class="wrap">';
        echo '<h1>' . esc_html__('Partidos Hoy - Dashboard', 'partidos-hoy') . '</h1>';

        if (empty($predictions) || empty($predictions['matches'])) {
            echo '<div class="notice notice-warning">';
            echo '<p>' . esc_html__('No predictions data available yet. The pipeline may still be initializing.', 'partidos-hoy') . '</p>';
            echo '</div>';
        } else {
            echo '<div class="notice notice-info">';
            echo '<p>' . sprintf(
                esc_html__('Model: %s | Generated: %s | Total matches: %d', 'partidos-hoy'),
                esc_html($predictions['model']),
                esc_html($predictions['generated_at']),
                count($predictions['matches'])
            ) . '</p>';
            echo '</div>';

            echo '<table class="wp-list-table widefat fixed striped">';
            echo '<thead><tr>';
            echo '<th>' . esc_html__('Date', 'partidos-hoy') . '</th>';
            echo '<th>' . esc_html__('Home', 'partidos-hoy') . '</th>';
            echo '<th>' . esc_html__('Away', 'partidos-hoy') . '</th>';
            echo '<th>' . esc_html__('Status', 'partidos-hoy') . '</th>';
            echo '<th>' . esc_html__('1', 'partidos-hoy') . '</th>';
            echo '<th>' . esc_html__('X', 'partidos-hoy') . '</th>';
            echo '<th>' . esc_html__('2', 'partidos-hoy') . '</th>';
            echo '</tr></thead><tbody>';

            foreach ($predictions['matches'] as $match) {
                echo '<tr>';
                echo '<td>' . esc_html($match['date']) . '</td>';
                echo '<td>' . esc_html($match['home']) . '</td>';
                echo '<td>' . esc_html($match['away']) . '</td>';
                if (isset($match['probabilities'])) {
                    $p = $match['probabilities'];
                    echo '<td><span class="dashicons dashicons-yes" style="color:green"></span></td>';
                    echo '<td>' . sprintf('%.1f%%', $p['home'] * 100) . '</td>';
                    echo '<td>' . sprintf('%.1f%%', $p['draw'] * 100) . '</td>';
                    echo '<td>' . sprintf('%.1f%%', $p['away'] * 100) . '</td>';
                } elseif (isset($match['status']) && $match['status'] === 'TBD') {
                    echo '<td colspan="4"><em>' . esc_html__('TBD (knockout stage)', 'partidos-hoy') . '</em></td>';
                }
                echo '</tr>';
            }

            echo '</tbody></table>';
        }

        echo '<hr>';
        echo '<p class="ph-disclaimer" style="font-size:11px;color:#999;">';
        echo esc_html__('For informational and entertainment purposes only. Not affiliated with FIFA or any football federation.', 'partidos-hoy');
        echo '</p>';
        echo '</div>';
    }
}
```

---

## Fase 4: CRA Compliance (EU Cyber Resilience Act)

### Task 17: security.txt + Vulnerability Disclosure Policy

**Files:**
- Create: `wp-plugin/security.txt`
- Create: `wp-plugin/.well-known/security.txt`

- [ ] **Step 1: Crear security.txt**

```
# Security Policy for Partidos Hoy WordPress Plugin
# https://github.com/miravosqueinteresante/partidos-hoy

Contact: mailto:security@partidoshoy.futbol
Encryption: https://partidoshoy.futbol/pgp-key.txt
Preferred-Languages: en, es
Policy: https://github.com/miravosqueinteresante/partidos-hoy/security/policy
Canonical: https://partidoshoy.futbol/.well-known/security.txt
```

- [ ] **Step 2: Crear Vulnerability Disclosure Policy**

```
# Vulnerability Disclosure Policy - Partidos Hoy

## Scope
This policy applies to:
- The Partidos Hoy WordPress plugin
- The partidoshoy.futbol website
- The predictions JSON endpoint at miravosqueinteresante.github.io

## Reporting a Vulnerability
Send details to: security@partidoshoy.futbol

## What to include
- Description of the vulnerability
- Steps to reproduce
- Affected versions/components
- Any proof of concept (if available)

## Our commitment
- We will acknowledge receipt within 72 hours
- We will provide an initial assessment within 5 business days
- We will work on a fix based on severity
- We will not pursue legal action for good-faith research

## Safe harbor
We consider security research conducted under this policy as:
- Authorized access to our systems
- Exempt from DMCA takedown notices
- Not a violation of our Terms of Service
```

---

## Resumen de Tareas - v1.0 REAL (lo que realmente se implementó)

| # | Componente | Estado | Notas |
|---|------------|--------|-------|
| 1 | Repositorio + Config | ✅ | Config ELO-only, requirements mínimo |
| 2 | Config  (Task 1) | ✅ | `src/config.py` — ELO + directorios |
| 3 | **EloPredictor (fórmula ELO clásica)** | ✅ | Home advantage +100, K=400 → 1X2 + expected_goals |
| 4 | 104 fixtures hardcodeados | ✅ | `data/fixtures_wc2026.json` — 72 grupo + 32 KO |
| 5 | Workflow GHA (cada 6h) | ✅ | Sin steps de diagnóstico, sin API keys |
| 6 | Plugin WordPress | ✅ | Shortcodes, admin, data client |
| 7 | CRA compliance | ✅ | security.txt + VDP + Dependabot |
| 8 | **Schema JSON-LD SportsEvent** | ✅ | v1.1 — rich snippets en Google |
| 9 | **Open Graph + Twitter Cards** | ✅ | v1.1 — sharing en redes sociales |
| 10 | **Filtros grupo/fecha/equipo** | ✅ | v1.1 — atributos en shortcode |
| 11 | **Paginación + búsqueda** | ✅ | v1.1 — navegación entre páginas |
| 12 | **Fallback endpoint** | ✅ | v1.1 — raw.githubusercontent como respaldo |
| 13 | **Healthchecks.io** | ✅ | v1.1 — monitoreo de pipeline |
| 14 | **News sentiment cache** | ✅ | v1.1 — cache + rate limiting |
| 15 | **Historial en Mundiales** | ✅ | v1.1 — 964 partidos 1930-2022 (Fjelstul DB) |
| 16 | **AJAX endpoint histórico** | ✅ | v1.1 — admin-ajax.php + transient cache |
| 17 | **Normalización nombres equipos (histórico)** | ✅ | v1.1 — ph_get_team_variants() mapea USA→United States, etc. |
| 18 | **Texto condensado en histórico** | ✅ | v1.1 — tabla reemplazada por párrafo <br> por partido |
| 19 | **Strip "not applicable" en goleadores** | ✅ | v1.1 — .replace(/^not applicable /, '') |
| 20 | **Paginación: page → ph_page** | ✅ | v1.1 — evita conflicto con query var de WP |
| 21 | **Search/pagination desde $_GET** | ✅ | v1.1 — lee search y ph_page de la URL |
| 22 | **News: 3 queries por partido** | ✅ | v1.1 — home prep + away prep + matchup |
| 23 | **Botón Compartir en tarjetas** | ✅ | v1.1 — WhatsApp, X, copy link (native share fallback) |
| 24 | **Traducción nombres equipos a español** | ✅ | v1.1 — ph_translate_team() en PHP, cubre 2026 e histórico |

**Código legacy eliminado** (existía en el plan original pero NO en producción):
- API-Football client, FBref scraper, football-data.org client
- DataCascade orquestador, XGBoost trainer/calibrator/predictor
- Rate limiter, historical data parser, feature builder, ELO class, rolling stats
- 14 tests legacy, 6 research docs

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
| **data/team_ratings.json** | ✅ 48 selecciones con ELO | Scrapeado de eloratings.net el 1 Jun 2026 |
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

---

## Fase 5: Mejoras v1.1 — SEO, UX, Históricos (Jun 2026)

### Task 18: Schema JSON-LD SportsEvent + Open Graph

**Files:**
- Modified: `wp-plugin/includes/class-shortcode.php`

- [x] **Agregar JSON-LD SportsEvent** en cada match card (render + render_single)
- [x] **Agregar OG/Twitter Cards** via wp_head con detección de shortcode
- [x] Datos incluidos: nombre, fecha, sede, equipos, descripción ELO

### Task 19: Filtros, Paginación y Búsqueda

**Files:**
- Modified: `wp-plugin/includes/class-shortcode.php`
- Modified: `wp-plugin/includes/class-data-client.php`
- Modified: `wp-plugin/assets/css/frontend.css`

- [x] Atributos `group`, `date`, `team`, `search`, `page` en shortcode
- [x] Métodos de filtrado en Data Client
- [x] Input de búsqueda + paginación numérica
- [x] Fallback endpoint configurable en admin

### Task 20: Pipeline — Healthchecks + News Cache

**Files:**
- Modified: `.github/workflows/worldcup-pipeline.yml`
- Modified: `scripts/news_sentiment.py`

- [x] Healthchecks.io ping en workflow (éxito y fallo)
- [x] Filtro de URLs example.com en news_sentiment
- [x] Prompt mejorado (no inventar resultados, temperatura 0.2)
- [x] Rate limiting (time.sleep(1) entre llamadas Tavily)
- [x] Cache de partidos procesados (news_cache.json)
- [x] **3 queries por partido** (v1.1): home squad prep + away squad prep + matchup
- [x] **Deduplicación** por URL entre las 3 queries
- [x] **Prompt enfocado en plantel/preparación** en vez de resultados

### Task 21: Historial en Mundiales

**Files:**
- Created: `scripts/build_historical_data.py`
- Created: `data/historical_wc_data.json` (964 matches, 2.720 goles)
- Created: `data/worldcup_fjelstul.json` (35 MB, fuente original — gitignored)
- Modified: `wp-plugin/partidos-hoy.php` (AJAX handler)
- Modified: `wp-plugin/includes/class-shortcode.php` (JS fetch + tabla HTML)
- Modified: `wp-plugin/assets/css/frontend.css` (estilos acordeón + tabla)

- [x] Descargar Fjelstul World Cup Database (jfjelstul/worldcup)
- [x] Script de conversión → formato propio
- [x] 964 partidos de todos los mundiales 1930-2022
- [x] 2.720 goles con jugadores, minutos, penales, own goals
- [x] AJAX endpoint en WordPress (admin-ajax.php)
- [x] Cache via transients (24h)
- [x] Acordeón en cada match card
- [x] Tabla con año, fase, resultado, goleadores
- [x] **Texto condensado** (v1.1): tabla reemplazada por párrafo `<br>` por partido
- [x] **Strip "not applicable"** (v1.1): .replace(/^not applicable /, '') en goleadores
- [x] **Normalización nombres** (v1.1): ph_get_team_variants() mapea USA, Korea Republic, IR Iran, Czechia, etc.

### Task 22: Botón Compartir en Tarjetas

**Files:**
- Modified: `wp-plugin/includes/class-shortcode.php` (HTML + JS)
- Modified: `wp-plugin/assets/css/frontend.css` (estilos)

- [x] Botón "Compartir" en footer, misma línea que xG (alineado derecha)
- [x] `navigator.share()` en mobile (share sheet nativo)
- [x] Fallback desktop: WhatsApp, X, Copiar link
- [x] Texto: "Predicciones {home} vs {away}" + URL
- [x] Feedback "¡Copiado!" en clipboard por 2 segundos

### Task 23: Bugfixes — Paginación + Histórico

**Files:**
- Modified: `wp-plugin/partidos-hoy.php` (ph_get_team_variants)
- Modified: `wp-plugin/includes/class-shortcode.php` (ph_page, $_GET)

- [x] `page` → `ph_page` para evitar conflicto con query var `page` de WordPress
- [x] Lectura de `$_GET['search']` y `$_GET['ph_page']` en shortcode
- [x] Normalización de nombres de equipos en AJAX handler

---

**Cobertura del spec (v1.1 REAL):**
- ✅ **v1.0 enfocado exclusivamente en Copa del Mundo 2026** 
- ✅ **Producto: Partidos Hoy - Pronósticos de Fútbol** (partidoshoy.futbol)
- ✅ **Branding sin marcas FIFA**: no usa "FIFA", "World Cup", "Mundial" ni "Copa del Mundo" en nombre del producto
- ✅ Pipeline Python completo (fixtures JSON → EloPredictor → JSON → gh-pages)
- ✅ **Fuente única de datos**: eloratings.net (scraping) + fixtures hardcodeados
- ✅ GitHub Actions CI/CD (1 workflow: worldcup-pipeline cada 6h, sin API keys)
- ✅ Plugin WordPress con shortcode y admin
- ✅ Plugin funcional para uso personal
- ✅ CRA compliance (security.txt + VDP + Dependabot)
- ✅ Seguridad WordPress (nonces, capability checks, sanitize, escape)
- ✅ Protección legal FIFA (branding sin marcas, disclaimers, checklists)
- ✅ Presupuesto cero (solo GitHub repo público + scraping eloratings.net)
- ✅ Timeline realista para llegar al Mundial (11 junio)
- ✅ Acentos normalizados (Côte d'Ivoire, Türkiye, Curaçao → lookup correcto)
- ✅ Knockout stages marcados como `status: TBD` en vez de NaN
- ✅ Banner de fecha + estadio en cada tarjeta (venue agregado a fixtures_wc2026.json)
- ✅ News sentiment con Tavily (web search) + Groq (Llama 3.3 70B) — reemplazo de Gemini API

## Feature: Banner de Fecha + Estadio en Tarjetas

**Implementado**: Jun 2026. Cada tarjeta de partido ahora muestra un banner superior oscuro con:
- 🗓️ Fecha formateada (`11 jun 2026`)
- 📍 Estadio y ciudad (`SoFi Stadium, Inglewood, CA`)

**Datos**: El campo `venue` fue agregado a `data/fixtures_wc2026.json` para los 48 partidos de grupos. Los 56 partidos de eliminación (round_of_32 hasta final) tienen `venue: "TBD"` hasta que se definan los emparejamientos.

**Stack visual**:
- Banner azul oscuro (`#1e3a5f`) en la parte superior de cada `.ph-card`
- Tarjeta usa `padding: 0` con elementos internos con `padding: 20px`
- Accordion de noticias usa `margin-top: 12px` (sin márgenes negativos)

**Equipos sin grupo definido** (TBD knockout): El banner no se muestra si `venue === 'TBD'`.

**Arquitectura final (v1.0):**
```
data/fixtures_wc2026.json ──→ EloPredictor ──→ predictions/latest.json ──→ gh-pages ──→ WordPress
data/team_ratings.json ────────↕              (104 matches, prob 1X2, xG)
(elorbitings.net scrape)
```

---

## Checklist de Protección Legal (FIFA/Cumplimiento)

> **Fuente**: Investigación legal FIFA completa en KNOWLEDGE_BASE.md §14 y `../research_legal_fifa/`. Riesgo FIFA: BAJO si se siguen estas reglas.

### Tarea pre-lanzamiento: Verificar cada item antes de publicar

- [ ] **Plugin name**: no contiene "FIFA", "World Cup", "Mundial" ni variantes
- [ ] **Description**: sin marcas registradas. Usar "football predictions", "soccer analytics"
- [ ] **Tags (readme.txt)**: sin `fifa`, `world cup`, `mundial`. Tags seguros: `football`, `soccer`, `predictions`, `analytics`
- [ ] **Disclaimers**: agregar en admin/footer del plugin: "For informational and entertainment purposes only. Not affiliated with FIFA or any football federation."
- [ ] **readme.txt**: incluir disclaimer legal en la descripción
- [ ] **Privacy Policy**: página estándar en el sitio
- [ ] **Términos y Condiciones**: crear página (18+, "as is", sin garantía)
- [ ] **Responsible Gambling**: link a GambleAware o equivalente en el shortcode output
- [ ] **Datos**: NO vender JSON crudo — solo predicciones derivadas
- [ ] **Logos**: NO usar logos de FIFA, federaciones, selecciones, o clubes en el plugin
- [ ] **URL/Dominio**: NO comprar dominios que contengan "FIFA" o "World Cup"
- [ ] **Marketing**: NO usar hashtags #FIFA, #FIFAWorldCup, #FIFAWorldCup2026
- [ ] **CRA compliance**: security.txt + VDP (ya cubierto en Task 17)
- [ ] **Texto precautorio visible**: en footer del shortcode agregar "Not affiliated with FIFA"
- [ ] **eloratings.net fair use**: solo scraping ocasional (1x por día) para datos ELO. No redistribuir datos crudos de eloratings.net
- [ ] **Revisión anual**: marcas FIFA pueden cambiar para 2027+ o próximos mundiales

### Notas de Implementación

| Check | Dónde implementarlo |
|-------|-------------------|
| Disclaimer en footer | `class-shortcode.php:render()` — agregar `<p class="ph-disclaimer">` |
| Disclaimers en admin | `class-admin.php:render_admin_page()` |
| readme.txt disclaimer | En `== Description ==` y `== Frequently Asked Questions ==` |
| Privacy Policy + TOS | Páginas separadas en WordPress (contenido estático) |
| "Not affiliated" | Constante en `partidos-hoy.php` header comment + shortcode |

### Ejemplo de Disclaimer para el Shortcode

```php
// Agregar al final del método render() en class-shortcode.php
$disclaimer = sprintf(
    '<p class="ph-disclaimer" style="font-size:11px;color:#999;margin-top:12px">' .
    '%s — %s</p>',
    esc_html__('Predicciones generadas por ELO para fines informativos y de entretenimiento', 'partidos-hoy'),
    esc_html__('No afiliado con FIFA ni ninguna federación de fútbol', 'partidos-hoy')
);
return ob_get_clean() . $disclaimer;
```
