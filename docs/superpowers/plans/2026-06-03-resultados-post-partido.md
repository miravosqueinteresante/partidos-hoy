# Resultados Post-Partido Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add admin panel to enter post-match results, compare vs ELO predictions, and show accuracy stats.

**Architecture:** Results stored in WordPress Options API (`ph_match_results`), keyed by `{date}_{home}_{away}`. PH_Data_Client gets 3 new methods. Admin page gains dashboard + results form. Shortcode merges results into match data and conditionally displays result+comparison. All new strings use i18n.

**Tech Stack:** WordPress 5.0+, PHP 7.4+, vanilla CSS (no framework).

---

### Task 1: Data Client — get_match_results() + save_results()

**Files:**
- Modify: `wp-plugin/includes/class-data-client.php:1-154`

- [ ] **Step 1: Add get_match_results() and save_results() methods**

Add after `clear_cache()` method (before closing brace):

```php
public function get_match_results(): array {
    $results = get_option('ph_match_results', array());
    return is_array($results) ? $results : array();
}

public function save_results(array $results): bool {
    $clean = array();
    foreach ($results as $key => $data) {
        $key_sanitized = sanitize_text_field(strtolower($key));
        if (!preg_match('/^[0-9]{4}-[0-9]{2}-[0-9]{2}_[a-z_ ]+$/', $key_sanitized)) {
            continue;
        }
        if (!isset($data['home_goals']) || !isset($data['away_goals'])) {
            continue;
        }
        $home = absint($data['home_goals']);
        $away = absint($data['away_goals']);
        if ($data['home_goals'] !== false && $data['away_goals'] !== false) {
            $clean[$key_sanitized] = array(
                'home_goals' => $home,
                'away_goals' => $away,
            );
        }
    }
    $existing = $this->get_match_results();
    $merged = array_merge($existing, $clean);
    return update_option('ph_match_results', $merged);
}
```

- [ ] **Step 2: Verify syntax**

Run: `php -l wp-plugin/includes/class-data-client.php`
Expected: `No syntax errors detected`

- [ ] **Step 3: Commit**

```bash
git add wp-plugin/includes/class-data-client.php
git commit -m "feat: add get_match_results and save_results methods"
```

---

### Task 2: Data Client — calculate_accuracy()

**Files:**
- Modify: `wp-plugin/includes/class-data-client.php:1-154`

- [ ] **Step 1: Add calculate_accuracy() method**

Add after `save_results()`:

```php
public function calculate_accuracy(array $predictions): array {
    $results = $this->get_match_results();
    if (empty($results)) {
        return array(
            'total' => 0,
            'correct' => 0,
            'pct' => 0.0,
            'groups' => array(),
            'last_match' => null,
        );
    }

    $stats = array(
        'total' => 0,
        'correct' => 0,
        'groups' => array(),
        'last_match' => null,
    );

    $last_date = '';

    foreach ($predictions as $match) {
        if (empty($match['probabilities'])) {
            continue;
        }
        $home = $match['home'] ?? '';
        $away = $match['away'] ?? '';
        $date = isset($match['date']) ? substr($match['date'], 0, 10) : '';
        $group = isset($match['group']) ? strtoupper($match['group']) : 'KO';
        $key = strtolower($date . '_' . $home . '_' . $away);

        if (!isset($results[$key])) {
            continue;
        }

        $probs = $match['probabilities'];
        $max_prob = max($probs);
        $max_keys = array_keys($probs, $max_prob);

        if (count($max_keys) > 1) {
            continue;
        }
        $predicted = $max_keys[0];

        $home_goals = $results[$key]['home_goals'];
        $away_goals = $results[$key]['away_goals'];
        $actual = $home_goals > $away_goals ? 'home' : ($away_goals > $home_goals ? 'away' : 'draw');
        $correct = ($predicted === $actual);

        $stats['total']++;
        if ($correct) {
            $stats['correct']++;
        }

        if (!isset($stats['groups'][$group])) {
            $stats['groups'][$group] = array('total' => 0, 'correct' => 0);
        }
        $stats['groups'][$group]['total']++;
        if ($correct) {
            $stats['groups'][$group]['correct']++;
        }

        if ($date > $last_date) {
            $last_date = $date;
            $stats['last_match'] = array(
                'home' => $home,
                'away' => $away,
                'home_goals' => $home_goals,
                'away_goals' => $away_goals,
                'correct' => $correct,
            );
        }
    }

    $stats['pct'] = $stats['total'] > 0
        ? round(($stats['correct'] / $stats['total']) * 100, 1)
        : 0.0;

    foreach ($stats['groups'] as $g => $data) {
        $stats['groups'][$g]['pct'] = $data['total'] > 0
            ? round(($data['correct'] / $data['total']) * 100, 1)
            : 0.0;
    }

    return $stats;
}
```

