<?php
defined('ABSPATH') || exit;

class PH_Shortcode {
    private $data_client;
    private $single_match_data = null;

    public function __construct($data_client) {
        $this->data_client = $data_client;
        add_shortcode('partidos-hoy', array($this, 'render'));
        add_shortcode('predicciones_partido', array($this, 'render_single'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_styles'));
        add_action('wp_head', array($this, 'add_og_meta_tags'), 1);
    }

    public function enqueue_styles() {
        wp_enqueue_style('ph-frontend', PH_PLUGIN_URL . 'assets/css/frontend.css',
                          array(), PH_VERSION);
    }

    public function render($atts) {
        $atts = shortcode_atts(array(
            'league' => '',
            'limit' => 20,
            'group' => '',
            'date' => '',
            'team' => '',
            'search' => '',
            'page' => 1,
        ), $atts, 'partidos-hoy');

        if (isset($_GET['search'])) {
            $atts['search'] = sanitize_text_field($_GET['search']);
        }
        if (isset($_GET['ph_page'])) {
            $atts['page'] = max(1, intval($_GET['ph_page']));
        }

        $matches = $this->data_client->get_matches_by_league($atts['league']);

        if (!empty($atts['group'])) {
            $matches = $this->data_client->get_matches_by_group($atts['group'], $matches);
        }
        if (!empty($atts['date'])) {
            $matches = $this->data_client->get_matches_by_date($atts['date'], $matches);
        }
        if (!empty($atts['team'])) {
            $matches = $this->data_client->get_matches_by_team($atts['team'], $matches);
        }
        if (!empty($atts['search'])) {
            $matches = $this->data_client->search_matches($atts['search'], $matches);
        }

        if (empty($matches)) {
            return '<p>' . esc_html__('No hay predicciones disponibles.', 'partidos-hoy') . '</p>';
        }

        $limit = intval($atts['limit']);
        $page = max(1, intval($atts['page']));
        $total_matches = count($matches);
        $total_pages = ceil($total_matches / $limit);
        $offset = ($page - 1) * $limit;
        $matches_page = array_slice($matches, $offset, $limit);

        ob_start();
        ?>
        <div class="ph-search-container">
            <form method="get" class="ph-search-form">
                <input type="text" name="search" class="ph-search-input"
                       placeholder="<?php esc_attr_e('Buscar equipo...', 'partidos-hoy'); ?>"
                       value="<?php echo esc_attr($atts['search']); ?>" />
                <button type="submit" class="ph-search-btn"><?php esc_html_e('Buscar', 'partidos-hoy'); ?></button>
            </form>
        </div>
        <div class="ph-grid">
            <?php foreach ($matches_page as $match): ?>
            <?php
                $date_str = isset($match['date']) ? $match['date'] : '';
                $formatted_date = $date_str ? date_i18n('d M Y', strtotime($date_str)) : '';
                $venue = isset($match['venue']) ? $match['venue'] : '';
                $home_team = isset($match['home']) ? $match['home'] : '';
                $away_team = isset($match['away']) ? $match['away'] : '';
                $home_prob = isset($match['probabilities']['home']) ? $match['probabilities']['home'] : 0;
                $draw_prob = isset($match['probabilities']['draw']) ? $match['probabilities']['draw'] : 0;
                $away_prob = isset($match['probabilities']['away']) ? $match['probabilities']['away'] : 0;
            ?>
            <div class="ph-card">
                <?php if ($formatted_date || $venue): ?>
                <div class="ph-card-banner">
                    <?php if ($formatted_date): ?>
                        <span class="ph-banner-date">🗓️ <?php echo esc_html($formatted_date); ?></span>
                    <?php endif; ?>
                    <?php if ($venue && $venue !== 'TBD'): ?>
                        <span class="ph-banner-venue">📍 <?php echo esc_html($venue); ?></span>
                    <?php endif; ?>
                </div>
                <?php endif; ?>
                <div class="ph-card-header">
                    <span class="ph-team ph-home"><?php echo $this->get_flag($home_team) . esc_html($home_team); ?></span>
                    <span class="ph-vs">vs</span>
                    <span class="ph-team ph-away"><?php echo $this->get_flag($away_team) . esc_html($away_team); ?></span>
                </div>
                
                <div class="ph-card-bars">
                    <div class="ph-bar-container" title="<?php esc_attr_e('Local', 'partidos-hoy'); ?>">
                        <div class="ph-bar ph-bar-home" style="width: <?php echo $home_prob * 100; ?>%">
                            <?php echo trim($this->get_flag($home_team)) . ' ' . $this->format_prob($home_prob); ?>
                        </div>
                    </div>
                    <div class="ph-bar-container" title="<?php esc_attr_e('Empate', 'partidos-hoy'); ?>">
                        <div class="ph-bar ph-bar-draw" style="width: <?php echo $draw_prob * 100; ?>%">
                            🤝 <?php echo $this->format_prob($draw_prob); ?>
                        </div>
                    </div>
                    <div class="ph-bar-container" title="<?php esc_attr_e('Visitante', 'partidos-hoy'); ?>">
                        <div class="ph-bar ph-bar-away" style="width: <?php echo $away_prob * 100; ?>%">
                            <?php echo trim($this->get_flag($away_team)) . ' ' . $this->format_prob($away_prob); ?>
                        </div>
                    </div>
                </div>

                <div class="ph-card-footer">
                    <div class="ph-xg">
                        xG: <?php echo isset($match['expected_goals']) ? esc_html($match['expected_goals']['home'] . ' - ' . $match['expected_goals']['away']) : 'N/A'; ?>
                    </div>
                </div>

                <?php if (!empty($match['news_sentiment'])): ?>
                <details class="ph-news-accordion">
                    <summary>🗞️ Análisis de Noticias</summary>
                    <div class="ph-news-content">
                        <p class="ph-news-text"><?php echo esc_html($match['news_sentiment']); ?></p>
                        <?php if (!empty($match['news_sources']) && is_array($match['news_sources'])): ?>
                            <div class="ph-news-sources">
                                <?php foreach($match['news_sources'] as $idx => $source): ?>
                                    <a href="<?php echo esc_url($source); ?>" target="_blank" rel="noopener noreferrer" class="ph-source-chip">Fuente <?php echo $idx + 1; ?></a>
                                <?php endforeach; ?>
                            </div>
                        <?php endif; ?>
                    </div>
                </details>
                <?php endif; ?>

                <details class="ph-historical-accordion">
                    <summary>📊 Historial en Mundiales</summary>
                    <div class="ph-historical-content" data-home="<?php echo esc_attr($home_team); ?>" data-away="<?php echo esc_attr($away_team); ?>">
                        <p class="ph-historical-loading"><?php esc_html_e('Cargando datos históricos...', 'partidos-hoy'); ?></p>
                    </div>
                </details>
            </div>

            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "SportsEvent",
                "name": "<?php echo esc_js($home_team); ?> vs <?php echo esc_js($away_team); ?>",
                "startDate": "<?php echo esc_js($date_str); ?>",
                "location": {
                    "@type": "Place",
                    "name": "<?php echo esc_js($venue ?: 'TBD'); ?>"
                },
                "competitor": [
                    { "@type": "SportsTeam", "name": "<?php echo esc_js($home_team); ?>" },
                    { "@type": "SportsTeam", "name": "<?php echo esc_js($away_team); ?>" }
                ],
                "description": "<?php echo esc_js(sprintf(__('Predicción ELO: %s %s, Empate %s, %s %s', 'partidos-hoy'), $home_team, $this->format_prob($home_prob), $this->format_prob($draw_prob), $away_team, $this->format_prob($away_prob))); ?>"
            }
            </script>
            <?php endforeach; ?>
        </div>

        <?php if ($total_pages > 1): ?>
        <div class="ph-pagination">
            <span class="ph-page-info">
                <?php printf(esc_html__('Página %d de %d', 'partidos-hoy'), $page, $total_pages); ?>
            </span>
            <div class="ph-page-links">
                <?php if ($page > 1): ?>
                    <a href="<?php echo esc_url(add_query_arg('ph_page', $page - 1)); ?>" class="ph-page-link">&laquo; <?php esc_html_e('Anterior', 'partidos-hoy'); ?></a>
                <?php endif; ?>
                <?php for ($i = 1; $i <= $total_pages; $i++): ?>
                    <a href="<?php echo esc_url(add_query_arg('ph_page', $i)); ?>" class="ph-page-link<?php echo $i === $page ? ' ph-page-active' : ''; ?>"><?php echo $i; ?></a>
                <?php endfor; ?>
                <?php if ($page < $total_pages): ?>
                    <a href="<?php echo esc_url(add_query_arg('ph_page', $page + 1)); ?>" class="ph-page-link"><?php esc_html_e('Siguiente', 'partidos-hoy'); ?> &raquo;</a>
                <?php endif; ?>
            </div>
        </div>
        <?php endif; ?>

        <p class="ph-footer-info">
            <?php esc_html_e('Actualizado:', 'partidos-hoy'); ?>
            <?php echo esc_html($this->data_client->get_predictions()['generated_at'] ?? ''); ?>
        </p>
        <p class="ph-disclaimer">
            <?php esc_html_e('Predicciones generadas por ELO para fines informativos y de entretenimiento. No afiliado con FIFA ni ninguna federación de fútbol.', 'partidos-hoy'); ?>
        </p>
        <?php
        $this->output_historical_js();
        return ob_get_clean();
    }

    public function render_single($atts) {
        $atts = shortcode_atts(array(
            'home' => '',
            'away' => '',
        ), $atts, 'predicciones_partido');

        if (empty($atts['home']) || empty($atts['away'])) {
            return '<p>' . esc_html__('Especificá home="Equipo" away="Equipo"', 'partidos-hoy') . '</p>';
        }

        $match = $this->data_client->get_single_match($atts['home'], $atts['away']);
        if (!$match) {
            return '<p>' . esc_html__('Partido no encontrado.', 'partidos-hoy') . '</p>';
        }

        $date_str = isset($match['date']) ? $match['date'] : '';
        $formatted_date = $date_str ? date_i18n('d M Y', strtotime($date_str)) : '';
        $venue = isset($match['venue']) ? $match['venue'] : '';
        $probs = $match['probabilities'];
        $home_team = isset($match['home']) ? $match['home'] : '';
        $away_team = isset($match['away']) ? $match['away'] : '';
        $home_prob = isset($probs['home']) ? $probs['home'] : 0;
        $draw_prob = isset($probs['draw']) ? $probs['draw'] : 0;
        $away_prob = isset($probs['away']) ? $probs['away'] : 0;

        $this->single_match_data = $match;

        ob_start();
        ?>
        <div class="ph-single-card">
            <?php if ($formatted_date || ($venue && $venue !== 'TBD')): ?>
            <div class="ph-card-banner">
                <?php if ($formatted_date): ?>
                    <span class="ph-banner-date">🗓️ <?php echo esc_html($formatted_date); ?></span>
                <?php endif; ?>
                <?php if ($venue && $venue !== 'TBD'): ?>
                    <span class="ph-banner-venue">📍 <?php echo esc_html($venue); ?></span>
                <?php endif; ?>
            </div>
            <?php endif; ?>
            <div class="ph-card-header">
                <span class="ph-team ph-home"><?php echo $this->get_flag($home_team) . esc_html($home_team); ?></span>
                <span class="ph-vs">vs</span>
                <span class="ph-team ph-away"><?php echo $this->get_flag($away_team) . esc_html($away_team); ?></span>
            </div>
            
            <div class="ph-card-bars">
                <div class="ph-bar-container" title="<?php esc_attr_e('Local', 'partidos-hoy'); ?>">
                    <div class="ph-bar ph-bar-home" style="width: <?php echo $home_prob * 100; ?>%">
                        <?php echo trim($this->get_flag($home_team)) . ' ' . $this->format_prob($home_prob); ?>
                    </div>
                </div>
                <div class="ph-bar-container" title="<?php esc_attr_e('Empate', 'partidos-hoy'); ?>">
                    <div class="ph-bar ph-bar-draw" style="width: <?php echo $draw_prob * 100; ?>%">
                        🤝 <?php echo $this->format_prob($draw_prob); ?>
                    </div>
                </div>
                <div class="ph-bar-container" title="<?php esc_attr_e('Visitante', 'partidos-hoy'); ?>">
                    <div class="ph-bar ph-bar-away" style="width: <?php echo $away_prob * 100; ?>%">
                        <?php echo trim($this->get_flag($away_team)) . ' ' . $this->format_prob($away_prob); ?>
                    </div>
                </div>
            </div>

            <div class="ph-card-footer">
                <div class="ph-xg">
                    xG: <?php echo isset($match['expected_goals']) ? esc_html($match['expected_goals']['home'] . ' - ' . $match['expected_goals']['away']) : 'N/A'; ?>
                </div>
            </div>

            <?php if (!empty($match['news_sentiment'])): ?>
            <details class="ph-news-accordion">
                <summary>🗞️ Análisis de Noticias</summary>
                <div class="ph-news-content">
                    <p class="ph-news-text"><?php echo esc_html($match['news_sentiment']); ?></p>
                    <?php if (!empty($match['news_sources']) && is_array($match['news_sources'])): ?>
                        <div class="ph-news-sources">
                            <?php foreach($match['news_sources'] as $idx => $source): ?>
                                <a href="<?php echo esc_url($source); ?>" target="_blank" rel="noopener noreferrer" class="ph-source-chip">Fuente <?php echo $idx + 1; ?></a>
                            <?php endforeach; ?>
                        </div>
                    <?php endif; ?>
                </div>
            </details>
            <?php endif; ?>

            <details class="ph-historical-accordion">
                <summary>📊 Historial en Mundiales</summary>
                <div class="ph-historical-content" data-home="<?php echo esc_attr($home_team); ?>" data-away="<?php echo esc_attr($away_team); ?>">
                    <p class="ph-historical-loading"><?php esc_html_e('Cargando datos históricos...', 'partidos-hoy'); ?></p>
                </div>
            </details>
        </div>

        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "SportsEvent",
            "name": "<?php echo esc_js($home_team); ?> vs <?php echo esc_js($away_team); ?>",
            "startDate": "<?php echo esc_js($date_str); ?>",
            "location": {
                "@type": "Place",
                "name": "<?php echo esc_js($venue ?: 'TBD'); ?>"
            },
            "competitor": [
                { "@type": "SportsTeam", "name": "<?php echo esc_js($home_team); ?>" },
                { "@type": "SportsTeam", "name": "<?php echo esc_js($away_team); ?>" }
            ],
            "description": "<?php echo esc_js(sprintf(__('Predicción ELO: %s %s, Empate %s, %s %s', 'partidos-hoy'), $home_team, $this->format_prob($home_prob), $this->format_prob($draw_prob), $away_team, $this->format_prob($away_prob))); ?>"
        }
        </script>
        <?php
        $this->output_historical_js();
        return ob_get_clean();
    }

