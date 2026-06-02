<?php
defined('WP_UNINSTALL_PLUGIN') || exit;

delete_option('ph_predictions_url');
delete_option('ph_cache_ttl');

delete_transient('ph_predictions_cache');

delete_metadata('user', 0, 'ph_', '', true);
