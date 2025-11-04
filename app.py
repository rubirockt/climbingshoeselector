import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# --- 1. DATEN-SETUP (mit geschätzten Dezimalwerten) ---

# Geschätzte Werte mit Dezimalstellen (basierend auf der relativen Position in den Originalplots)
# Die Achsen sind: X=Support, Y=Performance, Z=Volumen
data = {
    'Schuhmodell': [
        'Miura', 'Futura', 'Katana', 'Katana Laces', 'Kataki', 'Python', 'Cobra', 'Solution Comp', 'Solution', 'Theory',
        'Cobra K-ID', 'Skwama', 'TC Pro', 'Testarossa', 'Speedsyer', 'Miura VS', 'Finale', 'Zenit', 'Mythos', 'Mythos Eco',
        'Cobra Eco', 'Tarantulace', 'Tarantula', 'Aragon', 'Finale VS', 'Gekko', 'Stickit', 'Tarantula JR', 'Tarantula RN',
        'Miura XX'
    ],
    # Performance (Original ca. 1.0 bis 10.0)
    'Performance_Y_orig': [
        8.0, 8.5, 5.0, 8.2, 7.8, 7.5, 5.5, 10.0, 9.0, 9.8,
        7.0, 8.0, 9.5, 9.5, 9.8, 9.2, 5.2, 6.0, 4.0, 4.0,
        5.8, 2.0, 2.0, 3.0, 4.8, 1.0, 1.0, 1.0, 1.0, 10.0
    ],
    # Volumen (Original ca. 1.0 bis 3.0)
    'Volumen_Z_orig': [
        1.0, 2.0, 2.0, 2.0, 1.2, 2.0, 2.2, 1.8, 2.0, 2.0,
        2.0, 2.0, 2.0, 3.0, 2.0, 3.0, 2.0, 2.0, 2.5, 2.5,
        2.5, 2.5, 3.0, 3.0, 3.0, 2.0, 2.0, 2.5, 2.5, 1.0
    ],
    # Support (Original ca. 1.0 bis 4.0)
    'Support_X_orig': [
        3.0, 2.0, 3.0, 4.0, 3.0, 2.5, 2.0, 2.0, 3.0, 2.0,
        2.0, 2.0, 4.0, 3.5, 1.0, 4.0, 3.0, 3.0, 3.5, 3.5,
        2.5, 3.0, 3.0, 3.0, 3.0, 1.0, 1.0, 3.0, 3.0, 4.0
    ]
}

df = pd.DataFrame(data)

# --- FÜGE NEUE INTERPOLATIONSFUNKTION HINZU ---
def linear_interpolate(series, new_min=1.5, new_max=9.5):
    """Führt eine lineare Interpolation der Pandas Series auf den Bereich [1.5, 9.5] durch."""
    old_min = series.min()
    old_max = series.max()
    
    # Vermeide Division durch Null, falls alle Werte gleich sind
    if old_max == old_min:
        return pd.Series([new_min] * len(series)) 

    # Lineare Interpolationsformel
    new_series = (series - old_min) * ( (new_max - new_min) / (old_max - old_min) ) + new_min
    
    return new_series

# Skaliere die Originalspalten
df['Support_X'] = linear_interpolate(df['Support_X_orig'])
df['Performance_Y'] = linear_interpolate(df['Performance_Y_orig'])
df['Volumen_Z'] = linear_interpolate(df['Volumen_Z_orig'])

# --- FÜGE OVERLAP-DETEKTION UND OFFSET HINZU ---
def apply_offset(df, columns=['Support_X', 'Performance_Y', 'Volumen_Z'], offset=0.2):
    """Fügt einen künstlichen Offset hinzu, wenn Punkte im 3D-Raum überlappen."""
    
    # Runden auf eine bestimmte Präzision, um "Überlappungen" zu definieren
    df_rounded = df[columns].round(2)
    
    for i in range(len(df)):
        # Prüfe, ob der aktuelle Punkt mit einem vorherigen Punkt übereinst
