<?php
defined('ABSPATH') || exit;

class PH_Data_Client {
    private $predictions_url;
    private $cache_key = 'ph_predictions_cache';
    private $cache_ttl = 21600;

    public function __construct() {
        $url = get_option('ph_predictions_url', '');
        $this->predictions_url = $url ?: 'https://miravosqueinteresante.github.io/partidos-hoy/latest.json';
        $ttl = get_option('ph_cache_ttl', 21600);
        $this->cache_ttl = max(300, absint($ttl));
    }

    public function get_predictions() {
        $cached = get_transient($this->cache_key);
        if ($cached !== false && !empty($cached['matches'])) {
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
