import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# --- 1. DATEN-SETUP ---

# Originaldaten (Werte wie zuvor verwendet, da die Funktion sie neu skaliert)
data = {
    'Schuhmodell': [
        'Miura', 'Futura', 'Katana', 'Katana Laces', 'Kataki', 'Python', 'Cobra', 'Solution Comp', 'Solution', 'Theory',
        'Cobra K-ID', 'Skwama', 'TC Pro', 'Testarossa', 'Speedsyer', 'Miura VS', 'Finale', 'Zenit', 'Mythos', 'Mythos Eco',
        'Cobra Eco', 'Tarantulace', 'Tarantula', 'Aragon', 'Finale VS', 'Gekko', 'Stickit', 'Tarantula JR', 'Tarantula RN',
        'Miura XX'
    ],
    # Originalwerte (Performance: 1-10; Volumen: 1-3; Support: 1-4)
    'Performance_Y_orig': [
        8, 8, 5, 8, 8, 8, 5, 10, 9, 10,
        8, 8, 8, 10, 10, 9, 5, 6, 4, 4,
        6, 2, 2, 3, 5, 1, 1, 1, 1, 10
    ],
    'Volumen_Z_orig': [
        1, 2, 2, 2, 1, 2, 2, 2, 2, 2,
        2, 2, 2, 3, 2, 3, 2, 2, 2, 2,
        2, 2, 3, 3, 3, 2, 2, 2, 2, 1
    ],
    'Support_X_orig': [
        3, 2, 3, 4, 3, 2, 2, 2, 3, 2,
        2, 2, 4, 3, 1, 4, 3, 3, 3, 3,
        2, 3, 3, 3, 3, 1, 1, 3, 3, 4
    ]
}

df = pd.DataFrame(data)

# --- FÜGE NEUE INTERPOLATIONSFUNKTION HINZU ---
def linear_interpolate(series):
    """Führt eine lineare Interpolation der Pandas Series auf den Bereich [1, 10] durch."""
    old_min = series.min()
    old_max = series.max()
    new_min = 1
    new_max = 10
    
    # Vermeide Division durch Null, falls alle Werte gleich sind
    if old_max == old_min:
        return pd.Series([new_min] * len(series)) 

    # Lineare Interpolationsformel: NewValue = (OldValue - Old_min) * (New_range / Old_range) + New_min
    new
