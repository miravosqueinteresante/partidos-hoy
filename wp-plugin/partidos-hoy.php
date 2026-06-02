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
    load_plugin_textdomain('partidos-hoy', false, dirname(plugin_basename(__FILE__)) . '/languages');
    $data_client = new PH_Data_Client();
    new PH_Shortcode($data_client);
    if (is_admin()) {
        new PH_Admin($data_client);
    }
}
add_action('plugins_loaded', 'ph_init');

function ph_ajax_historical() {
    $home = isset($_GET['home']) ? sanitize_text_field($_GET['home']) : '';
    $away = isset($_GET['away']) ? sanitize_text_field($_GET['away']) : '';
    if (empty($home) || empty($away)) {
        wp_send_json_error(array('message' => 'Parámetros incompletos'));
    }

    $cache_key = 'ph_historical_all';
    $all_matches = get_transient($cache_key);

    if (false === $all_matches) {
        $json_path = PH_PLUGIN_DIR . 'data/historical_wc_data.json';
        if (!file_exists($json_path)) {
            wp_send_json_error(array('message' => 'Datos históricos no disponibles'));
        }
        $json = file_get_contents($json_path);
        $data = json_decode($json, true);
        if (!is_array($data) || !isset($data['matches'])) {
            wp_send_json_error(array('message' => 'Datos históricos inválidos'));
        }
        $all_matches = $data['matches'];
        set_transient($cache_key, $all_matches, DAY_IN_SECONDS);
    }

    $matches = array();
    foreach ($all_matches as $m) {
        if (
            (strcasecmp($m['home_team'], $home) === 0 && strcasecmp($m['away_team'], $away) === 0) ||
            (strcasecmp($m['home_team'], $away) === 0 && strcasecmp($m['away_team'], $home) === 0)
        ) {
            $matches[] = $m;
        }
    }

    wp_send_json_success($matches);
}
add_action('wp_ajax_ph_historical', 'ph_ajax_historical');
add_action('wp_ajax_nopriv_ph_historical', 'ph_ajax_historical');