- [ ] **Step 2: Verify syntax**

Run: `php -l wp-plugin/includes/class-data-client.php`
Expected: `No syntax errors detected`

- [ ] **Step 3: Commit**

```bash
git add wp-plugin/includes/class-data-client.php
git commit -m "feat: add calculate_accuracy method"
```

---

### Task 3: Admin Page — Dashboard + Results Table + Save Handler

**Files:**
- Modify: `wp-plugin/includes/class-admin.php:1-116`
- Create: `wp-plugin/assets/css/admin.css` (or modify if exists)

- [ ] **Step 1: Load predictions data in the admin constructor**

Add property and modify constructor in `class-admin.php`:

```php
class PH_Admin {
    private $data_client;
    private $predictions;

    public function __construct($data_client) {
        $this->data_client = $data_client;
        $this->predictions = $this->data_client->get_predictions();
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));
        add_action('admin_init', array($this, 'handle_save_results'));
        add_action('admin_enqueue_scripts', array($this, 'enqueue_admin_styles'));
    }
```

- [ ] **Step 2: Add handle_save_results() method**

Add before `render_admin_page()`:

```php
public function handle_save_results() {
    if (!isset($_POST['ph_action']) || $_POST['ph_action'] !== 'save_results') {
        return;
    }
    if (!isset($_POST['ph_results_nonce']) || !wp_verify_nonce($_POST['ph_results_nonce'], 'ph_save_results')) {
        return;
    }
    if (!current_user_can('manage_options')) {
        return;
    }

    $results = array();
    if (isset($_POST['ph_results']) && is_array($_POST['ph_results'])) {
        foreach ($_POST['ph_results'] as $key => $data) {
            $key = sanitize_text_field($key);
            if (!preg_match('/^[0-9]{4}-[0-9]{2}-[0-9]{2}_[a-z_ ]+$/', $key)) {
                continue;
            }
            $home_goals = isset($data['home_goals']) && $data['home_goals'] !== '' ? absint($data['home_goals']) : null;
            $away_goals = isset($data['away_goals']) && $data['away_goals'] !== '' ? absint($data['away_goals']) : null;
            if ($home_goals !== null && $away_goals !== null) {
                $results[$key] = array(
                    'home_goals' => $home_goals,
                    'away_goals' => $away_goals,
                );
            }
        }
    }

    if (!empty($results)) {
        $this->data_client->save_results($results);
        add_action('admin_notices', function() {
            echo '<div class="notice notice-success"><p>' .
                 esc_html__('Resultados guardados correctamente.', 'partidos-hoy') .
                 '</p></div>';
        });
    } else {
        add_action('admin_notices', function() {
            echo '<div class="notice notice-info"><p>' .
                 esc_html__('No se ingresaron resultados válidos.', 'partidos-hoy') .
                 '</p></div>';
        });
    }
}
```

- [ ] **Step 3: Add helper methods for grouping + rendering**

Add before `render_admin_page()`:

```php
private function get_matches_by_group($matches, $group) {
    return array_values(array_filter($matches, function($m) use ($group) {
        $g = isset($m['group']) ? strtoupper($m['group']) : 'KO';
        return $g === $group;
    }));
}

private function get_group_labels() {
    return array('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'KO');
}
```

- [ ] **Step 4: Rewrite render_admin_page() with dashboard + results table**

Replace the entire `render_admin_page()` method:

