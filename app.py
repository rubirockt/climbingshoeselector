import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# --- 1. DATEN-CONFIG ---
DATA_DIR = 'data/'
CLIMBING_SHOE_DATA_PATH = DATA_DIR + 'climbingshoedata.csv'
MANUFACTURER_DATA_PATH = DATA_DIR + 'manufacturer.csv'

# Skalen-Grenzen für Robustheit
MIN_VAL, MAX_VAL = 1.0, 10.0


# --- 2. ROBUSTE HILFSFUNKTIONEN ZUM LADEN DER DATEN ---

def load_manufacturer_colors(filepath):
    """
    Lädt die Hersteller-Farben und gibt ein Dictionary zurück.
    Fügt automatisch den Fallback-Hersteller 'Other' hinzu.
    """
    # Startet mit dem Fallback-Hersteller 'Other'
    gruppencodes = {'Other': 'gray'} 
    try:
        df_colors = pd.read_csv(filepath)
        # Konvertiert das DataFrame in ein Dictionary: {'Hersteller': 'Farbcode'}
        # Aktualisiert das Dictionary mit den geladenen Werten
        gruppencodes.update(df_colors.set_index('Hersteller')['Farbcode'].to_dict())
        return gruppencodes
    except FileNotFoundError:
        print(f"FEHLER: Hersteller-Datei {filepath} nicht gefunden. Verwende Fallback-Farben.")
        return gruppencodes # Gibt nur den Fallback zurück
    except Exception as e:
        print(f"FEHLER beim Laden der Herstellerfarben: {e}")
        return gruppencodes # Gibt nur den Fallback zurück

def load_climbing_shoe_data(filepath, manufacturer_colors):
    """
    Lädt, bereinigt und validiert die Schuhdaten gemäß den Robustheitsregeln.
    - Behandelt fehlende Hersteller.
    - Behandelt ungültige/fehlende Koordinaten (setzt auf 5.5).
    - Begrenzt Koordinaten auf die Skala [1.0, 10.0].
    """
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"FEHLER beim Laden der Schuhdaten: {e}")
        # Rückgabe eines Notfall-DataFrames
        return pd.DataFrame({
            'Schuhmodell': ['Datenfehler'],
            'Hersteller': ['Other'],
            'Support_X': [5.5],
            'Performance_Y': [5.5],
            'Volumen_Z': [5.5]
        })

    # --- 2.1. Hersteller-Validierung (Regel: Unbekannter Hersteller -> 'Other') ---
    known_manufacturers = set(manufacturer_colors.keys())
    
    # Fehlende Werte in der Spalte 'Hersteller' mit "Other" füllen
    df['Hersteller'] = df['Hersteller'].fillna('Other') 
    
    # Unbekannte Hersteller (nicht in manufacturer_colors) auf "Other" setzen
    df.loc[~df['Hersteller'].isin(known_manufacturers), 'Hersteller'] = 'Other'


    # --- 2.2. Koordinaten-Validierung (Regeln: NaN -> 5.5, Clip [1.0, 10.0]) ---
    for col in ['Support_X', 'Performance_Y', 'Volumen_Z']:
        # Konvertieren zu numerisch, Fehler werden zu NaN
        df[col] = pd.to_numeric(df[col], errors='coerce') 
        
        # Fehlende/Ungültige Werte auf 5.5 setzen
        df[col] = df[col].fillna(5.5) 
        
        # Werte auf die Skala [1.0, 10.0] begrenzen
        df[col] = df[col].clip(lower=MIN_VAL, upper=MAX_VAL) 

    return df

# Daten laden
GRUPPEN_FARBEN = load_manufacturer_colors(MANUFACTURER_DATA_PATH)
df = load_climbing_shoe_data(CLIMBING_SHOE_DATA_PATH, GRUPPEN_FARBEN)


# --- 3. ACHSEN-CONFIG ---
# Die Achsen-Konfigurationen bleiben unverändert, da die Skala 1-10 fest ist.

# Labels für Slider
slider_support_labels = {i: '' for i in range(int(MIN_VAL), int(MAX_VAL) + 1)}
slider_performance_labels = {i: '' for i in range(int(MIN_VAL), int(MAX_VAL) + 1)}
slider_volumen_labels = {i: '' for i in range(int(MIN_VAL), int(MAX_VAL) + 1)}

slider_support_labels.update({1: 'Min Support', 5: 'Mittel', 10: 'Max Support'})
slider_performance_labels.update({1: 'Min Performance', 5: 'Mittel', 10: 'Max Performance'})
slider_volumen_labels.update({1: 'Schmal', 5: 'Mittel', 10: 'Breit'})


achsen_namen = {
    'Support_X': 'Steifigkeit/Support',
    'Performance_Y': 'Leistungsniveau',
    'Volumen_Z': 'Fußvolumen'
}

