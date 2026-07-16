# Spec: Resultados Post-Partido y Comparación vs Predicciones

Fecha: 2026-06-03

## Objective

Agregar un panel de administración en WordPress para cargar resultados reales de partidos del Mundial 2026, compararlos automáticamente con las predicciones ELO mostradas en las tarjetas, y mostrar estadísticas de precisión. El usuario del panel es el administrador del sitio; los visitantes ven la precisión en el frontend.

## Success Criteria

- **SC1:** El admin puede guardar el marcador (goles local + visitante) para cualquier partido del fixture desde Ajustes → Partidos Hoy y ver la actualización inmediata en el frontend.
- **SC2:** Las tarjetas de partidos finalizados muestran el score reemplazando el "vs", un badge "✅ Finalizado", y un acordeón de comparación predicción vs resultado con ✅/❌.
- **SC3:** Las estadísticas de precisión (acertados/total/porcentaje, desglose por grupo y KO) se calculan correctamente y se muestran tanto en el admin como en el frontend.

## 1. Almacenamiento

Opción `ph_match_results` en WordPress Options API. Array indexado por **match ID numérico** (el campo `id` de cada match en `predictions/latest.json`) para evitar colisiones y problemas con caracteres especiales en nombres de equipos.

```php
array(
  1 => array('home_goals' => 2, 'away_goals' => 0),
  2 => array('home_goals' => 1, 'away_goals' => 1),
)
```

**API privada:** el option key es un detalle de implementación. Todo acceso debe ser a través de `PH_Data_Client`.

## 2. Interfaz de Data Client (`includes/class-data-client.php`)

Tres métodos nuevos:

```php
/**
 * Retorna todos los resultados guardados.
 * @return array Keyeado por "{date}_{home}_{away}"
 */
public function get_match_results(): array

/**
 * Guarda resultados. Cada entrada validada antes de persistir.
 * @param array $results  [key => ['home_goals' => int, 'away_goals' => int]]
 * @return bool True si se guardó correctamente
 * @throws InvalidArgumentException si algún valor no pasa validación
 */
public function save_results(array $results): bool

/**
 * Calcula estadísticas de precisión cruzando predicciones vs resultados.
 * @param array $matches  Array de matches desde get_predictions()
 * @return array Con claves: total, correct, pct, groups (A-H y KO), last_match
 */
public function calculate_accuracy(array $matches): array
```

### Validación de datos en `save_results()`

- `home_goals` y `away_goals`: `absint()` obligatorio, rechazar negativos y strings no numéricos.
- Key: debe coincidir con patrón `/^[0-9]{4}-[0-9]{2}-[0-9]{2}_[a-z_]+$/`. Usar `sanitize_text_field()`.
- Rechazar entradas con keys que no correspondan a ningún fixture conocido.

### Formato de retorno de `calculate_accuracy()`

```php
array(
  'total' => 15,
  'correct' => 12,
  'pct' => 80.0,
  'groups' => array(
    'A' => array('total' => 3, 'correct' => 2, 'pct' => 66.7),
    'B' => array('total' => 3, 'correct' => 3, 'pct' => 100.0),
    // ... A-H + 'KO'
  ),
  'last_match' => array(
    'home' => 'Brazil',
    'away' => 'Uruguay',
    'home_goals' => 1,
    'away_goals' => 0,
    'correct' => true,
  ),
)
```

Si no hay resultados, retorna `array('total' => 0, 'correct' => 0, 'pct' => 0.0, 'groups' => array(), 'last_match' => null)`.

## 3. Lógica de Acierto

```php
$probs = $match['probabilities']; // ['home' => 0.73, 'draw' => 0.21, 'away' => 0.06]
$max_prob = max($probs);
$max_keys = array_keys($probs, $max_prob);

if (count($max_keys) > 1) {
    // Empate en probabilidades → no se considera acierto ni error
    $predicted = 'uncertain';
} else {
    $predicted = $max_keys[0]; // 'home' | 'draw' | 'away'
}

$actual = $home_goals > $away_goals ? 'home' : ($away_goals > $home_goals ? 'away' : 'draw');

if ($predicted === 'uncertain') {
    $correct = 'uncertain';
} else {
    $correct = ($predicted === $actual);
}
```

Si `$probs` está vacío o el match no existe en predicciones, no se cuenta en las estadísticas.

## 4. Página de Admin (Ajustes → Partidos Hoy)

### Dashboard de precisión (arriba de todo)

```
📊 Precisión: 12/15 (80%)
  Grupo A: 3/4 (75%) | Grupo B: 2/3 (67%) | Grupo C: 3/3 (100%) | ...
  Fase KO: 3/5 (60%)
  Último: Brasil 1-0 Uruguay → ✅ Acertado
```