```php
public function render_admin_page() {
    if (!current_user_can('manage_options')) {
        return;
    }

    $results = $this->data_client->get_match_results();
    $accuracy = $this->data_client->calculate_accuracy(
        isset($this->predictions['matches']) ? $this->predictions['matches'] : array()
    );
    $matches = isset($this->predictions['matches']) ? $this->predictions['matches'] : array();

    $selected_group = isset($_GET['ph_group']) && in_array(strtoupper($_GET['ph_group']), $this->get_group_labels())
        ? strtoupper($_GET['ph_group'])
        : 'A';
    ?>
    <div class="wrap">
        <h1><?php echo esc_html__('Partidos Hoy', 'partidos-hoy'); ?></h1>
        <p><em><?php esc_html_e('For informational and entertainment purposes only.', 'partidos-hoy'); ?></em></p>

        <div class="ph-admin-stats">
            <h2><?php esc_html_e('📊 Precisión de predicciones', 'partidos-hoy'); ?></h2>
            <?php if ($accuracy['total'] > 0): ?>
                <p class="ph-accuracy-main">
                    <?php
                    printf(
                        esc_html__('Acertados: %d de %d (%s%%)', 'partidos-hoy'),
                        $accuracy['correct'],
                        $accuracy['total'],
                        $accuracy['pct']
                    );
                    ?>
                </p>
                <div class="ph-accuracy-groups">
                    <?php foreach ($accuracy['groups'] as $group => $data): ?>
                        <span class="ph-group-stat">
                            <?php printf(
                                esc_html__('Grupo %s: %d/%d (%s%%)', 'partidos-hoy'),
                                esc_html($group),
                                $data['correct'],
                                $data['total'],
                                $data['pct']
                            ); ?>
                        </span>
                    <?php endforeach; ?>
                </div>
                <?php if ($accuracy['last_match']): $lm = $accuracy['last_match']; ?>
                    <p class="ph-last-match">
                        <?php printf(
                            esc_html__('Último: %s %d-%d %s — %s', 'partidos-hoy'),
                            esc_html(ph_translate_team($lm['home'])),
                            $lm['home_goals'],
                            $lm['away_goals'],
                            esc_html(ph_translate_team($lm['away'])),
                            $lm['correct'] ? '✅ ' . __('Acertado', 'partidos-hoy') : '❌ ' . __('Falló', 'partidos-hoy')
                        ); ?>
                    </p>
                <?php endif; ?>
            <?php else: ?>
                <p><?php esc_html_e('No hay resultados cargados todavía. Los resultados aparecerán aquí a medida que los ingreses.', 'partidos-hoy'); ?></p>
            <?php endif; ?>
        </div>

        <hr />

        <h2><?php esc_html_e('Resultados', 'partidos-hoy'); ?></h2>

        <div class="ph-admin-tabs">
            <?php foreach ($this->get_group_labels() as $g): ?>
                <a href="<?php echo esc_url(add_query_arg('ph_group', $g)); ?>"
                   class="ph-tab <?php echo $g === $selected_group ? 'ph-tab-active' : ''; ?>">
                    <?php echo $g === 'KO' ? esc_html__('Fase KO', 'partidos-hoy') : sprintf(esc_html__('Grupo %s', 'partidos-hoy'), $g); ?>
                </a>
            <?php endforeach; ?>
        </div>

        <?php $group_matches = $this->get_matches_by_group($matches, $selected_group); ?>

        <?php if (empty($group_matches)): ?>
            <p><?php esc_html_e('No hay partidos en este grupo.', 'partidos-hoy'); ?></p>
        <?php else: ?>
            <form method="post" action="">
                <?php wp_nonce_field('ph_save_results', 'ph_results_nonce'); ?>
                <input type="hidden" name="ph_action" value="save_results" />
                <table class="wp-list-table widefat fixed striped ph-results-table">
                    <thead>
                        <tr>
                            <th><?php esc_html_e('Partido', 'partidos-hoy'); ?></th>
                            <th><?php esc_html_e('Predicción', 'partidos-hoy'); ?></th>
                            <th><?php esc_html_e('Goles', 'partidos-hoy'); ?></th>
                            <th><?php esc_html_e('Estado', 'partidos-hoy'); ?></th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($group_matches as $match):
                            $home = $match['home'] ?? '';
                            $away = $match['away'] ?? '';
                            $date = isset($match['date']) ? substr($match['date'], 0, 10) : '';
                            $key = strtolower($date . '_' . $home . '_' . $away);
                            $probs = $match['probabilities'] ?? array();
                            $max_key = !empty($probs) ? array_search(max($probs), $probs) : '';
                            $max_label = array('home' => $home, 'draw' => __('Empate', 'partidos-hoy'), 'away' => $away);
                            $max_pct = isset($probs[$max_key]) ? round(floatval($probs[$max_key]) * 100) : 0;
                            $flag_home = $this->get_flag_static($home);
                            $has_result = isset($results[$key]);
                            $existing = $has_result ? $results[$key] : null;
                        ?>
                        <tr class="<?php echo $has_result ? 'ph-row-complete' : ''; ?>">
                            <td class="ph-col-match">
                                <?php echo esc_html(ph_translate_team($home)); ?>
                                vs
                                <?php echo esc_html(ph_translate_team($away)); ?>
                            </td>
                            <td class="ph-col-prediction">
                                <?php echo $flag_home . ' ' . esc_html($max_label[$max_key] ?? '') . ' ' . $max_pct . '%'; ?>
                            </td>
                            <td class="ph-col-scores">
                                <input type="number" min="0" max="50" class="ph-score-input"
                                       name="ph_results[<?php echo esc_attr($key); ?>][home_goals]"
                                       value="<?php echo $has_result ? esc_attr($existing['home_goals']) : ''; ?>"
                                       placeholder="<?php esc_attr_e('Local', 'partidos-hoy'); ?>" />
                                <span class="ph-score-sep">-</span>
                                <input type="number" min="0" max="50" class="ph-score-input"
                                       name="ph_results[<?php echo esc_attr($key); ?>][away_goals]"
                                       value="<?php echo $has_result ? esc_attr($existing['away_goals']) : ''; ?>"
                                       placeholder="<?php esc_attr_e('Visit', 'partidos-hoy'); ?>" />
                            </td>
                            <td class="ph-col-status">
                                <?php if ($has_result): ?>
                                    <span title="<?php esc_attr_e('Completado', 'partidos-hoy'); ?>">✅</span>
                                <?php else: ?>
                                    <span title="<?php esc_attr_e('Pendiente', 'partidos-hoy'); ?>">⏳</span>
                                <?php endif; ?>
                            </td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
                <p class="submit">
                    <button type="submit" class="button button-primary">
                        <?php esc_html_e('Guardar resultados', 'partidos-hoy'); ?>
                    </button>
                </p>
            </form>
        <?php endif; ?>

        <hr />

        <h2><?php esc_html_e('Configuración', 'partidos-hoy'); ?></h2>
        <form method="post" action="options.php">
            <?php settings_fields('ph_settings_group'); ?>
            <table class="form-table">
                <tr>
                    <th scope="row">
                        <label for="ph_predictions_url"><?php esc_html_e('URL de predicciones JSON', 'partidos-hoy'); ?></label>
                    </th>
                    <td>
                        <input type="url" id="ph_predictions_url" name="ph_predictions_url"
                               value="<?php echo esc_attr(get_option('ph_predictions_url', '')); ?>"
                               class="regular-text" />
                    </td>
                </tr>
                <tr>
                    <th scope="row">
                        <label for="ph_fallback_url"><?php esc_html_e('URL de respaldo', 'partidos-hoy'); ?></label>
                    </th>
                    <td>
                        <input type="url" id="ph_fallback_url" name="ph_fallback_url"
                               value="<?php echo esc_attr(get_option('ph_fallback_url', '')); ?>"
                               class="regular-text" />
                    </td>
                </tr>
                <tr>
                    <th scope="row">
                        <label for="ph_cache_ttl"><?php esc_html_e('TTL de caché (segundos)', 'partidos-hoy'); ?></label>
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
            <button type="submit" class="button"><?php esc_html_e('Limpiar caché', 'partidos-hoy'); ?></button>
        </form>
        <?php $this->handle_cache_clear(); ?>
    </div>
    <?php
}
```

