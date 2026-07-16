<?php
defined('ABSPATH') || exit;

class PH_Admin {
    private $data_client;
    private $predictions;

    public function __construct($data_client) {
        $this->data_client = $data_client;
        $this->predictions = $this->data_client->get_predictions();
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));
        add_action('admin_init', array($this, 'handle_save_results'));
        add_action('admin_init', array($this, 'handle_clear_results'));
        add_action('admin_init', array($this, 'handle_cache_clear'));
        add_action('admin_enqueue_scripts', array($this, 'enqueue_admin_styles'));
    }

    public function add_admin_menu() {
        add_options_page(
            __('Partidos Hoy', 'partidos-hoy'),
            __('Partidos Hoy', 'partidos-hoy'),
            'manage_options',
            'partidos-hoy',
            array($this, 'render_admin_page')
        );
    }

    public function register_settings() {
        register_setting('ph_settings_group', 'ph_predictions_url', 'esc_url_raw');
        register_setting('ph_settings_group', 'ph_fallback_url', 'esc_url_raw');
        register_setting('ph_settings_group', 'ph_cache_ttl', 'absint');
    }

    public function enqueue_admin_styles($hook) {
        if ($hook !== 'settings_page_partidos-hoy') {
            return;
        }
        wp_enqueue_style('ph-admin', PH_PLUGIN_URL . 'admin.css', array(), PH_VERSION);
    }

    public function handle_clear_results() {
        if (!isset($_POST['ph_action']) || $_POST['ph_action'] !== 'clear_results') {
            return;
        }
        if (!isset($_POST['ph_clear_nonce']) || !wp_verify_nonce($_POST['ph_clear_nonce'], 'ph_clear_results')) {
            return;
        }
        if (!current_user_can('manage_options')) {
            return;
        }
        delete_option('ph_match_results');
        add_action('admin_notices', function() {
            echo '<div class="notice notice-success"><p>' .
                 esc_html__('Todos los resultados fueron eliminados. Podés cargarlos de nuevo desde cero.', 'partidos-hoy') .
                 '</p></div>';
        });
    }

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
                $id = absint($key);
                if ($id <= 0) {
                    continue;
                }
                $home_raw = $data['home_goals'] ?? '';
                $away_raw = $data['away_goals'] ?? '';
                if ($home_raw === '' || $away_raw === '') {
                    continue;
                }
                $results[$id] = array(
                    'home_goals' => absint($home_raw),
                    'away_goals' => absint($away_raw),
                );
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

    private function get_matches_by_group($matches, $group) {
        return array_values(array_filter($matches, function($m) use ($group) {
            $stage = isset($m['stage']) ? $m['stage'] : '';
            $g = isset($m['group']) ? strtoupper($m['group']) : ($stage && $stage !== 'group' ? 'KO' : '');
            return $g === $group;
        }));
    }

    private function get_group_labels() {
        return array('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'KO');
    }

    private function get_flag_static($team_name) {
        return ph_get_flag($team_name);
    }

    public function render_admin_page() {
        if (!current_user_can('manage_options')) {
            return;
        }

        $results = $this->data_client->get_match_results();
        $matches = isset($this->predictions['matches']) ? $this->predictions['matches'] : array();

        $valid_ids = array();
        foreach ($matches as $m) {
            if (isset($m['id'])) {
                $valid_ids[] = intval($m['id']);
            }
        }
        if (!empty($valid_ids) && !empty($results)) {
            $valid_set = array_flip($valid_ids);
            $pruned = array_intersect_key($results, $valid_set);
            if (count($pruned) !== count($results)) {
                update_option('ph_match_results', $pruned);
                $results = $pruned;
            }
        }

        $accuracy = $this->data_client->calculate_accuracy($matches);

        $selected_group = isset($_GET['ph_group']) && in_array(strtoupper($_GET['ph_group']), $this->get_group_labels())
            ? strtoupper($_GET['ph_group'])
            : 'A';
        ?>
        <div class="wrap">
            <h1><?php echo esc_html__('Partidos Hoy', 'partidos-hoy'); ?></h1>
            <p><em><?php esc_html_e('For informational and entertainment purposes only.', 'partidos-hoy'); ?></em></p>

            <div class="ph-admin-stats">
                <h2><?php echo '📊 '; esc_html_e('Precisión de predicciones', 'partidos-hoy'); ?></h2>
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
                <form method="post" action="" style="margin-top:12px">
                    <?php wp_nonce_field('ph_clear_results', 'ph_clear_nonce'); ?>
                    <input type="hidden" name="ph_action" value="clear_results" />
                    <button type="submit" class="button button-secondary"
                        onclick="return confirm('<?php esc_attr_e('¿Borrar todos los resultados cargados? Esta acción no se puede deshacer.', 'partidos-hoy'); ?>')">
                        <?php esc_html_e('Borrar todos los resultados', 'partidos-hoy'); ?>
                    </button>
                </form>
            </div>

            <?php $this->render_health_check(); ?>

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
                                $mid = isset($match['id']) ? intval($match['id']) : 0;
                                $probs = $match['probabilities'] ?? array();
                                $max_key = !empty($probs) ? array_search(max($probs), $probs) : '';
                                $max_label = array('home' => $home, 'draw' => __('Empate', 'partidos-hoy'), 'away' => $away);
                                $max_pct = isset($probs[$max_key]) ? round(floatval($probs[$max_key]) * 100) : 0;
                                $flag_home = $this->get_flag_static($home);
                                $has_result = $mid > 0 && isset($results[$mid]);
                                $existing = $has_result ? $results[$mid] : null;
                            ?>
                            <tr class="<?php echo $has_result ? 'ph-row-complete' : ''; ?>">
                                <td class="ph-col-match">
                                    <?php
                                    $stage_name = isset($match['stage']) && $match['stage'] !== 'group' ? ph_translate_stage($match['stage']) : '';
                                    if ($stage_name): ?>
                                        <span class="ph-stage-badge"><?php echo esc_html($stage_name); ?></span>
                                    <?php endif;
                                    $home_disp = $home ? ph_translate_team($home) : __('Por definir', 'partidos-hoy');
                                    $away_disp = $away ? ph_translate_team($away) : __('Por definir', 'partidos-hoy');
                                    echo esc_html($home_disp);
                                    ?> vs <?php
                                    echo esc_html($away_disp);
                                    ?>
                                </td>
                                <td class="ph-col-prediction">
                                    <?php echo $flag_home . ' ' . esc_html($max_label[$max_key] ?? '') . ' ' . $max_pct . '%'; ?>
                                </td>
                                <td class="ph-col-scores">
                                    <input type="number" min="0" max="50" class="ph-score-input"
                                           name="ph_results[<?php echo $mid; ?>][home_goals]"
                                           value="<?php echo $has_result ? esc_attr($existing['home_goals']) : ''; ?>"
                                           placeholder="<?php esc_attr_e('Local', 'partidos-hoy'); ?>" />
                                    <span class="ph-score-sep">-</span>
                                    <input type="number" min="0" max="50" class="ph-score-input"
                                           name="ph_results[<?php echo $mid; ?>][away_goals]"
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
            <h2><?php esc_html_e('Shortcodes disponibles', 'partidos-hoy'); ?></h2>
            <table class="wp-list-table widefat fixed striped">
                <thead>
                    <tr>
                        <th style="width:22%"><?php esc_html_e('Shortcode', 'partidos-hoy'); ?></th>
                        <th style="width:30%"><?php esc_html_e('Descripción', 'partidos-hoy'); ?></th>
                        <th><?php esc_html_e('Parámetros y ejemplos', 'partidos-hoy'); ?></th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>[partidos-hoy]</code></td>
                        <td><?php esc_html_e('Grilla completa de tarjetas de predicción con filtros y paginación.', 'partidos-hoy'); ?></td>
                        <td>
                            <strong><?php esc_html_e('Parámetros:', 'partidos-hoy'); ?></strong><br>
                            <code>league</code> — <?php esc_html_e('liga (default: todas)', 'partidos-hoy'); ?><br>
                            <code>limit</code> — <?php esc_html_e('tarjetas por página (default: 20)', 'partidos-hoy'); ?><br>
                            <code>group</code> — <?php esc_html_e('filtrar por grupo (A-L, KO)', 'partidos-hoy'); ?><br>
                            <code>stage</code> — <?php esc_html_e('filtrar por fase (round_of_32, round_of_16, quarter_final, semi_final, bronze_final, final)', 'partidos-hoy'); ?><br>
                            <code>date</code> — <?php esc_html_e('filtrar por fecha (YYYY-MM-DD)', 'partidos-hoy'); ?><br>
                            <code>team</code> — <?php esc_html_e('filtrar por equipo (inglés)', 'partidos-hoy'); ?><br>
                            <code>search</code> — <?php esc_html_e('búsqueda por texto', 'partidos-hoy'); ?><br>
                            <code>page</code> — <?php esc_html_e('página inicial (default: 1)', 'partidos-hoy'); ?><br><br>
                            <strong><?php esc_html_e('Ejemplos:', 'partidos-hoy'); ?></strong><br>
                            <code>[partidos-hoy]</code> — <?php esc_html_e('todas las tarjetas', 'partidos-hoy'); ?><br>
                            <code>[partidos-hoy group="A"]</code> — <?php esc_html_e('solo Grupo A', 'partidos-hoy'); ?><br>
                            <code>[partidos-hoy group="KO"]</code> — <?php esc_html_e('toda la fase knockout', 'partidos-hoy'); ?><br>
                            <code>[partidos-hoy stage="round_of_16"]</code> — <?php esc_html_e('solo Octavos de Final', 'partidos-hoy'); ?><br>
                            <code>[partidos-hoy team="Argentina"]</code> — <?php esc_html_e('partidos de Argentina', 'partidos-hoy'); ?><br>
                            <code>[partidos-hoy date="2026-06-11" limit="10"]</code> — <?php esc_html_e('partidos del 11/6, 10 por página', 'partidos-hoy'); ?>
                        </td>
                    </tr>
                    <tr>
                        <td><code>[predicciones_partido]</code></td>
                        <td><?php esc_html_e('Tarjeta individual para un partido específico. Ideal para páginas dedicadas con OG meta tags.', 'partidos-hoy'); ?></td>
                        <td>
                            <strong><?php esc_html_e('Parámetros:', 'partidos-hoy'); ?></strong><br>
                            <code>home</code> — <?php esc_html_e('equipo local (obligatorio, en inglés)', 'partidos-hoy'); ?><br>
                            <code>away</code> — <?php esc_html_e('equipo visitante (obligatorio, en inglés)', 'partidos-hoy'); ?><br><br>
                            <strong><?php esc_html_e('Ejemplos:', 'partidos-hoy'); ?></strong><br>
                            <code>[predicciones_partido home="Argentina" away="Brazil"]</code> — <?php esc_html_e('tarjeta Argentina vs Brasil', 'partidos-hoy'); ?><br>
                            <code>[predicciones_partido home="Mexico" away="USA"]</code> — <?php esc_html_e('tarjeta México vs USA', 'partidos-hoy'); ?>
                        </td>
                    </tr>
                </tbody>
            </table>

            <hr />
            <h2><?php esc_html_e('Caché', 'partidos-hoy'); ?></h2>
            <form method="post">
                <?php wp_nonce_field('ph_clear_cache', 'ph_nonce'); ?>
                <input type="hidden" name="ph_action" value="clear_cache" />
                <button type="submit" class="button"><?php esc_html_e('Limpiar caché', 'partidos-hoy'); ?></button>
            </form>
        </div>
        <?php
    }

    public function handle_cache_clear() {
        if (!isset($_POST['ph_action']) || $_POST['ph_action'] !== 'clear_cache') {
            return;
        }
        if (!isset($_POST['ph_nonce']) || !wp_verify_nonce($_POST['ph_nonce'], 'ph_clear_cache')) {
            add_action('admin_notices', function() {
                echo '<div class="notice notice-error"><p>' .
                     esc_html__('Error de seguridad: nonce inválido.', 'partidos-hoy') .
                     '</p></div>';
            });
            return;
        }
        if (!current_user_can('manage_options')) {
            return;
        }
        $this->data_client->clear_cache();
        add_action('admin_notices', function() {
            echo '<div class="notice notice-success"><p>' .
                 esc_html__('Caché limpiada correctamente.', 'partidos-hoy') .
                 '</p></div>';
        });
    }

    private function render_health_check() {
        $predictions = $this->data_client->get_predictions();
        $has_data = !empty($predictions) && !empty($predictions['matches']);
        $historical_path = PH_PLUGIN_DIR . 'historical_wc_data.json';
        $has_historical = file_exists($historical_path);
        $historical_size = $has_historical ? size_format(filesize($historical_path)) : 'N/A';
        $predictions_url = get_option('ph_predictions_url', '');
        $fallback_url = get_option('ph_fallback_url', '');
        ?>
        <details class="ph-health-check" style="margin:16px 0;padding:12px 16px;background:#f8f9fa;border:1px solid #dcdcde;border-radius:6px;">
            <summary style="cursor:pointer;font-weight:700;font-size:0.9rem;">
                ⚙️ <?php esc_html_e('Estado del sistema', 'partidos-hoy'); ?>
            </summary>
            <table class="widefat fixed" style="margin-top:12px;">
                <tbody>
                    <tr>
                        <td style="width:200px;font-weight:600;"><?php esc_html_e('Plugin versión', 'partidos-hoy'); ?></td>
                        <td><?php echo esc_html(PH_VERSION); ?></td>
                    </tr>
                    <tr>
                        <td style="font-weight:600;"><?php esc_html_e('Datos de predicciones', 'partidos-hoy'); ?></td>
                        <td><?php echo $has_data
                            ? '<span style="color:#16a34a;">✅ ' . esc_html(count($predictions['matches'])) . ' partidos cargados</span>'
                            : '<span style="color:#dc2626;">❌ ' . esc_html__('Sin datos. Verificar URL de predicciones.', 'partidos-hoy') . '</span>'; ?></td>
                    </tr>
                    <tr>
                        <td style="font-weight:600;"><?php esc_html_e('URL predicciones', 'partidos-hoy'); ?></td>
                        <td><code><?php echo esc_html($predictions_url ?: 'Usando URL por defecto'); ?></code></td>
                    </tr>
                    <tr>
                        <td style="font-weight:600;"><?php esc_html_e('URL respaldo', 'partidos-hoy'); ?></td>
                        <td><code><?php echo esc_html($fallback_url ?: 'Usando URL por defecto'); ?></code></td>
                    </tr>
                    <tr>
                        <td style="font-weight:600;"><?php esc_html_e('Caché activa', 'partidos-hoy'); ?></td>
                        <td><?php echo get_transient('ph_predictions_cache') !== false
                            ? '<span style="color:#16a34a;">✅ ' . esc_html__('Sí', 'partidos-hoy') . '</span>'
                            : '<span style="color:#64748b;">⏳ ' . esc_html__('No (se cargará en el próximo acceso)', 'partidos-hoy') . '</span>'; ?></td>
                    </tr>
                    <tr>
                        <td style="font-weight:600;"><?php esc_html_e('Datos históricos', 'partidos-hoy'); ?></td>
                        <td><?php echo $has_historical
                            ? '<span style="color:#16a34a;">✅ ' . esc_html(sprintf(__('%s — 964 partidos (1930-2022)', 'partidos-hoy'), $historical_size)) . '</span>'
                            : '<span style="color:#dc2626;">❌ ' . esc_html__('Archivo no encontrado', 'partidos-hoy') . '</span>'; ?></td>
                    </tr>
                </tbody>
            </table>
            <p style="margin:8px 0 0;font-size:0.75rem;color:#64748b;">
                <?php esc_html_e('Si los datos no se cargan, verificá que las URLs de predicción sean accesibles. La caché se refresca automáticamente cada 6 horas.', 'partidos-hoy'); ?>
            </p>
        </details>
        <?php
    }
}
