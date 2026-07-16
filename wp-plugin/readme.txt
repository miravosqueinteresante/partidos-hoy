=== Partidos Hoy ===
Contributors: partidoshoy
Tags: football, soccer, predictions, analytics
Requires at least: 5.0
Tested up to: 6.7
Requires PHP: 7.4
Stable tag: 1.0.4
License: GPLv2 or later

== Description ==

Pronósticos de fútbol generados con el sistema de ranking ELO.
Las predicciones se actualizan automáticamente cada 6 horas.

For informational and entertainment purposes only. Not affiliated with FIFA or any football federation.

== Installation ==

1. Upload the `partidos-hoy` folder to `/wp-content/plugins/`
2. Activate the plugin
3. Use `[partidos-hoy]` shortcode in any post or page

== Frequently Asked Questions ==

= How are predictions generated? =
Using the World Football ELO rating system, which evaluates team strength based on match results, goal differential, and competition importance.

= How often are predictions updated? =
Every 6 hours via automated pipeline.

= Are you affiliated with FIFA? =
No. This plugin is not affiliated with FIFA or any football federation.

== Changelog ==

= 1.0.4 =
* Security: Added nonce verification to AJAX historical endpoint
* Security: Improved cache clearing with admin_init hook
* Security: Fixed uninstall.php to clean up all options
* Fix: Moved emojis outside translation functions for i18n compliance
* Fix: Consolidated duplicate flag mapping into shared function
* Fix: Improved local path validation in data client
* Fix: Enhanced match results validation

= 1.0.3 =
* Value detection vs Polymarket (v1.2)
* Results post-partido (v1.3)
* Shortcodes documentation in admin

= 1.0.2 =
* Historial en Mundiales (964 partidos 1930-2022)
* Botón compartir en tarjetas
* Traducción nombres equipos a español

= 1.0.1 =
* Schema JSON-LD SportsEvent
* Open Graph + Twitter Cards
* Filtros grupo/fecha/equipo
* Paginación y búsqueda
* Fallback endpoint

= 1.0.0 =
* Initial release

== Upgrade Notice ==

= 1.0.4 =
Security improvements and bug fixes. Recommended update for all installations.
