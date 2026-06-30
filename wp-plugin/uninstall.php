<?php
defined('WP_UNINSTALL_PLUGIN') || exit;

if (!current_user_can('manage_options')) {
    return;
}

delete_option('ph_predictions_url');
delete_option('ph_fallback_url');
delete_option('ph_cache_ttl');
delete_option('ph_match_results');

delete_transient('ph_predictions_cache');
delete_transient('ph_predictions_cache_check');
delete_transient('ph_historical_all');