- [ ] **Step 5: Add get_flag_static() static helper**

Add before `render_admin_page()`:

```php
private function get_flag_static($team_name) {
    $flags = array(
        'Mexico' => '🇲🇽', 'South Africa' => '🇿🇦', 'Korea Republic' => '🇰🇷', 'Czechia' => '🇨🇿',
        'Canada' => '🇨🇦', 'Bosnia and Herzegovina' => '🇧🇦', 'USA' => '🇺🇸', 'Paraguay' => '🇵🇾',
        'Haiti' => '🇭🇹', 'Scotland' => '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'Australia' => '🇦🇺', 'Türkiye' => '🇹🇷',
        'Brazil' => '🇧🇷', 'Morocco' => '🇲🇦', 'Qatar' => '🇶🇦', 'Switzerland' => '🇨🇭',
        "Côte d'Ivoire" => '🇨🇮', 'Ecuador' => '🇪🇨', 'Germany' => '🇩🇪', 'Curaçao' => '🇨🇼',
        'Netherlands' => '🇳🇱', 'Japan' => '🇯🇵', 'Sweden' => '🇸🇪', 'Tunisia' => '🇹🇳',
        'Saudi Arabia' => '🇸🇦', 'Uruguay' => '🇺🇾', 'Spain' => '🇪🇸', 'Cabo Verde' => '🇨🇻',
        'IR Iran' => '🇮🇷', 'New Zealand' => '🇳🇿', 'Belgium' => '🇧🇪', 'Egypt' => '🇪🇬',
        'France' => '🇫🇷', 'Senegal' => '🇸🇳', 'Iraq' => '🇮🇶', 'Norway' => '🇳🇴',
        'Argentina' => '🇦🇷', 'Algeria' => '🇩🇿', 'Austria' => '🇦🇹', 'Jordan' => '🇯🇴',
        'Ghana' => '🇬🇭', 'Panama' => '🇵🇦', 'England' => '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Croatia' => '🇭🇷',
        'Portugal' => '🇵🇹', 'Congo DR' => '🇨🇩', 'Uzbekistan' => '🇺🇿', 'Colombia' => '🇨🇴',
    );
    return isset($flags[$team_name]) ? $flags[$team_name] . ' ' : '';
}
```