# Achsen-Ticks für 3D-Plot
achsen_ticks_3d = {
    'Support_X': {1: 'Min Support (1.0)', 5: 'Mittel', 10: 'Max'}, 
    'Performance_Y': {1: 'Min Perf (1.0)', 5: 'Mittel', 10: 'Max Perf (10.0)'},
    'Volumen_Z': {1: 'Min Vol (1.0)', 5: 'Mittel', 10: 'Max. Volumen'} 
}

# --- 4. HILFSFUNKTION FÜR DIE ERSTELLUNG DER 3D-FIGUR ---
def create_3d_figure(dataframe, filtered_dataframe, x_range, y_range, z_range):
    """Erstellt eine Plotly 3D-Scatter-Figur basierend auf dem Haupt- und dem gefilterten DataFrame."""
    
    fig = go.Figure()

    # Sortiert die Hersteller, um sicherzustellen, dass 'Other' falls vorhanden, zuletzt geplottet wird 
    # (damit es im Fall von Überlappungen nicht die Hauptfarben dominiert)
    manufacturer_order = sorted(dataframe['Hersteller'].unique(), key=lambda x: (x == 'Other', x))

    # 4.1 Plotten der Basis-Punkte (alle, leicht transparent)
    for group_name in manufacturer_order:
        df_group = dataframe[dataframe['Hersteller'] == group_name]
        # Die Farbe wird aus dem dynamisch geladenen Dictionary abgerufen
        group_color = GRUPPEN_FARBEN.get(group_name, 'gray') 

        # Erstellung des Hover-Textes
        hover_texts = [
            f"Schuh: {row['Schuhmodell']}<br>"
            f"Hersteller: {row['Hersteller']}<br>"
            f"Support (X): {row['Support_X']:.1f}<br>"
            f"Performance (Y): {row['Performance_Y']:.1f}<br>"
            f"Volumen (Z): {row['Volumen_Z']:.1f}"
            for index, row in df_group.iterrows()
        ]

        fig.add_trace(go.Scatter3d(
            x=df_group['Support_X'],
            y=df_group['Performance_Y'],
            z=df_group['Volumen_Z'],
            mode='markers',
            marker=dict(size=6, color=group_color, opacity=0.3),
            name=group_name,
            hoverinfo='text',
            hovertext=hover_texts
        ))

    # 4.2 Plotten der GEFILTERTEN Punkte (Highlighted)
    for group_name in filtered_dataframe['Hersteller'].unique():
        df_group_filtered = filtered_dataframe[filtered_dataframe['Hersteller'] == group_name]
        group_color = GRUPPEN_FARBEN.get(group_name, 'gray')
        
        highlight_hover_texts = [
            f"Schuh: {row['Schuhmodell']} (Gefiltert)<br>"
            f"Hersteller: {row['Hersteller']}<br>"
            f"Support (X): {row['Support_X']:.1f}<br>"
            f"Performance (Y): {row['Performance_Y']:.1f}<br>"
            f"Volumen (Z): {row['Volumen_Z']:.1f}"
            for index, row in df_group_filtered.iterrows()
        ]

        fig.add_trace(go.Scatter3d(
            x=df_group_filtered['Support_X'],
            y=df_group_filtered['Performance_Y'],
            z=df_group_filtered['Volumen_Z'],
            mode='markers',
            marker=dict(size=8, color=group_color, opacity=1.0), 
            name=f'Gefiltert ({group_name})',
            showlegend=False,
            hoverinfo='text',
            hovertext=highlight_hover_texts
        ))
    
    # 4.3 Permanentes Hinzufügen der Schuhnamen als Annotationen (nur für gefilterte)
    annotations = []
    for index, row in filtered_dataframe.iterrows():
        annotations.append(
            dict(
                showarrow=False,
                x=row['Support_X'],
                y=row['Performance_Y'],
                z=row['Volumen_Z'],
                text=row['Schuhmodell'],
                xanchor='left',
                yanchor='bottom',
                font=dict(color='darkred', size=9),
            )
        )
    
    # 4.4 Layout konfigurieren
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            xaxis=dict(
                title=dict(
                    text=achsen_namen['Support_X'],
                    font=dict(size=14, color="#333"),
                ),
                tickvals=list(achsen_ticks_3d['Support_X'].keys()),
                ticktext=[achsen_ticks_3d['Support_X'].get(k, '') for k in range(int(MIN_VAL), int(MAX_VAL) + 1)],
                range=[MIN_VAL - 0.5, MAX_VAL + 0.5],
                nticks=int(MAX_VAL - MIN_VAL) + 1
            ),
            yaxis=dict(
                title=dict(
                    text=achsen_namen['Performance_Y'],
                    font=dict(size=14, color="#333"),
                ),
                tickvals=list(achsen_ticks_3d['Performance_Y'].keys()),
                ticktext=[achsen_ticks_3d['Performance_Y'].get(k, '') for k in range(int(MIN_VAL), int(MAX_VAL) + 1)],
                range=[MIN_VAL - 0.5, MAX_VAL + 0.5],
                nticks=int(MAX_VAL - MIN_VAL) + 1
            ),
            zaxis=dict(
                title=dict(
                    text=achsen_namen['Volumen_Z'],
                    font=dict(size=14, color="#333"),
                ),
                tickvals=list(achsen_ticks_3d['Volumen_Z'].keys()),
                ticktext=[achsen_ticks_3d['Volumen_Z'].get(k, '') for k in range(int(MIN_VAL), int(MAX_VAL) + 1)],
                range=[MIN_VAL - 0.5, MAX_VAL + 0.5],
                nticks=int(MAX_VAL - MIN_VAL) + 1
            ),
            annotations=annotations
        ),
        showlegend=True
    )
    return fig

