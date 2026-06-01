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

if ( ! function_exists( 'ph_fs' ) ) {
    function ph_fs() {
        $is_local = ( $_SERVER['REMOTE_ADDR'] ?? '' ) === '127.0.0.1'
                 || ( $_SERVER['REMOTE_ADDR'] ?? '' ) === '::1'
                 || ( $_SERVER['SERVER_NAME'] ?? '' ) === 'localhost'
                 || ( $_SERVER['SERVER_NAME'] ?? '' ) === 'experimentos.test';
        if ( $is_local ) {
            return false;
        }

        global $ph_fs;

        if ( ! isset( $ph_fs ) ) {
            require_once dirname( __FILE__ ) . '/vendor/freemius/start.php';

            $ph_fs = fs_dynamic_init( array(
                'id'                  => '30947',
                'slug'                => 'partidos-hoy',
                'type'                => 'plugin',
                'public_key'          => 'pk_f94ef765415511b6c749099fb9843',
                'is_premium'          => true,
                'is_premium_only'     => true,
                'has_addons'          => false,
                'has_paid_plans'      => true,
                'is_org_compliant'    => true,
                'wp_org_gatekeeper'   => 'OA7#BoRiBNqdf52FvzEf!!074aRLPs8fspif$7K1#4u4Csys1fQlCecVcUTOs2mcpeVHi#C2j9d09fOTvbC0HloPT7fFee5WdS3G',
                'trial'               => array(
                    'days'               => 3,
                    'is_require_payment' => false,
                ),
                'menu'                => array(
                    'support'        => false,
                ),
            ) );
        }

        return $ph_fs;
    }

    if ( ph_fs() !== false ) {
        ph_fs();
        do_action( 'ph_fs_loaded' );
    }
}

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
