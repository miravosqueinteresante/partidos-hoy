<?php
/**
 * Plugin Name:     Partidos Hoy
 * Plugin URI:       https://github.com/miravosqueinteresante/partidos-hoy
 * Description:      Pronósticos de fútbol con ranking ELO para el torneo 2026
 * Version:          1.0.4
 * Requires PHP:     7.4
 * Requires at least: 5.0
 * Author:           partidoshoy.futbol
 * License:          GPL v2 or later
 * Text Domain:      partidos-hoy
 * Domain Path:      /languages
 */

defined('ABSPATH') || exit;

define('PH_VERSION', '1.0.4');
define('PH_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('PH_PLUGIN_URL', plugin_dir_url(__FILE__));

require_once PH_PLUGIN_DIR . 'class-data-client.php';
require_once PH_PLUGIN_DIR . 'class-shortcode.php';
require_once PH_PLUGIN_DIR . 'class-admin.php';

function ph_activate() {
    if (version_compare(PHP_VERSION, '7.4', '<')) {
        deactivate_plugins(plugin_basename(__FILE__));
        wp_die('PHP 7.4 or higher required.');
    }
    if (empty(get_option('ph_cache_ttl'))) {
        add_option('ph_cache_ttl', 21600);
    }
    if (empty(get_option('ph_predictions_url'))) {
        add_option('ph_predictions_url', 'https://miravosqueinteresante.github.io/partidos-hoy/latest.json');
    }
    if (empty(get_option('ph_fallback_url'))) {
        add_option('ph_fallback_url', 'https://raw.githubusercontent.com/miravosqueinteresante/partidos-hoy/gh-pages/latest.json');
    }
}
register_activation_hook(__FILE__, 'ph_activate');

function ph_deactivate() {
    delete_transient('ph_predictions_cache');
    delete_transient('ph_predictions_cache_check');
    delete_transient('ph_historical_all');
}
register_deactivation_hook(__FILE__, 'ph_deactivate');

function ph_init() {
    load_plugin_textdomain('partidos-hoy', false, dirname(plugin_basename(__FILE__)) . '/languages');
    $data_client = new PH_Data_Client();
    new PH_Shortcode($data_client);
    if (is_admin()) {
        new PH_Admin($data_client);
    }
}
add_action('plugins_loaded', 'ph_init');

function ph_get_team_variants($name) {
    $map = array(
        'USA'                   => array('United States'),
        'United States'         => array('USA'),
        'Korea Republic'        => array('South Korea', 'Corea del Sur'),
        'South Korea'           => array('Korea Republic', 'Corea del Sur'),
        'Corea del Sur'         => array('South Korea', 'Korea Republic'),
        'IR Iran'               => array('Iran'),
        'Iran'                  => array('IR Iran'),
        'Czechia'               => array('Czech Republic', 'Czechoslovakia'),
        'Czech Republic'        => array('Czechia'),
        'Côte d\'Ivoire'        => array('Ivory Coast'),
        'Ivory Coast'           => array('Côte d\'Ivoire'),
        'Türkiye'               => array('Turkey'),
        'Turkey'                => array('Türkiye'),
        'Congo DR'              => array('Zaire'),
        'Zaire'                 => array('Congo DR'),
    );
    $variants = array($name);
    if (isset($map[$name])) {
        $variants = array_merge($variants, $map[$name]);
    }
    return $variants;
}

function ph_translate_team($name) {
    $map = array(
        'USA'                      => 'Estados Unidos',
        'United States'            => 'Estados Unidos',
        'Korea Republic'           => 'Corea del Sur',
        'South Korea'              => 'Corea del Sur',
        'North Korea'              => 'Corea del Norte',
        'IR Iran'                  => 'Irán',
        'Iran'                     => 'Irán',
        'Czechia'                  => 'República Checa',
        'Czech Republic'           => 'República Checa',
        'Czechoslovakia'           => 'Checoslovaquia',
        'Côte d\'Ivoire'           => 'Costa de Marfil',
        'Ivory Coast'              => 'Costa de Marfil',
        'Türkiye'                  => 'Turquía',
        'Turkey'                   => 'Turquía',
        'Netherlands'              => 'Países Bajos',
        'England'                  => 'Inglaterra',
        'Germany'                  => 'Alemania',
        'West Germany'             => 'Alemania Occidental',
        'East Germany'             => 'Alemania Oriental',
        'Switzerland'              => 'Suiza',
        'Sweden'                   => 'Suecia',
        'Spain'                    => 'España',
        'France'                   => 'Francia',
        'Italy'                    => 'Italia',
        'Belgium'                  => 'Bélgica',
        'Greece'                   => 'Grecia',
        'Denmark'                  => 'Dinamarca',
        'Norway'                   => 'Noruega',
        'Poland'                   => 'Polonia',
        'Romania'                  => 'Rumanía',
        'Russia'                   => 'Rusia',
        'Scotland'                 => 'Escocia',
        'Wales'                    => 'Gales',
        'Northern Ireland'         => 'Irlanda del Norte',
        'Republic of Ireland'      => 'Irlanda',
        'Brazil'                   => 'Brasil',
        'Mexico'                   => 'México',
        'Japan'                    => 'Japón',
        'South Africa'             => 'Sudáfrica',
        'Egypt'                    => 'Egipto',
        'Morocco'                  => 'Marruecos',
        'Cameroon'                 => 'Camerún',
        'Tunisia'                  => 'Túnez',
        'Algeria'                  => 'Argelia',
        'Nigeria'                  => 'Nigeria',
        'Senegal'                  => 'Senegal',
        'Togo'                     => 'Togo',
        'Angola'                   => 'Angola',
        'Congo DR'                 => 'República Democrática del Congo',
        'Zaire'                    => 'Zaire',
        'Iraq'                     => 'Irak',
        'Saudi Arabia'             => 'Arabia Saudita',
        'United Arab Emirates'     => 'Emiratos Árabes Unidos',
        'Canada'                   => 'Canadá',
        'Panama'                   => 'Panamá',
        'Costa Rica'               => 'Costa Rica',
        'Honduras'                 => 'Honduras',
        'El Salvador'              => 'El Salvador',
        'Haiti'                    => 'Haití',
        'Jamaica'                  => 'Jamaica',
        'Trinidad and Tobago'      => 'Trinidad y Tobago',
        'Cuba'                     => 'Cuba',
        'Bolivia'                  => 'Bolivia',
        'Peru'                     => 'Perú',
        'Ecuador'                  => 'Ecuador',
        'Paraguay'                 => 'Paraguay',
        'Uruguay'                  => 'Uruguay',
        'Chile'                    => 'Chile',
        'Colombia'                 => 'Colombia',
        'Argentina'                => 'Argentina',
        'Australia'                => 'Australia',
        'New Zealand'              => 'Nueva Zelanda',
        'Qatar'                    => 'Catar',
        'Jordan'                   => 'Jordania',
        'Uzbekistan'               => 'Uzbekistán',
        'Kuwait'                   => 'Kuwait',
        'China'                    => 'China',
        'Israel'                   => 'Israel',
        'Cabo Verde'               => 'Cabo Verde',
        'Curaçao'                  => 'Curazao',
        'Bosnia and Herzegovina'   => 'Bosnia y Herzegovina',
        'Croatia'                  => 'Croacia',
        'Serbia'                   => 'Serbia',
        'Serbia and Montenegro'    => 'Serbia y Montenegro',
        'Slovenia'                 => 'Eslovenia',
        'Slovakia'                 => 'Eslovaquia',
        'Ukraine'                  => 'Ucrania',
        'Hungary'                  => 'Hungría',
        'Bulgaria'                 => 'Bulgaria',
        'Soviet Union'             => 'Unión Soviética',
        'Yugoslavia'               => 'Yugoslavia',
        'Dutch East Indies'        => 'Indias Orientales Neerlandesas',
        'Austria'                  => 'Austria',
        'Portugal'                 => 'Portugal',
        'Ghana'                    => 'Ghana',
        'Iceland'                  => 'Islandia',
    );
    if (isset($map[$name])) return $map[$name];
    $reverse = array(
        'Estados Unidos'             => 'United States',
        'Corea del Sur'              => 'South Korea',
        'Corea del Norte'            => 'North Korea',
        'Irán'                       => 'Iran',
        'República Checa'            => 'Czechia',
        'Checoslovaquia'             => 'Czechoslovakia',
        'Costa de Marfil'            => 'Ivory Coast',
        'Turquía'                    => 'Türkiye',
        'Países Bajos'               => 'Netherlands',
        'Inglaterra'                 => 'England',
        'Alemania'                   => 'Germany',
        'Alemania Occidental'        => 'West Germany',
        'Alemania Oriental'          => 'East Germany',
        'Suiza'                      => 'Switzerland',
        'Suecia'                     => 'Sweden',
        'España'                     => 'Spain',
        'Francia'                    => 'France',
        'Italia'                     => 'Italy',
        'Bélgica'                    => 'Belgium',
        'Grecia'                     => 'Greece',
        'Dinamarca'                  => 'Denmark',
        'Noruega'                    => 'Norway',
        'Polonia'                    => 'Poland',
        'Rumanía'                    => 'Romania',
        'Rusia'                      => 'Russia',
        'Escocia'                    => 'Scotland',
        'Gales'                      => 'Wales',
        'Irlanda del Norte'          => 'Northern Ireland',
        'Irlanda'                    => 'Republic of Ireland',
        'Brasil'                     => 'Brazil',
        'México'                     => 'Mexico',
        'Japón'                      => 'Japan',
        'Sudáfrica'                  => 'South Africa',
        'Egipto'                     => 'Egypt',
        'Marruecos'                  => 'Morocco',
        'Camerún'                    => 'Cameroon',
        'Túnez'                      => 'Tunisia',
        'Argelia'                    => 'Algeria',
        'Nigeria'                    => 'Nigeria',
        'Senegal'                    => 'Senegal',
        'República Democrática del Congo' => 'Congo DR',
        'Irak'                       => 'Iraq',
        'Arabia Saudita'             => 'Saudi Arabia',
        'Emiratos Árabes Unidos'     => 'United Arab Emirates',
        'Canadá'                     => 'Canada',
        'Panamá'                     => 'Panama',
        'Haití'                      => 'Haiti',
        'Trinidad y Tobago'          => 'Trinidad and Tobago',
        'Perú'                       => 'Peru',
        'Ecuador'                    => 'Ecuador',
        'Paraguay'                   => 'Paraguay',
        'Uruguay'                    => 'Uruguay',
        'Chile'                      => 'Chile',
        'Colombia'                   => 'Colombia',
        'Argentina'                  => 'Argentina',
        'Australia'                  => 'Australia',
        'Nueva Zelanda'              => 'New Zealand',
        'Catar'                      => 'Qatar',
        'Jordania'                   => 'Jordan',
        'Uzbekistán'                 => 'Uzbekistan',
        'Kuwait'                     => 'Kuwait',
        'Cabo Verde'                 => 'Cabo Verde',
        'Curazao'                    => 'Curaçao',
        'Bosnia y Herzegovina'       => 'Bosnia and Herzegovina',
        'Croacia'                    => 'Croatia',
        'Serbia'                     => 'Serbia',
        'Serbia y Montenegro'        => 'Serbia and Montenegro',
        'Eslovenia'                  => 'Slovenia',
        'Eslovaquia'                 => 'Slovakia',
        'Ucrania'                    => 'Ukraine',
        'Hungría'                    => 'Hungary',
        'Bulgaria'                   => 'Bulgaria',
        'Unión Soviética'            => 'Soviet Union',
        'Yugoslavia'                 => 'Yugoslavia',
        'Indias Orientales Neerlandesas' => 'Dutch East Indies',
        'Austria'                    => 'Austria',
        'Portugal'                   => 'Portugal',
        'Islandia'                   => 'Iceland',
    );
    return isset($reverse[$name]) ? $reverse[$name] : $name;
}

function ph_esc_json($str) {
    $escaped = str_replace(
        array('\\', '"', "\n", "\r", "\t"),
        array('\\\\', '\\"', '\\n', '\\r', '\\t'),
        $str
    );
    return $escaped;
}

function ph_translate_stage($stage) {
    $map = array(
        'group'         => 'Fase de Grupos',
        'round_of_32'   => 'Dieciseisavos',
        'round_of_16'   => 'Octavos de Final',
        'quarter_final' => 'Cuartos de Final',
        'semi_final'    => 'Semifinal',
        'bronze_final'  => 'Tercer Puesto',
        'final'         => 'Final',
    );
    return isset($map[$stage]) ? $map[$stage] : $stage;
}

function ph_get_flag($team_name) {
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

function ph_ajax_historical() {
    $nonce = isset($_GET['ph_nonce']) ? $_GET['ph_nonce'] : '';
    if (!wp_verify_nonce($nonce, 'ph_historical')) {
        wp_send_json_error(array('message' => 'Nonce inválido'));
    }

    $home = isset($_GET['home']) ? sanitize_text_field($_GET['home']) : '';
    $away = isset($_GET['away']) ? sanitize_text_field($_GET['away']) : '';
    if (empty($home) || empty($away)) {
        wp_send_json_error(array('message' => 'Parámetros incompletos'));
    }

    $cache_key = 'ph_historical_all';
    $all_matches = get_transient($cache_key);

    if (false === $all_matches) {
        $json_path = PH_PLUGIN_DIR . 'historical_wc_data.json';
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

    $home_variants = ph_get_team_variants($home);
    $away_variants = ph_get_team_variants($away);

    $matches = array();
    foreach ($all_matches as $m) {
        $mh_v = ph_get_team_variants($m['home_team']);
        $ma_v = ph_get_team_variants($m['away_team']);

        if (
            (array_intersect($home_variants, $mh_v) && array_intersect($away_variants, $ma_v)) ||
            (array_intersect($home_variants, $ma_v) && array_intersect($away_variants, $mh_v))
        ) {
            $m['home_team'] = ph_translate_team($m['home_team']);
            $m['away_team'] = ph_translate_team($m['away_team']);
            $matches[] = $m;
        }
    }

    wp_send_json_success($matches);
}
add_action('wp_ajax_ph_historical', 'ph_ajax_historical');
add_action('wp_ajax_nopriv_ph_historical', 'ph_ajax_historical');
