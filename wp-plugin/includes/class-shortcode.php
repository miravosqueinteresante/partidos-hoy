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
        <div class="ph-table-wrapper">
            <table class="ph-table">
                <thead>
                    <tr>
                        <th><?php esc_html_e('Partido', 'partidos-hoy'); ?></th>
                        <th class="ph-prob">1</th>
                        <th class="ph-prob">X</th>
                        <th class="ph-prob">2</th>
                        <th class="ph-prob">1X</th>
                        <th class="ph-prob">12</th>
                        <th class="ph-prob">X2</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($matches as $match): ?>
                    <tr>
                        <td class="ph-match">
                            <span class="ph-team ph-home"><?php echo esc_html($match['home']); ?></span>
                            <span class="ph-vs">vs</span>
                            <span class="ph-team ph-away"><?php echo esc_html($match['away']); ?></span>
                        </td>
                        <td class="ph-prob ph-highlight-<?php
                            echo $this->get_highlight_class($match['probabilities'], 'home');
                        ?>"><?php echo $this->format_prob($match['probabilities']['home']); ?></td>
                        <td class="ph-prob"><?php echo $this->format_prob($match['probabilities']['draw']); ?></td>
                        <td class="ph-prob ph-highlight-<?php
                            echo $this->get_highlight_class($match['probabilities'], 'away');
                        ?>"><?php echo $this->format_prob($match['probabilities']['away']); ?></td>
                        <td class="ph-prob"><?php
                            echo $this->format_prob($match['probabilities']['home'] + $match['probabilities']['draw']);
                        ?></td>
                        <td class="ph-prob"><?php
                            echo $this->format_prob($match['probabilities']['home'] + $match['probabilities']['away']);
                        ?></td>
                        <td class="ph-prob"><?php
                            echo $this->format_prob($match['probabilities']['draw'] + $match['probabilities']['away']);
                        ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <p class="ph-footer">
                <?php esc_html_e('Actualizado:', 'partidos-hoy'); ?>
                <?php echo esc_html($this->data_client->get_predictions()['generated_at'] ?? ''); ?>
            </p>
        </div>
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

        $probs = $match['probabilities'];
        ob_start();
        ?>
        <div class="ph-single-card">
            <div class="ph-card-header">
                <span class="ph-card-team"><?php echo esc_html($match['home']); ?></span>
                <span class="ph-card-vs">vs</span>
                <span class="ph-card-team"><?php echo esc_html($match['away']); ?></span>
            </div>
            <div class="ph-card-bars">
                <div class="ph-bar-container">
                    <div class="ph-bar ph-bar-home" style="width: <?php echo $probs['home'] * 100; ?>%">
                        <?php echo $this->format_prob($probs['home']); ?>
                    </div>
                </div>
                <div class="ph-bar-container">
                    <div class="ph-bar ph-bar-draw" style="width: <?php echo $probs['draw'] * 100; ?>%">
                        <?php echo $this->format_prob($probs['draw']); ?>
                    </div>
                </div>
                <div class="ph-bar-container">
                    <div class="ph-bar ph-bar-away" style="width: <?php echo $probs['away'] * 100; ?>%">
                        <?php echo $this->format_prob($probs['away']); ?>
                    </div>
                </div>
            </div>
            <?php if (isset($match['expected_goals'])): ?>
            <div class="ph-xg">
                <span>xG: <?php echo esc_html($match['home']); ?>
                      <?php echo $match['expected_goals']['home']; ?></span>
                <span> - </span>
                <span><?php echo esc_html($match['away']); ?>
                      <?php echo $match['expected_goals']['away']; ?></span>
            </div>
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
}
