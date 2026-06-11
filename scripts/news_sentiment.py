"""
news_sentiment.py — Módulo de Análisis de Sentimiento de Noticias
Usa DuckDuckGo (búsqueda web gratuita, sin API key) + Groq (resúmenes con Llama 3.3 70B, 30 req/min gratis)
para investigar noticias recientes de cada partido y generar un resumen.

Seguridad:
- La API key de Groq se lee de variable de entorno GROQ_API_KEY
- En local: se carga desde .env (gitignored)
- En GitHub Actions: se carga desde GitHub Secrets
"""

import os
import json
import logging
import sys
import re
import time
from datetime import datetime

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


def generate_summary_with_groq(home, away, context, sources):
    """
    Usa Groq (Llama 3.3 70B) para generar un resumen en español de 3 oraciones.
    """
    try:
        from groq import Groq
    except ImportError:
        logging.warning("Groq no instalado, usando resumen básico")
        return None

    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        logging.warning("GROQ_API_KEY no encontrada, usando resumen básico")
        return None

    prompt = f"""Eres un analista deportivo experto. Basándote en estas noticias recientes sobre {home} vs {away} en el Mundial 2026, genera un resumen de exactamente 3 oraciones en español sobre:
- Novedades de cada selección (plantel, concentración, amistosos)
- Jugadores importantes y lesionados
- Preparación y expectativas
No menciones resultados del partido si aún no se jugó.

NOTICIAS:
{context}

Responde ÚNICAMENTE con un JSON válido (sin markdown, sin backticks) con este formato exacto:
{{
  "news_sentiment": "Tu resumen de 3 oraciones en español.",
  "news_sources": ["url1", "url2"]
}}

Reglas estrictas:
- Máximo 3 oraciones en español
- Las URLs deben ser exactamente las proporcionadas
- No inventar información
- Si un equipo tiene varias noticias, priorizá las más relevantes sobre plantel y preparación."""

    try:
        client = Groq(api_key=groq_api_key)
        chat = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un analista deportivo experto cubriendo la previa del Mundial 2026. Responde en español sobre preparación de selecciones, plantel y novedades. Exactamente 3 oraciones en JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=300
        )

        raw_text = chat.choices[0].message.content.strip()
        logging.info(f"Groq raw response: {raw_text[:200]}")
        raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text)
        raw_text = re.sub(r'\s*```$', '', raw_text)
        result = json.loads(raw_text)

        if "news_sentiment" in result:
            news_sentiment = result["news_sentiment"]
            news_sources = sources[:2]
            logging.info(f"✅ Resumen generado con Groq para {home} vs {away}")
            return {"news_sentiment": news_sentiment, "news_sources": news_sources}

    except Exception as e:
        logging.warning(f"Groq falló: {e}")

    return None


def ddg_search(query, max_results=6):
    """
    Busca en DuckDuckGo usando requests + BeautifulSoup (incluido en la mayoría de entornos).
    Si BeautifulSoup no está, usa regex simple.
    """
    try:
        import requests
        from urllib.parse import urlencode, urlparse, parse_qs

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
        }

        resp = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers=headers,
            timeout=12,
        )
        resp.raise_for_status()

        # Parse results - try BeautifulSoup first, fall back to regex
        results = []
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            for article in soup.select(".result"):
                title_el = article.select_one(".result__a")
                snippet_el = article.select_one(".result__snippet")
                if title_el:
                    href = title_el.get("href", "")
                    # DDG uses redirect URLs, extract actual URL
                    if "uddg=" in href:
                        from urllib.parse import parse_qs, urlparse
                        parsed = urlparse(href)
                        qs = parse_qs(parsed.query)
                        href = qs.get("uddg", [href])[0]
                    title = title_el.get_text(strip=True)
                    body = snippet_el.get_text(strip=True) if snippet_el else ""
                    if href and title:
                        results.append({"href": href, "title": title, "body": body})
        except ImportError:
            # Fallback: simple regex extraction
            import re
            blocks = re.findall(
                r'<a rel="nofollow" class="result__a" href="([^"]+)".*?>(.*?)</a>',
                resp.text, re.DOTALL
            )
            for href, title_html in blocks[:max_results]:
                title = re.sub(r'<[^>]+>', '', title_html).strip()
                if href and title:
                    results.append({"href": href, "title": title, "body": ""})
            # Also extract snippets
            snippets = re.findall(
                r'<a class="result__snippet"[^>]*href="([^"]+)".*?>(.*?)</a>',
                resp.text, re.DOTALL
            )
            snippet_map = {}
            for href, body_html in snippets:
                body = re.sub(r'<[^>]+>', '', body_html).strip()
                snippet_map[href] = body
            for r in results:
                r["body"] = snippet_map.get(r["href"], "")

        results = results[:max_results]
        logging.info(f"DDG: {len(results)} resultados para '{query[:50]}...'")
        return results

    except Exception as e:
        logging.warning(f"DuckDuckGo falló para query '{query}': {e}")
    return []


