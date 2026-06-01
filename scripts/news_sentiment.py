"""
news_sentiment.py — Módulo de Análisis de Sentimiento de Noticias
Usa la API gratuita de Gemini (Google) con Google Search Grounding
para investigar noticias recientes de cada partido y generar un resumen.

Seguridad:
- La API key se lee de variable de entorno GEMINI_API_KEY
- En local: se carga desde .env (gitignored)
- En GitHub Actions: se carga desde GitHub Secrets
"""

import os
import json
import logging
import sys
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cargamos .env si existe (para desarrollo local)
def load_dotenv():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())
        logging.info("Variables de entorno cargadas desde .env")

load_dotenv()


def get_news_sentiment(home_team, away_team):
    """
    Usa la API de Gemini para buscar noticias recientes sobre el partido
    y generar un resumen de sentimiento + enlaces de fuentes.
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        logging.error("Librería google-genai no instalada. Ejecuta: pip install google-genai")
        return None

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logging.error("GEMINI_API_KEY no encontrada en variables de entorno.")
        return None

    client = genai.Client(api_key=api_key)

    prompt = f"""Eres un analista deportivo experto. Investiga las noticias más recientes 
sobre el partido de fútbol del Mundial 2026: {home_team} vs {away_team}.

Responde ÚNICAMENTE con un JSON válido (sin markdown, sin backticks, sin texto extra) con este formato exacto:
{{
  "news_sentiment": "Un resumen de exactamente 3 oraciones sobre el estado actual de ambos equipos, lesiones clave, forma reciente y el sentimiento general de la prensa deportiva.",
  "news_sources": ["url_real_1", "url_real_2", "url_real_3"]
}}

Reglas:
- El resumen debe ser en español.
- Las URLs deben ser de artículos reales y verificables.
- Máximo 3 fuentes.
- No inventes URLs. Si no encuentras fuentes reales, devuelve un array vacío.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.3,
            )
        )

        raw_text = response.text.strip()
        # Limpiar posibles backticks de markdown
        raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text)
        raw_text = re.sub(r'\s*```$', '', raw_text)
        
        result = json.loads(raw_text)

        # Validamos la estructura
        if "news_sentiment" in result and "news_sources" in result:
            logging.info(f"✅ Sentimiento generado para {home_team} vs {away_team}")
            return result
        else:
            logging.warning(f"Respuesta de Gemini no tiene la estructura esperada: {raw_text[:200]}")
            return None

    except json.JSONDecodeError as e:
        logging.error(f"Error parseando JSON de Gemini: {e} — Respuesta: {raw_text[:300]}")
        return None
    except Exception as e:
        logging.error(f"Error llamando a Gemini API: {e}")
        return None


def update_predictions_with_news(latest_json_path, max_matches=None):
    """
    Lee el latest.json, agrega sentimiento de noticias a cada partido
    que tenga equipos definidos, y guarda el resultado.
    """
    with open(latest_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    matches = data.get("matches", [])
    # Solo procesar partidos con equipos definidos (no TBD)
    valid_matches = [m for m in matches if m.get("home") and m.get("away")]

    if max_matches:
        valid_matches = valid_matches[:max_matches]

    updated_count = 0
    for match in valid_matches:
        home = match["home"]
        away = match["away"]
        logging.info(f"🔍 Investigando: {home} vs {away}...")

        result = get_news_sentiment(home, away)

        if result:
            match["news_sentiment"] = result["news_sentiment"]
            match["news_sources"] = result["news_sources"]
            updated_count += 1
        else:
            logging.warning(f"⚠️ Sin resultados para {home} vs {away}")

    # Guardar
    with open(latest_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logging.info(f"🎉 ¡Listo! {updated_count}/{len(valid_matches)} partidos actualizados con noticias.")


if __name__ == "__main__":
    predictions_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'predictions', 'latest.json'
    )
    
    # Por defecto procesamos solo 3 partidos para probar
    max_matches = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    
    logging.info(f"Procesando {max_matches} partidos...")
    update_predictions_with_news(predictions_path, max_matches=max_matches)