- [ ] **Step 6: Verify syntax**

Run: `php -l wp-plugin/includes/class-admin.php`
Expected: `No syntax errors detected`

- [ ] **Step 7: Commit**

```bash
git add wp-plugin/includes/class-admin.php
git commit -m "feat: add results admin panel with tabs, dashboard, and save handler"
```

---

### Task 4: Shortcode — Merge Results + Conditional Header

**Files:**
- Modify: `wp-plugin/includes/class-shortcode.php:1-535`

- [ ] **Step 1: Fetch results at start of render() and render_single()**

In the `render()` method, after getting `$matches` (around line 39), add:

```php
$saved_results = $this->data_client->get_match_results();
```

In `render_single()`, after getting `$match` (around line 244), add:

```php
$saved_results = $this->data_client->get_match_results();
```

- [ ] **Step 2: Add helper method to build result data for a match**

Add to the class:

```php
private function get_match_result(array $match, array $saved_results) {
    $mid = isset($match['id']) ? intval($match['id']) : 0;
    return ($mid > 0 && isset($saved_results[$mid])) ? $saved_results[$mid] : null;
}
```

- [ ] **Step 3: Replace "vs" with score in card header**

In `render()`, around line 101-103, change the card header section:

```php
<?php
$result = $this->get_match_result($match, $saved_results);
$has_result = $result !== null;
?>
<div class="ph-card-header">
    <?php if ($has_result): ?>
        <span class="ph-team ph-home"><?php echo $this->get_flag($home_team) . esc_html($home_team_display); ?></span>
        <span class="ph-score-display"><?php echo intval($result['home_goals']) . ' - ' . intval($result['away_goals']); ?></span>
        <span class="ph-team ph-away"><?php echo $this->get_flag($away_team) . esc_html($away_team_display); ?></span>
    <?php else: ?>
        <span class="ph-team ph-home"><?php echo $this->get_flag($home_team) . esc_html($home_team_display); ?></span>
        <span class="ph-vs">vs</span>
        <span class="ph-team ph-away"><?php echo $this->get_flag($away_team) . esc_html($away_team_display); ?></span>
    <?php endif; ?>
</div>
```

