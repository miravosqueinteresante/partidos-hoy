<?php
defined('ABSPATH') || exit;

class PH_Shortcode {
    private $data_client;

    public function __construct($data_client) {
        $this->data_client = $data_client;
        add_shortcode('partidos-hoy', array($this, 'render'));
        add_shortcode('predicciones_partido', array($this, 'render_single'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_styles'));
    }

    public function enqueue_styles() {
        wp_enqueue_style('ph-frontend', PH_PLUGIN_URL . 'assets/css/frontend.css',
                          array(), PH_VERSION);
    }

    public function render($atts) {
        $atts = shortcode_atts(array(
            'league' => '',
            'limit' => 20,
        ), $atts, 'partidos-hoy');

        $matches = $this->data_client->get_matches_by_league($atts['league']);
        if (empty($matches)) {
            return '<p>' . esc_html__('No hay predicciones disponibles.', 'partidos-hoy') . '</p>';
        }

        $matches = array_slice($matches, 0, intval($atts['limit']));
        ob_start();
        ?>
        <div class="ph-grid">
            <?php foreach ($matches as $match): ?>
            <?php
                $date_str = isset($match['date']) ? $match['date'] : '';
                $formatted_date = $date_str ? date_i18n('d M Y', strtotime($date_str)) : '';
                $venue = isset($match['venue']) ? $match['venue'] : '';
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
                    <span class="ph-team ph-home"><?php echo $this->get_flag($match['home']) . esc_html($match['home']); ?></span>
                    <span class="ph-vs">vs</span>
                    <span class="ph-team ph-away"><?php echo $this->get_flag($match['away']) . esc_html($match['away']); ?></span>
                </div>
                
                <div class="ph-card-bars">
                    <div class="ph-bar-container" title="<?php esc_attr_e('Local', 'partidos-hoy'); ?>">
                        <div class="ph-bar ph-bar-home" style="width: <?php echo $match['probabilities']['home'] * 100; ?>%">
                            <?php echo trim($this->get_flag($match['home'])) . ' ' . $this->format_prob($match['probabilities']['home']); ?>
                        </div>
                    </div>
                    <div class="ph-bar-container" title="<?php esc_attr_e('Empate', 'partidos-hoy'); ?>">
                        <div class="ph-bar ph-bar-draw" style="width: <?php echo $match['probabilities']['draw'] * 100; ?>%">
                            🤝 <?php echo $this->format_prob($match['probabilities']['draw']); ?>
                        </div>
                    </div>
                    <div class="ph-bar-container" title="<?php esc_attr_e('Visitante', 'partidos-hoy'); ?>">
                        <div class="ph-bar ph-bar-away" style="width: <?php echo $match['probabilities']['away'] * 100; ?>%">
                            <?php echo trim($this->get_flag($match['away'])) . ' ' . $this->format_prob($match['probabilities']['away']); ?>
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
            </div>
            <?php endforeach; ?>
        </div>
        <p class="ph-footer-info">
            <?php esc_html_e('Actualizado:', 'partidos-hoy'); ?>
            <?php echo esc_html($this->data_client->get_predictions()['generated_at'] ?? ''); ?>
        </p>
        <?php
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
                <span class="ph-team ph-home"><?php echo $this->get_flag($match['home']) . esc_html($match['home']); ?></span>
                <span class="ph-vs">vs</span>
                <span class="ph-team ph-away"><?php echo $this->get_flag($match['away']) . esc_html($match['away']); ?></span>
            </div>
            
            <div class="ph-card-bars">
                <div class="ph-bar-container" title="<?php esc_attr_e('Local', 'partidos-hoy'); ?>">
                    <div class="ph-bar ph-bar-home" style="width: <?php echo $probs['home'] * 100; ?>%">
                        <?php echo trim($this->get_flag($match['home'])) . ' ' . $this->format_prob($probs['home']); ?>
                    </div>
                </div>
                <div class="ph-bar-container" title="<?php esc_attr_e('Empate', 'partidos-hoy'); ?>">
                    <div class="ph-bar ph-bar-draw" style="width: <?php echo $probs['draw'] * 100; ?>%">
                        🤝 <?php echo $this->format_prob($probs['draw']); ?>
                    </div>
                </div>
                <div class="ph-bar-container" title="<?php esc_attr_e('Visitante', 'partidos-hoy'); ?>">
                    <div class="ph-bar ph-bar-away" style="width: <?php echo $probs['away'] * 100; ?>%">
                        <?php echo trim($this->get_flag($match['away'])) . ' ' . $this->format_prob($probs['away']); ?>
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
        </div>
        <?php
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
}
