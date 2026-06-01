"""
news_sentiment.py — Módulo de Análisis de Sentimiento de Noticias
Usa la API gratuita de Tavily (1000 searches/mes gratis) con búsqueda web
para investigar noticias recientes de cada partido y generar un resumen.

Seguridad:
- La API key se lee de variable de entorno TAVILY_API_KEY
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
    Usa la API de Tavily para buscar noticias recientes sobre el partido
    y generar un resumen de sentimiento + enlaces de fuentes.
    """
    try:
        from tavily import TavilyClient
    except ImportError:
        logging.error("Librería tavily-python no instalada. Ejecuta: pip install tavily-python")
        return None

    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        logging.error("TAVILY_API_KEY no encontrada en variables de entorno.")
        return None

    client = TavilyClient(api_key=api_key)

    query = f"{home_team} vs {away_team} World Cup 2026"

    try:
        search_result = client.search(
            query=query,
            max_results=3,
            search_depth="basic"
        )

        if not search_result or 'results' not in search_result or len(search_result['results']) == 0:
            logging.warning(f"No se encontraron resultados para: {query}")
            return None

        sources = []
        context_parts = []
        for r in search_result['results'][:3]:
            url = r.get('url', '')
            title = r.get('title', '')
            content = r.get('content', '')[:500]
            if url:
                sources.append(url)
            if title and content:
                context_parts.append(f"Título: {title}. Contenido: {content}")

        if not context_parts:
            return None

        context = "\n\n".join(context_parts)

        prompt = f"""Eres un analista deportivo experto. Basándote en estas noticias recientes sobre {home_team} vs {away_team} en el Mundial 2026, genera un resumen de exactamente 3 oraciones sobre:
- Estado actual de ambos equipos
- Lesiones clave si las hay
- Forma reciente
- Sentimiento general de la prensa deportiva

NOTICIAS:
{context}

Responde ÚNICAMENTE con un JSON válido (sin markdown, sin backticks) con este formato exacto:
{{
  "news_sentiment": "Tu resumen de 3 oraciones en español.",
  "news_sources": ["url1", "url2", "url3"]
}}

Reglas:
- Las URLs deben ser exactamente las que aparecen en las noticias (máximo 3).
- No inventes URLs ni información. Si no hay suficientes fuentes, usa las que tengas.
- El resumen debe ser en español.
"""

        # Intentar usar Anthropic si hay API key
        claude_api_key = os.environ.get("ANTHROPIC_API_KEY")
        news_sentiment = None

        if claude_api_key:
            try:
                import anthropic
                client_anthropic = anthropic.Anthropic(api_key=claude_api_key)
                message = client_anthropic.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=300,
                    messages=[{"role": "user", "content": prompt}]
                )
                raw_text = message.content[0].text.strip()
                raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text)
                raw_text = re.sub(r'\s*```$', '', raw_text)
                result = json.loads(raw_text)
                if "news_sentiment" in result and "news_sources" in result:
                    news_sentiment = result["news_sentiment"]
                    # Asegurar que las sources sean válidas
                    result_sources = [s for s in result.get("news_sources", []) if s]
                    if not result_sources:
                        result_sources = sources[:3]
                    logging.info(f"✅ Sentimiento generado para {home_team} vs {away_team}")
                    return {"news_sentiment": news_sentiment, "news_sources": result_sources}
            except Exception as e:
                logging.warning(f"Anthropic no disponible, usando resumen básico: {e}")

        # Fallback: retornar contexto directamente si no hay Anthropic
        summary = f"Noticias recientes sobre {home_team} vs {away_team}: {context[:400]}..."
        return {"news_sentiment": summary, "news_sources": sources[:3] if sources else []}

    except Exception as e:
        logging.error(f"Error buscando noticias con Tavily: {e}")
        return None


def update_predictions_with_news(latest_json_path, max_new_matches=None, date_from=None):
    """
    Lee el latest.json, agrega sentimiento de noticias a cada partido
    que tenga equipos definidos y aún no tenga news_sentiment.

    Args:
        latest_json_path: ruta al archivo latest.json
        max_new_matches: máximo número de partidos nuevos a procesar (None = todos)
        date_from: procesar solo partidos desde esta fecha inclusive (YYYY-MM-DD, None = todos)
    """
    with open(latest_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    matches = data.get("matches", [])
    # Solo partidos con equipos definidos (no TBD) y sin news_sentiment aún
    valid_matches = [
        m for m in matches
        if m.get("home") and m.get("away") and not m.get("news_sentiment")
    ]

    # Filtrar por fecha si se especifica
    if date_from:
        valid_matches = [m for m in valid_matches if m.get("date", "") >= date_from]

    if max_new_matches:
        valid_matches = valid_matches[:max_new_matches]

    updated_count = 0
    for match in valid_matches:
        home = match["home"]
        away = match["away"]
        match_date = match.get("date", "unknown")
        logging.info(f"🔍 [{match_date}] {home} vs {away}...")

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

    # Argumentos: python -m scripts.news_sentiment [max_new_matches] [date_from]
    # Ejemplo: python -m scripts.news_sentiment 8 2026-06-11
    max_new_matches = int(sys.argv[1]) if len(sys.argv) > 1 else None
    date_from = sys.argv[2] if len(sys.argv) > 2 else None

    if date_from:
        logging.info(f"Procesando hasta {max_new_matches or 'todos'} partidos desde {date_from}...")
    else:
        logging.info(f"Procesando hasta {max_new_matches or 'todos'} partidos (sin filtro de fecha)...")

    update_predictions_with_news(predictions_path, max_new_matches=max_new_matches, date_from=date_from)