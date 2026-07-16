import pandas as pd
import requests
import io
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_football_data_co_uk(league_code='E0', season='2324'):
    """
    Descarga datos históricos y cuotas de apuestas de football-data.co.uk.
    Ideal para entrenar modelos predictivos v2.0 (XGBoost) post-Mundial.
    
    :param league_code: 'E0' (Premier League), 'SP1' (La Liga), etc.
    :param season: '2324' para la temporada 2023-2024.
    :return: DataFrame de Pandas con los resultados y cuotas.
    """
    url = f"https://www.football-data.co.uk/mmz4281/{season}/{league_code}.csv"
    logging.info(f"Descargando datos desde: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Leemos el CSV directamente en Pandas
        df = pd.read_csv(io.StringIO(response.text))
        
        logging.info(f"¡Éxito! {len(df)} partidos descargados.")
        
        # Seleccionamos columnas relevantes para nuestro modelo predictivo
        # FTHG: Goles local, FTAG: Goles visitante, FTR: Resultado (H, D, A)
        # B365H, B365D, B365A: Cuotas de Bet365 (Sabiduría de las masas)
        cols = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'B365H', 'B365D', 'B365A']
        
        # Filtramos columnas que existen (a veces cambian las casas de apuestas)
        available_cols = [c for c in cols if c in df.columns]
        df_clean = df[available_cols].copy()
        
        return df_clean
        
    except requests.RequestException as e:
        logging.error(f"Error al descargar datos: {e}")
        return None

if __name__ == "__main__":
    # Prueba de concepto: Descargar la Premier League 23/24
    df_premier = download_football_data_co_uk('E0', '2324')
    
    if df_premier is not None:
        print("\nPrimeros 5 partidos:")
        print(df_premier.head())
        
        print("\nResumen Estadístico de las Cuotas (Odds):")
        print(df_premier[['B365H', 'B365D', 'B365A']].describe())
        
        # Ejemplo de cómo calcular la probabilidad implícita del mercado
        # Esto es clave para encontrar valor (ineficiencias) con tu propio modelo ELO
        df_premier['Prob_Home_Mercado'] = 1 / df_premier['B365H']
        print("\nProbabilidad Implícita de victoria local calculada desde la cuota:")
        print(df_premier[['HomeTeam', 'AwayTeam', 'B365H', 'Prob_Home_Mercado']].head())
