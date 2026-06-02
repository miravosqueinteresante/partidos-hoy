<?php
defined('ABSPATH') || exit;

class PH_Data_Client {
    private $predictions_url;
    private $fallback_url;
    private $cache_key = 'ph_predictions_cache';
    private $cache_ttl = 21600;

    public function __construct() {
        $url = get_option('ph_predictions_url', '');
        $this->predictions_url = $url ?: 'https://miravosqueinteresante.github.io/partidos-hoy/latest.json';
        $fallback = get_option('ph_fallback_url', '');
        $this->fallback_url = $fallback ?: 'https://raw.githubusercontent.com/miravosqueinteresante/partidos-hoy/gh-pages/latest.json';
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
        $data = $this->try_fetch_url($this->predictions_url);
        if (!empty($data)) {
            return $data;
        }

        $data = $this->try_fetch_url($this->fallback_url);
        if (!empty($data)) {
            return $data;
        }

        return array();
    }

    private function try_fetch_url($url) {
        if (preg_match('/^[\/~]|^\/|^[A-Z]:/i', $url) || strpos($url, 'localhost') !== false) {
            $local_path = preg_replace('/^~\//', dirname(__FILE__) . '/../../', $url);
            if (file_exists($local_path)) {
                $body = file_get_contents($local_path);
                $data = json_decode($body, true);
                if (json_last_error() === JSON_ERROR_NONE && isset($data['matches'])) {
                    set_transient($this->cache_key, $data, $this->cache_ttl);
                    return $data;
                }
            }
        }

        $response = wp_remote_get($url, array(
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

    public function get_matches_by_group($group, $matches = null) {
        if ($matches === null) {
            $data = $this->get_predictions();
            $matches = isset($data['matches']) ? $data['matches'] : array();
        }
        return array_values(array_filter($matches, function($m) use ($group) {
            return isset($m['group']) && strcasecmp($m['group'], $group) === 0;
        }));
    }

    public function get_matches_by_date($date, $matches = null) {
        if ($matches === null) {
            $data = $this->get_predictions();
            $matches = isset($data['matches']) ? $data['matches'] : array();
        }
        return array_values(array_filter($matches, function($m) use ($date) {
            return isset($m['date']) && substr($m['date'], 0, 10) === $date;
        }));
    }

    public function get_matches_by_team($team, $matches = null) {
        if ($matches === null) {
            $data = $this->get_predictions();
            $matches = isset($data['matches']) ? $data['matches'] : array();
        }
        return array_values(array_filter($matches, function($m) use ($team) {
            return (isset($m['home']) && strcasecmp($m['home'], $team) === 0) ||
                   (isset($m['away']) && strcasecmp($m['away'], $team) === 0);
        }));
    }

    public function search_matches($query, $matches = null) {
        if ($matches === null) {
            $data = $this->get_predictions();
            $matches = isset($data['matches']) ? $data['matches'] : array();
        }
        $query = strtolower(trim($query));
        if (empty($query)) {
            return $matches;
        }
        return array_values(array_filter($matches, function($m) use ($query) {
            return (isset($m['home']) && stripos($m['home'], $query) !== false) ||
                   (isset($m['away']) && stripos($m['away'], $query) !== false);
        }));
    }

    public function add_fallback_endpoint($url) {
        $this->fallback_url = $url;
    }

    public function clear_cache() {
        delete_transient($this->cache_key);
    }
}