def generate_fallback_summary(home_team, away_team, context_parts):
    titles = []
    for part in context_parts:
        if ". " in part:
            after_bracket = part.split("] ", 1)[1] if "] " in part else part
            title = after_bracket.split(". ")[0].strip()
            if title and len(title) > 10 and title not in titles:
                titles.append(title)
    if titles:
        home_title = ""
        away_title = ""
        for t in titles[:4]:
            if home_team.lower() in t.lower() and not home_title:
                home_title = t
            elif away_team.lower() in t.lower() and not away_title:
                away_title = t
        parts = []
        if home_title:
            parts.append(home_title[:120])
        if away_title:
            parts.append(away_title[:120])
        if parts:
            return "Últimas noticias: " + ". ".join(parts) + "."
    return None


def get_news_sentiment(home_team, away_team, max_retries=2):
    """
    Busca noticias con DuckDuckGo usando una query combinada.
    Luego resume con Groq (Llama 3.3 70B) o fallback estructurado.
    """
    try:
        query = f"{home_team} vs {away_team} World Cup 2026"

        sources = []
        context_parts = []
        seen_urls = set()

        results = ddg_search(query, max_results=6)
        for r in results:
            url = r.get('href', '')
            title = r.get('title', '')
            content = r.get('body', '')[:600]
            if url and url not in seen_urls and 'example.com' not in url:
                seen_urls.add(url)
                sources.append(url)
                if title and content:
                    context_parts.append(f"[Partido] {title}. {content}")

        if not context_parts:
            logging.warning(f"No se encontraron resultados para {home_team} vs {away_team}")
            return None

        context = "\n\n".join(context_parts)

        groq_result = generate_summary_with_groq(home_team, away_team, context, sources)
        if groq_result:
            return groq_result

        summary = generate_fallback_summary(home_team, away_team, context_parts)
        if summary:
            return {"news_sentiment": summary, "news_sources": sources[:3] if sources else []}

        return None

    except Exception as e:
        logging.error(f"Error buscando noticias con Tavily: {e}")
        return None


def update_predictions_with_news(latest_json_path, max_new_matches=None, date_from=None):
    """
    Lee el latest.json, agrega sentimiento de noticias a cada partido
    que tenga equipos definidos y aún no tenga news_sentiment.
    Guarda un cache en data/news_cache.json para evitar re-procesar partidos.
    """
    cache_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'news_cache.json')
    processed_ids = set()
    cache_expired = False
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            cached_at = cache_data.get("cached_at", "2000-01-01T00:00:00")
            cache_ts = datetime.strptime(cached_at, "%Y-%m-%dT%H:%M:%S").timestamp()
            cache_age = time.time() - cache_ts
            if cache_age < 86400:
                processed_ids = set(cache_data.get("processed_ids", []))
                logging.info(f"📦 Cache cargado ({len(processed_ids)} IDs, {int(cache_age/3600)}h de antigüedad)")
            else:
                cache_expired = True
                logging.info(f"♻️ Cache expirado ({int(cache_age/3600)}h > 24h). Reprocesando todos los partidos...")
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logging.warning(f"⚠️ Cache corrupto ({e}), empezando fresco")

    with open(latest_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    matches = data.get("matches", [])

    if cache_expired:
        for m in matches:
            m.pop("news_sentiment", None)
            m.pop("news_sources", None)
        logging.info("🧹 news_sentiment eliminado de todos los partidos por cache expirado")

    valid_matches = [
        m for m in matches
        if m.get("home") and m.get("away")
        and m.get("id") not in processed_ids
        and not m.get("news_sentiment")
    ]

    if date_from:
        valid_matches = [m for m in valid_matches if m.get("date", "") >= date_from]

    valid_matches.sort(key=lambda m: m.get("date", ""))

    if max_new_matches:
        valid_matches = valid_matches[:max_new_matches]

    updated_count = 0
    for i, match in enumerate(valid_matches):
        home = match["home"]
        away = match["away"]
        match_date = match.get("date", "unknown")
        match_id = match.get("id")
        logging.info(f"🔍 [{match_date}] {home} vs {away}...")

        if i > 0:
            time.sleep(1)

        result = get_news_sentiment(home, away)

        if result:
            match["news_sentiment"] = result["news_sentiment"]
            match["news_sources"] = result["news_sources"]
            updated_count += 1
        else:
            logging.warning(f"⚠️ Sin resultados para {home} vs {away}")

        if match_id:
            processed_ids.add(match_id)
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({"cached_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "processed_ids": list(processed_ids)}, f)

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