- [ ] **Step 4: Add "✅ Finalizado" badge to banner**

In `render()`, add inside the banner div (around line 91), after `</div>` adding the banner close, before the card header:

```php
<?php if ($has_result): ?>
    <span class="ph-result-badge">✅ <?php esc_html_e('Finalizado', 'partidos-hoy'); ?></span>
<?php endif; ?>
```

- [ ] **Step 5: Repeat header + badge changes in render_single()**

Same as steps 3-4 but in `render_single()` (around lines 265-280).

- [ ] **Step 6: Verify syntax**

Run: `php -l wp-plugin/includes/class-shortcode.php`
Expected: `No syntax errors detected`

- [ ] **Step 7: Commit**

```bash
git add wp-plugin/includes/class-shortcode.php
git commit -m "feat: show match score in header when result exists"
```

---

### Task 5: Shortcode — Comparison Accordion + Global Stats

**Files:**
- Modify: `wp-plugin/includes/class-shortcode.php:1-535`

- [ ] **Step 1: Add accuracy calculation in render()**

After `$saved_results = $this->data_client->get_match_results();` (from Task 4), add:

```php
$accuracy = $this->data_client->calculate_accuracy($matches);
```

- [ ] **Step 2: Add global accuracy stats above search**

In `render()`, after the search form div (around line 74), before the grid div, add:

```php
<?php if ($accuracy['total'] > 0): ?>
<div class="ph-accuracy-bar">
    <?php printf(
        esc_html__('📊 Precisión de predicciones: %d/%d (%s%%)', 'partidos-hoy'),
        $accuracy['correct'],
        $accuracy['total'],
        $accuracy['pct']
    ); ?>
</div>
<?php endif; ?>
```

- [ ] **Step 3: Add helper method for comparison accordion HTML**

Add to the class:

```php
private function render_comparison_accordion(array $match, array $result) {
    $home = $match['home'] ?? '';
    $away = $match['away'] ?? '';
    $probs = $match['probabilities'] ?? array();

    $home_goals = intval($result['home_goals']);
    $away_goals = intval($result['away_goals']);

    $max_prob = !empty($probs) ? max($probs) : 0;
    $max_keys = !empty($probs) ? array_keys($probs, $max_prob) : array();
    $predicted = (count($max_keys) === 1) ? $max_keys[0] : 'uncertain';

    $actual = $home_goals > $away_goals ? 'home' : ($away_goals > $home_goals ? 'away' : 'draw');

    if ($predicted === 'uncertain') {
        $correct = null;
    } else {
        $correct = ($predicted === $actual);
    }

    $labels = array(
        'home' => ph_translate_team($home),
        'draw' => __('Empate', 'partidos-hoy'),
        'away' => ph_translate_team($away),
    );

    ob_start();
    ?>
    <details class="ph-comparison-accordion">
        <summary>📊 <?php esc_html_e('Resultado vs Predicción', 'partidos-hoy'); ?></summary>
        <div class="ph-comparison-content">
            <div class="ph-comparison-prediction">
                <strong><?php esc_html_e('Predicción:', 'partidos-hoy'); ?></strong>
                <?php foreach (array('home', 'draw', 'away') as $key):
                    $pct = isset($probs[$key]) ? round(floatval($probs[$key]) * 100) : 0;
                    $flag = $key === 'home' ? $this->get_flag($home) : ($key === 'away' ? $this->get_flag($away) : '');
                ?>
                    <span class="ph-comp-item <?php echo $key === $actual ? 'ph-comp-actual' : ''; ?>">
                        <?php echo $flag . esc_html($labels[$key]) . ' ' . $pct . '%'; ?>
                    </span>
                    <?php if ($key !== 'away'): ?>
                        <span class="ph-comp-sep">|</span>
                    <?php endif; ?>
                <?php endforeach; ?>
            </div>
            <div class="ph-comparison-result">
                <strong><?php esc_html_e('Resultado:', 'partidos-hoy'); ?></strong>
                <?php printf('%d - %d', $home_goals, $away_goals); ?>
                →
                <?php if ($correct === true): ?>
                    <span class="ph-comp-correct">✅ <?php esc_html_e('Acertado', 'partidos-hoy'); ?>
                        (<?php printf(esc_html__('se pronosticó %s', 'partidos-hoy'), esc_html($labels[$predicted])); ?>)
                    </span>
                <?php elseif ($correct === false): ?>
                    <span class="ph-comp-wrong">❌ <?php esc_html_e('Falló', 'partidos-hoy'); ?>
                        (<?php printf(esc_html__('se pronosticó %s', 'partidos-hoy'), esc_html($labels[$predicted])); ?>)
                    </span>
                <?php else: ?>
                    <span class="ph-comp-uncertain">🤷 <?php esc_html_e('Incierto (probabilidades empatadas)', 'partidos-hoy'); ?></span>
                <?php endif; ?>
            </div>
        </div>
    </details>
    <?php
    return ob_get_clean();
}
```