Si no hay resultados cargados: muestra "No hay resultados cargados todavía. Los resultados aparecerán aquí a medida que los ingreses."

### Gestión de resultados con pestañas

```
[ Grupo A | Grupo B | Grupo C | Grupo D | Grupo E | Grupo F | Grupo G | Grupo H | Fase KO ]
┌──────────────────────────────────────────────────────────────┐
│ Partido              │ Predicción  │ Goles         │ Estado  │
├──────────────────────────────────────────────────────────────┤
│ México vs Sudáfrica  │ 🇲🇽 73%     │ [2] - [0]     │ ✅      │
│ Canada vs Bosnia     │ 🇨🇦 45%     │ [_] - [_]     │ ⏳      │
└──────────────────────────────────────────────────────────────┘
[ Guardar resultados ]
```

- Inputs numéricos inline (`<input type="number" min="0">`)
- Fila se resalta en verde si tiene resultado completo
- Nonce: `wp_nonce_field('ph_save_results', 'ph_results_nonce')`
- Capability check: `current_user_can('manage_options')`
- El `$_POST` se procesa con `check_admin_referer('ph_save_results', 'ph_results_nonce')`

### Seguridad

- CSRF: nonce verification en cada save
- Capability: `manage_options` en el handler
- Input: `absint()` en goles, `sanitize_text_field()` en keys
- Output: `esc_html()` / `esc_attr()` en todos los valores renderizados

## 5. Tarjetas (Frontend)

### Header condicional

Si el match tiene resultado:

```
[✅ Finalizado]
México  2 - 0  Sudáfrica
```

En vez de `México vs Sudáfrica`. El badge "✅ Finalizado" va en el banner junto a fecha/venue.

### Acordeón "📊 Resultado vs Predicción"

Solo visible si el match tiene resultado. Usa `<details>/<summary>` como los acordeones existentes.

```
Predicción:   🇲🇽 México 73% | 🤝 Empate 21% | 🇿🇦 Sudáfrica 6%
Resultado:    2-0 → ✅ Acertado (se pronosticó México)
```

- Barra visual que resalta el outcome que ocurrió
- Texto en verde ✅ / rojo ❌ / gris si incierto
- Todos los strings con `__()` / `_e()` para i18n

### Stats globales arriba de la grilla

Solo si hay ≥1 resultado cargado:

```
📊 Precisión de predicciones: 12/15 (80%)
```

## 6. Estados vacíos y edge cases

| Escenario | Admin | Frontend |
|---|---|---|
| Sin resultados cargados | "No hay resultados todavía" | Stats globales no se muestran |
| Partido sin resultado | Inputs vacíos, fila sin badge | Header normal "vs", sin acordeón |
| Partido con solo 1 gol ingresado | El otro input vacío → no se guarda | No aplica (validación impide) |
| Key inválida en POST | Se rechaza, no se persiste | No aplica |
| Empate en probabilidades | — | Se muestra "🤷 Incierto" en vez de ✅/❌ |

## 7. Testing Strategy

- Framework: PHPUnit (o WP_Mock si no hay test suite existente)
- Cobertura objetivo para `calculate_accuracy()`:
  - Todos los pronósticos acertados → 100%
  - Todos fallados → 0%
  - Mixto → porcentaje correcto
  - Empate en probabilidades → se omite del conteo
  - Array vacío → stats en cero
  - Match sin resultado en `ph_match_results` → no se cuenta
- Cobertura para `save_results()`:
  - Input válido → se persiste
  - Goles negativos → rechazado
  - Key mal formada → rechazado
  - Array vacío → OK (no hay nada que persistir)

## 8. i18n

Todos los strings nuevos visibles al usuario deben usar `__()`, `_e()`, `esc_html__()`, siguiendo el patrón del código existente. Text domain: `partidos-hoy`.

## 9. No-cambios

- Pipeline GHA: no se toca
- `predictions/latest.json`: no se toca
- `fixtures_wc2026.json`: no se toca
- `partidos-hoy.php`: no se toca (solo carga archivos)

## 10. Archivos a modificar (5)

| Archivo | Cambio |
|---|---|
| `includes/class-data-client.php` | +3 métodos: `get_match_results()`, `save_results()` (con validación), `calculate_accuracy()` |
| `includes/class-admin.php` | + dashboard stats + tabla con pestañas por grupo + guardado con nonce + capability check |
| `includes/class-shortcode.php` | + merge resultados en render + header condicional + acordeón comparación + stats globales |
| `assets/css/frontend.css` | + `.ph-result-badge`, `.ph-result-header`, `.ph-comparison-accordion`, `.ph-accuracy-stats` |
| `assets/css/admin.css` | + `.ph-admin-tabs`, `.ph-results-table`, `.ph-admin-stats`, `.ph-score-input` |

## 11. Open Questions

(Pendientes de resolver durante implementación si surgen)