    private function format_prob($prob) {
        return round(floatval($prob) * 100) . '%';
    }

    private function get_highlight_class($probs, $key) {
        $values = array('home' => $probs['home'], 'draw' => $probs['draw'], 'away' => $probs['away']);
        arsort($values);
        return (array_key_first($values) === $key) ? 'yes' : 'no';
    }

    private function get_flag($team_name) {
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
            'Portugal' => '🇵🇹', 'Congo DR' => '🇨🇩', 'Uzbekistan' => '🇺🇿', 'Colombia' => '🇨🇴'
        );
        return isset($flags[$team_name]) ? $flags[$team_name] . ' ' : '';
    }

    public function add_og_meta_tags() {
        $post = get_queried_object();
        $og_title = '';
        $og_description = '';

        if ($post instanceof WP_Post) {
            $content = $post->post_content;
            $pattern = get_shortcode_regex(array('predicciones_partido'));
            if (preg_match('/' . $pattern . '/s', $content, $matches)) {
                $shortcode_content = $matches[5];
                $atts = shortcode_parse_atts($shortcode_content);
                $home = isset($atts['home']) ? $atts['home'] : '';
                $away = isset($atts['away']) ? $atts['away'] : '';
                if ($home && $away) {
                    $og_title = sprintf(__('%s vs %s - Predicción Partidos Hoy', 'partidos-hoy'), $home, $away);
                    $og_description = sprintf(__('Pronóstico ELO para %s vs %s. Probabilidades, análisis y más.', 'partidos-hoy'), $home, $away);
                }
            }
        }

        if (empty($og_title)) {
            $og_title = get_bloginfo('name');
            $og_description = get_bloginfo('description');
        }
        ?>
        <meta property="og:title" content="<?php echo esc_attr($og_title); ?>" />
        <meta property="og:description" content="<?php echo esc_attr($og_description); ?>" />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="<?php echo esc_url(get_permalink()); ?>" />
        <meta property="og:site_name" content="<?php echo esc_attr(get_bloginfo('name')); ?>" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="<?php echo esc_attr($og_title); ?>" />
        <meta name="twitter:description" content="<?php echo esc_attr($og_description); ?>" />
        <?php
    }

    private function output_historical_js() {
        static $historical_js_loaded = false;
        if ($historical_js_loaded) {
            return;
        }
        $historical_js_loaded = true;
        ?>
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.ph-historical-content').forEach(function(container) {
                var home = container.getAttribute('data-home');
                var away = container.getAttribute('data-away');
                if (!home || !away) return;

                var ajaxUrl = '<?php echo esc_js(admin_url('admin-ajax.php')); ?>';
                fetch(ajaxUrl + '?action=ph_historical&home=' + encodeURIComponent(home) + '&away=' + encodeURIComponent(away))
                    .then(function(r) { return r.json(); })
                    .then(function(response) {
                        var matches = response.success ? response.data : [];
                        if (matches.length === 0) {
                            container.innerHTML = '<p class="ph-historical-loading"><?php echo esc_js(__('No hay registros históricos de este enfrentamiento.', 'partidos-hoy')); ?></p>';
                            return;
                        }
                        var lines = [];
                        matches.forEach(function(m) {
                            var score = m.home_score + '-' + m.away_score;
                            if (m.penalty_shootout && m.score_penalties) {
                                score += ' (pen: ' + m.score_penalties + ')';
                            }
                            var stage = m.stage ? m.stage.charAt(0).toUpperCase() + m.stage.slice(1) : '';
                            var scorers = '';
                            if (m.scorers && m.scorers.length > 0) {
                                scorers = m.scorers.slice(0, 4).map(function(s) {
                                    var text = s.player.replace(/^not applicable /, '');
                                    if (s.minute) text += ' ' + s.minute + '\'';
                                    if (s.type === 'penalty') text += ' (p)';
                                    if (s.type === 'own_goal') text += ' (og)';
                                    return text;
                                }).join(', ');
                                if (m.scorers.length > 4) scorers += '...';
                            }
                            var line = m.year + ' (' + stage + '): ' + m.home_team + ' ' + score + ' ' + m.away_team;
                            if (scorers) line += ' — ' + scorers;
                            lines.push(line);
                        });
                        container.innerHTML = '<div class="ph-historical-lines">' + lines.join('<br>') + '</div>';
                    })
                    .catch(function() {
                        container.innerHTML = '<p class="ph-historical-loading"><?php echo esc_js(__('Error al cargar datos históricos.', 'partidos-hoy')); ?></p>';
                    });
            });
        });
        </script>
        <?php
    }
}