- [ ] **Step 4: Add comparison accordion to each card in render()**

In `render()`, after the historical accordion (around line 175-181), add:

```php
<?php if ($has_result): ?>
    <?php echo $this->render_comparison_accordion($match, $result); ?>
<?php endif; ?>
```

- [ ] **Step 5: Repeat for render_single()**

Same addition in `render_single()` after the historical accordion.

- [ ] **Step 6: Verify syntax**

Run: `php -l wp-plugin/includes/class-shortcode.php`
Expected: `No syntax errors detected`

- [ ] **Step 7: Commit**

```bash
git add wp-plugin/includes/class-shortcode.php
git commit -m "feat: add comparison accordion and global accuracy stats"
```

---

### Task 6: Frontend CSS — Result badge, score display, accordion, stats

**Files:**
- Read: `wp-plugin/assets/css/frontend.css`
- Modify: `wp-plugin/assets/css/frontend.css` (append)

- [ ] **Step 1: Read existing frontend.css**

Run (or use read tool): `Get-Content wp-plugin/assets/css/frontend.css`

- [ ] **Step 2: Append new styles**

Add at the end of `frontend.css`:

```css
/* === Post-Match Results === */

.ph-result-badge {
    display: inline-block;
    background: #e8f5e9;
    color: #2e7d32;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
    margin-left: 8px;
    vertical-align: middle;
}

.ph-score-display {
    font-size: 1.3rem;
    font-weight: 800;
    color: #1a1a2e;
    margin: 0 12px;
    letter-spacing: 0.05em;
}

.ph-accuracy-bar {
    text-align: center;
    padding: 10px 16px;
    margin-bottom: 16px;
    background: #f0f4ff;
    border-radius: 8px;
    font-size: 0.95rem;
    font-weight: 600;
    color: #1a1a2e;
}

.ph-comparison-accordion {
    border-top: 1px solid #e0e0e0;
}

.ph-comparison-content {
    padding: 12px 16px;
    font-size: 0.85rem;
    line-height: 1.7;
}

.ph-comparison-prediction {
    margin-bottom: 8px;
}

.ph-comparison-prediction strong,
.ph-comparison-result strong {
    display: inline-block;
    margin-right: 6px;
    color: #555;
}

.ph-comp-item {
    padding: 2px 6px;
    border-radius: 3px;
}

.ph-comp-actual {
    background: #fff3e0;
    font-weight: 700;
    border-bottom: 2px solid #ff9800;
}

.ph-comp-sep {
    color: #ccc;
    margin: 0 4px;
}

.ph-comp-correct {
    color: #2e7d32;
    font-weight: 700;
}

.ph-comp-wrong {
    color: #c62828;
    font-weight: 700;
}

.ph-comp-uncertain {
    color: #757575;
    font-style: italic;
}

/* Responsive: admin results table */
@media (max-width: 600px) {
    .ph-score-display {
        font-size: 1.1rem;
        margin: 0 8px;
    }
}
```

- [ ] **Step 3: Verify syntax no-op (CSS has no syntax check)**

Just verify the file is valid.

- [ ] **Step 4: Commit**

```bash
git add wp-plugin/assets/css/frontend.css
git commit -m "style: add post-match result badges, accordion, and accuracy stats"
```

---

### Task 7: Admin CSS — Tabs, table, stats, score inputs

**Files:**
- Create: `wp-plugin/assets/css/admin.css` (add to existing if exists)

