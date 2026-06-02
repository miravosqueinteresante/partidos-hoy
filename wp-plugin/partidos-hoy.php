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
