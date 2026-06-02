<?php
defined('ABSPATH') || exit;

class PH_Admin {
    private $data_client;

    public function __construct($data_client) {
        $this->data_client = $data_client;
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));
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
        wp_enqueue_style('ph-admin', PH_PLUGIN_URL . 'assets/css/admin.css', array(), PH_VERSION);
    }

    public function render_admin_page() {
        if (!current_user_can('manage_options')) {
            return;
        }
        ?>
        <div class="wrap">
            <h1><?php echo esc_html__('Partidos Hoy', 'partidos-hoy'); ?></h1>
            <p><em><?php esc_html_e('For informational and entertainment purposes only. Not affiliated with FIFA or any football federation.', 'partidos-hoy'); ?></em></p>
            <form method="post" action="options.php">
                <?php settings_fields('ph_settings_group'); ?>
                <table class="form-table">
                    <tr>
                        <th scope="row">
                            <label for="ph_predictions_url">
                                <?php esc_html_e('URL de predicciones JSON', 'partidos-hoy'); ?>
                            </label>
                        </th>
                        <td>
                            <input type="url" id="ph_predictions_url" name="ph_predictions_url"
                                   value="<?php echo esc_attr(get_option('ph_predictions_url', '')); ?>"
                                   class="regular-text" />
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">
                            <label for="ph_fallback_url">
                                <?php esc_html_e('URL de respaldo', 'partidos-hoy'); ?>
                            </label>
                        </th>
                        <td>
                            <input type="url" id="ph_fallback_url" name="ph_fallback_url"
                                   value="<?php echo esc_attr(get_option('ph_fallback_url', '')); ?>"
                                   class="regular-text" />
                        </td>
                    </tr>
                    <tr>
                        <th scope="row">
                            <label for="ph_cache_ttl">
                                <?php esc_html_e('TTL de caché (segundos)', 'partidos-hoy'); ?>
                            </label>
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
                <button type="submit" class="button">
                    <?php esc_html_e('Limpiar caché', 'partidos-hoy'); ?>
                </button>
            </form>
            <?php $this->handle_cache_clear(); ?>
        </div>
        <?php
    }

    private function handle_cache_clear() {
        if (!isset($_POST['ph_action']) || $_POST['ph_action'] !== 'clear_cache') {
            return;
        }
        if (!isset($_POST['ph_nonce']) || !wp_verify_nonce($_POST['ph_nonce'], 'ph_clear_cache')) {
            return;
        }
        if (!current_user_can('manage_options')) {
            return;
        }
        $this->data_client->clear_cache();
        echo '<div class="notice notice-success"><p>' .
             esc_html__('Caché limpiada correctamente.', 'partidos-hoy') .
             '</p></div>';
    }
}