- [ ] **Step 1: Read existing admin.css**

Run: `Get-Content wp-plugin/assets/css/admin.css`

- [ ] **Step 2: Create/append admin styles**

```css
/* === Admin Results === */

.ph-admin-stats {
    background: #f0f6fc;
    border: 1px solid #c3d9ff;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 12px 0;
}

.ph-accuracy-main {
    font-size: 1.1rem;
    font-weight: 700;
    margin: 8px 0;
}

.ph-accuracy-groups {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 8px 0;
}

.ph-group-stat {
    background: #e3f2fd;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 0.85rem;
}

.ph-last-match {
    margin: 8px 0 0;
    font-size: 0.9rem;
    color: #555;
}

.ph-admin-tabs {
    margin: 16px 0 12px;
    border-bottom: 1px solid #ccc;
    padding-bottom: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 2px;
}

.ph-tab {
    display: inline-block;
    padding: 8px 14px;
    text-decoration: none;
    color: #555;
    background: #f1f1f1;
    border: 1px solid #ccc;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    font-size: 0.85rem;
}

.ph-tab:hover {
    background: #e5e5e5;
    color: #1a1a1a;
}

.ph-tab-active {
    background: #fff;
    color: #1a1a1a;
    border-bottom: 1px solid #fff;
    margin-bottom: -1px;
    font-weight: 700;
}

.ph-results-table {
    margin: 12px 0;
}

.ph-results-table th {
    font-weight: 600;
}

.ph-row-complete {
    background: #f0f8f0 !important;
}

.ph-col-prediction {
    white-space: nowrap;
}

.ph-col-scores {
    white-space: nowrap;
}

.ph-score-input {
    width: 50px !important;
    text-align: center;
}

.ph-score-sep {
    margin: 0 4px;
    font-weight: 700;
}

.ph-col-status {
    text-align: center;
    font-size: 1.1rem;
}

/* Responsive */
@media (max-width: 782px) {
    .ph-accuracy-groups {
        flex-direction: column;
        gap: 4px;
    }
    .ph-admin-tabs {
        gap: 4px;
    }
    .ph-tab {
        padding: 6px 10px;
        font-size: 0.8rem;
    }
    .ph-score-input {
        width: 40px !important;
    }
}
```

- [ ] **Step 3: Commit**

```bash
git add wp-plugin/assets/css/admin.css
git commit -m "style: add admin results tabs, table, and dashboard styles"
```

---

### Task 8: Integration Verification

**Files:**
- Test: `wp-plugin/includes/class-data-client.php`
- Test: `wp-plugin/includes/class-admin.php`
- Test: `wp-plugin/includes/class-shortcode.php`

- [ ] **Step 1: Verify all PHP files parse**

```bash
php -l wp-plugin/includes/class-data-client.php; if ($?) { php -l wp-plugin/includes/class-admin.php }; if ($?) { php -l wp-plugin/includes/class-shortcode.php }
```

Expected: all return `No syntax errors detected`

- [ ] **Step 2: Verify all referenced methods exist**

Check that:
- `class-admin.php` calls `$this->data_client->get_match_results()`, `save_results()`, `calculate_accuracy()`, `get_predictions()` — all defined in `class-data-client.php`
- `class-shortcode.php` calls `$this->data_client->get_match_results()`, `calculate_accuracy()` — same
- `class-admin.php` calls `ph_translate_team()` — defined in `partidos-hoy.php`
- All `__()`, `_e()`, `esc_attr_e()`, `esc_html__()` use `'partidos-hoy'` text domain

- [ ] **Step 3: Manual test in WordPress**

Navigate to Ajustes → Partidos Hoy in WordPress admin:
- Confirm tabs (Group A-H + KO) render
- Confirm score inputs show for each match
- Enter a result, click Guardar resultados
- Confirm success message appears

Navigate to page with `[partidos-hoy]` shortcode:
- Confirm match with result now shows "2-0" instead of "vs"
- Confirm "✅ Finalizado" badge shows in banner
- Confirm "📊 Resultado vs Predicción" accordion appears
- Confirm global accuracy stats show above grid

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: post-match results with admin panel, comparison display, and accuracy stats"
```
