<?php
/**
 * Plugin Name:     Partidos Hoy
 * Plugin URI:       https://github.com/tuusuario/partidos-hoy
 * Description:      Predicciones de partidos de fútbol con ML (XGBoost)
 * Version:          1.0.0
 * Requires PHP:     7.4
 * Requires at least: 5.0
 * Author:           Tu Nombre
 * License:          GPL v2 or later
 * Text Domain:      partidos-hoy
 * Domain Path:      /languages
 */

defined('ABSPATH') || exit;

require_once dirname( __FILE__ ) . '/vendor/freemius/start.php';

function ph_freemius() {
    $freemius = fs_dynamic_init( array(
        'id'                  => 'YOUR_PRODUCT_ID',
        'slug'                => 'partidos-hoy',
        'type'                => 'plugin',
        'public_key'          => 'pk_YOUR_PUBLIC_KEY',
        'is_premium'          => false,
        'premium_suffix'      => ' (Premium)',
        'has_addons'          => false,
        'has_paid_plans'      => true,
        'trial'               => array(
            'days'               => 7,
            'is_require_payment' => false,
        ),
        'menu'                => array(
            'slug'           => 'partidos-hoy',
            'support'        => false,
            'parent'         => array(
                'slug' => 'options-general.php',
            ),
        ),
    ) );
    return $freemius;
}
ph_freemius();

define('PH_VERSION', '1.0.0');
define('PH_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('PH_PLUGIN_URL', plugin_dir_url(__FILE__));

require_once PH_PLUGIN_DIR . 'includes/class-data-client.php';
require_once PH_PLUGIN_DIR . 'includes/class-shortcode.php';

function ph_init_premium() {
    $data_client = new PH_Data_Client();
    new PH_Shortcode($data_client);

    if (is_admin()) {
        require_once PH_PLUGIN_DIR . 'includes/class-admin.php';
        new PH_Admin($data_client);
    }
}

if (ph_freemius()->can_use_premium_code()) {
    define('PH_IS_PREMIUM', true);
    add_filter('ph_league_limit', function() { return 50; });
} else {
    define('PH_IS_PREMIUM', false);
    add_filter('ph_league_limit', function() { return 5; });
}

add_action('plugins_loaded', 'ph_init_premium');