# --- 5. DASH LAYOUT ERSTELLUNG (Bleibt unverändert) ---
app = dash.Dash(__name__)
server = app.server

# Standardwerte für die Slider
default_x_range = [MIN_VAL, MAX_VAL]
default_y_range = [MIN_VAL, MAX_VAL]
default_z_range = [MIN_VAL, MAX_VAL]

# Initialisierung des gefilterten DataFrames für die Standard-Figur
initial_filtered_df = df[
    (df['Support_X'] >= default_x_range[0]) & (df['Support_X'] <= default_x_range[1]) &
    (df['Performance_Y'] >= default_y_range[0]) & (df['Performance_Y'] <= default_y_range[1]) &
    (df['Volumen_Z'] >= default_z_range[0]) & (df['Volumen_Z'] <= default_z_range[1])
]

# Erstelle die initiale 3D-Figur
initial_figure = create_3d_figure(df, initial_filtered_df, default_x_range, default_y_range, default_z_range)

app.layout = html.Div(
    style={'backgroundColor': '#f9f9f9', 'padding': '20px'},
    children=[
        html.H1("🧗 **Climbing Shoe Finder**", style={'textAlign': 'center', 'color': '#333'}),
        html.P("Match your foot & style – Finden Sie Ihren idealen Kletterschuh",
               style={'textAlign': 'center', 'color': '#555'}),

        dcc.Graph(
            id='kletterschuh-3d-plot', 
            figure=initial_figure, 
            style={'height': '650px', 'margin-bottom': '20px'}
        ),
        html.Div(
            style={
                'width': '40%', 
                'marginLeft': '0', 
                'display': 'flex', 
                'flexDirection': 'column', 
                'gap': '30px', 
                'padding': '20px', 
                'borderTop': '1px solid #ddd'
            },
            children=[
                # --- Slider X-Achse (Support) ---
                html.Div([
                    html.Label(f'**{achsen_namen["Support_X"]}**', style={'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='x-range-slider',
                        min=MIN_VAL, max=MAX_VAL, 
                        step=0.1, 
                        marks=slider_support_labels, 
                        value=default_x_range
                    ),
                ]),

                # --- Slider Y-Achse (Performance) ---
                html.Div([
                    html.Label(f'**{achsen_namen["Performance_Y"]}**', style={'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='y-range-slider',
                        min=MIN_VAL, max=MAX_VAL, 
                        step=0.1, 
                        marks=slider_performance_labels, 
                        value=default_y_range
                    ),
                ]),

                # --- Slider Z-Achse (Volumen) ---
                html.Div([
                    html.Label(f'**{achsen_namen["Volumen_Z"]}**', style={'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='z-range-slider',
                        min=MIN_VAL, max=MAX_VAL, 
                        step=0.1, 
                        marks=slider_volumen_labels, 
                        value=default_z_range
                    ),
                ]),
            ]
        )
    ]
)

# --- 6. CALLBACKS (Bleibt unverändert) ---
@app.callback(
    Output('kletterschuh-3d-plot', 'figure'),
    [Input('x-range-slider', 'value'),
     Input('y-range-slider', 'value'),
     Input('z-range-slider', 'value')]
)
def update_graph(x_range, y_range, z_range):
    # 1. Daten filtern (nur X, Y, Z)
    filtered_df = df[
        (df['Support_X'] >= x_range[0]) & (df['Support_X'] <= x_range[1]) &
        (df['Performance_Y'] >= y_range[0]) & (df['Performance_Y'] <= y_range[1]) &
        (df['Volumen_Z'] >= z_range[0]) & (df['Volumen_Z'] <= z_range[1])
    ]

    # 2. Erstellen und Rückgabe der Figur mit der Hilfsfunktion
    return create_3d_figure(df, filtered_df, x_range, y_range, z_range)

# Lokales Starten (wird auf Render ignoriert)
if __name__ == '__main__':
    app.run_server(debug=True)
