import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# --- 1. DATEN-SETUP (83 Modelle) ---

# --- LA SPORTIVA DATEN (37 Modelle) ---
la_sportiva_modelle = [
    'Miura', 'Futura', 'Katana', 'Katana Laces', 'Kataki', 'Python', 'Cobra', 'Solution Comp', 'Solution', 'Theory',
    'Cobra 4:99', 'Skwama', 'TC Pro', 'Testarossa', 
    'Speedster', 'Miura VS', 'Finale', 'Zenit', 'Mythos', 'Mythos Eco',
    'Cobra Eco', 'Tarantulace', 'Tarantula', 'Aragon', 'Finale VS', 'Gekko', 'Stickit', 'Tarantula JR', 'Tarantula RN',
    'Miura XX',
    'Kubo', 'Tarantula Boulder', 'Mantra', 'Skwama Vegan', 'Mistral', 'Otaki', 'Genius'
]

la_sportiva_support_x = [
    7.0, 4.0, 7.0, 10.0, 7.6, 5.5, 4.0, 4.6, 7.0, 4.0,
    5.5, 4.0, 10.0, 8.5, 
    1.0, 
    10.0, 7.0, 7.0, 8.5, 8.5,
    5.5, 7.0, 7.0, 7.0, 7.0, 1.0, 1.0, 7.0, 7.0, 10.0,
    4.5, 4.5, 1.0, 4.0, 5.5, 8.5, 4.3
]

la_sportiva_performance_y = [
    8.0, 8.8, 5.0, 8.0, 7.8, 7.5, 5.5, 9.8, 9.0, 10.0,
    7.0, 
    8.0, 9.5, 9.5, 
    9.8, 
    9.2, 5.0, 6.0, 4.0, 4.0,
    5.8, 2.0, 2.0, 2.0, 4.8, 1.0, 1.0, 1.0, 1.0, 10.0,
    4.5, 1.4, 7.5, 7.2, 4.0, 7.0, 8.2
]

la_sportiva_volumen_z = [
    1.0, 5.5, 5.5, 5.5, 1.0, 6.4, 5.5, 5.5, 5.5, 5.5,
    5.5, 5.5, 5.5, 10.0, 
    5.5, 
    10.0, 5.5, 5.5, 7.8, 7.8,
    7.8, 7.8, 10.0, 10.0, 10.0, 5.5, 5.5, 7.8, 7.8, 1.0,
    5.0, 7.0, 4.0, 6.5, 5.0, 5.5, 7.0
]

la_sportiva_toe = ['N/A'] * 37


# --- SCARPA DATEN (ZUSAMMENGEFÜHRT, 46 Modelle) ---
scarpa_modelle = [
    'Mago', 'Booster', 'Drago', 'Drago LV', 'Chimera', 'Furia Air', 'Instinct S', 'Instinct VS', 'Instinct VSR', 'Instinct Wmn', 
    'Instinct VS Wmn', 'Force', 'Force Wmn', 'Helix', 'Helix Wmn', 'Origin', 'Origin Wmn', 'Origin VS', 'Origin VS Wmn', 
    'Reflex - Y', 'Reflex VS', 'Reflex VS Wmn', 'Pik! - Y', 'Veloce', 'Veloce L', 'Veloce Wmn', 'Veloce L Wmn', 
    'Generator', 'Generator Mid', 'Generator Wmn', 'Generator Mid Wmn', 'Vapor S', 'Vapor S Wmn', 'Vapor V', 
    'Vapor V LV', 'Arpia V', 'Arpia V Wmn',
    'Vapor', 'Vapor WMN', 'Generator V', 'Generator V WMN', 'Boostic', 'Boostic R', 'Drago - Y', 'Drago XT', 'Instinct VSR LV', 'Instinct'
]

scarpa_support_x = [
    6.5, 4.0, 2.0, 2.0, 4.0, 2.0, 6.5, 6.5, 4.0, 4.0,
    4.0, 6.5, 6.5, 6.5, 6.5, 6.5, 6.5, 4.0, 4.0, 
    4.0, 6.5, 6.5, 4.0, 2.0, 6.5, 2.0, 6.5, 
    9.0, 9.0, 9.0, 9.0, 6.5, 6.5, 6.5, 6.5, 
    6.5, 6.5,
    9.0, 9.0, 9.0, 9.0, 6.5, 9.0, 2.0, 4.0, 4.0, 6.5
]

scarpa_performance_y = [
    8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5,
    8.5, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 
    5.0, 5.0, 5.0, 5.5, 5.0, 5.0, 5.0, 5.0, 
    8.5, 8.5, 8.5, 8.5, 9.0, 9.0, 9.0, 9.0, 
    5.5, 5.5,
    5.5, 5.5, 5.0, 5.0, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5
]

scarpa_volumen_z = [
    5.5, 5.5, 3.0, 3.0, 3.0, 3.0, 5.5, 8.0, 8.0, 5.5,
    5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 
    5.5, 5.5, 5.5, 5.5, 8.0, 8.0, 8.0, 8.0, 
    5.0, 5.0, 5.0, 5.0, 3.0, 3.0, 3.0, 3.0, 
    8.0, 5.5,
    3.0, 3.0, 5.5, 5.5, 5.5, 5.5, 3.0, 3.0, 3.0, 8.0
]

scarpa_toe = [
    'Classic', 'Classic', 'Classic', 'Classic', 'Classic', 'Classic', 'Centre', 'Centre', 'Centre', 'Centre',
    'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 
    'Centre', 'Centre', 'Centre', 'Centre', 'Square', 'Square', 'Square', 'Square',
    'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 
    'Centre', 'Centre', 'Centre',
    'Centre', 'Centre', 'Centre', 'Centre', 'Classic', 'Classic', 'Classic', 'Classic', 'Centre', 'Centre'
]


# --- ZUSAMMENFÜHRUNG DER GESAMTEN DATEN ---
data = {
    'Schuhmodell': la_sportiva_modelle + scarpa_modelle,
    'Support_X': la_sportiva_support_x + scarpa_support_x,
    'Performance_Y': la_sportiva_performance_y + scarpa_performance_y,
    'Volumen_Z': la_sportiva_volumen_z + scarpa_volumen_z,
    'Gruppe': ['La Sportiva'] * 37 + ['Scarpa'] * len(scarpa_modelle), 
    'Toe': la_sportiva_toe + scarpa_toe 
}

df = pd.DataFrame(data)

# --- GRUPPENFARBEN (Scarpa ist Schwarz) ---
GRUPPEN_FARBEN = {
    'La Sportiva': '#F1C31E', # Gelb/Orange
    'Scarpa': '#000000',     # Schwarz
}

# --- ACHSEN-CONFIG ---
MIN_VAL, MAX_VAL = 1, 10
AXIS_RANGE = [1, 10]

slider_support_labels = {i: '' for i in range(MIN_VAL, MAX_VAL + 1)}
slider_performance_labels = {i: '' for i in range(MIN_VAL, MAX_VAL + 1)}
slider_volumen_labels = {i: '' for i in range(MIN_VAL, MAX_VAL + 1)}

slider_support_labels.update({1: 'Min Support', 5: 'Mittel', 10: 'Max Support'})
slider_performance_labels.update({1: 'Min Performance', 5: 'Mittel', 10: 'Max Performance'})
slider_volumen_labels.update({1: 'Schmal', 5: 'Mittel', 10: 'Breit'})


achsen_namen = {
    'Support_X': 'Steifigkeit/Support',
    'Performance_Y': 'Leistungsniveau',
    'Volumen_Z': 'Fußvolumen'
}

achsen_ticks_3d = {
    'Support_X': {1: 'Min Support (1.0)', 5: 'Mittel', 10: 'Max Support (10.0)'},
    'Performance_Y': {1: 'Min Perf (1.0)', 5: 'Mittel', 10: 'Max Perf (10.0)'},
    'Volumen_Z': {1: 'Min Vol (1.0)', 5: 'Mittel', 10: 'Max Vol (10.0)'}
}

# --- 2. HILFSFUNKTION FÜR DIE ERSTELLUNG DER 3D-FIGUR ---
def create_3d_figure(dataframe, filtered_dataframe, x_range, y_range, z_range):
    """Erstellt eine Plotly 3D-Scatter-Figur basierend auf dem Haupt- und dem gefilterten DataFrame."""
    
    fig = go.Figure()

    # 2.1 Plotten der Basis-Punkte (alle, leicht transparent)
    for group_name in dataframe['Gruppe'].unique():
        df_group = dataframe[dataframe['Gruppe'] == group_name]
        group_color = GRUPPEN_FARBEN.get(group_name, 'gray')

        # Erstellung des Hover-Textes (OHNE 'Toe')
        hover_texts = [
            f"Schuh: {row['Schuhmodell']}<br>"
            f"Hersteller: {row['Gruppe']}<br>"
            f"Support (X): {row['Support_X']}<br>"
            f"Performance (Y): {row['Performance_Y']}<br>"
            f"Volumen (Z): {row['Volumen_Z']}"
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

    # 2.2 Plotten der GEFILTERTEN Punkte (Highlighted)
    # Hier wird die Logik geändert: Eine separate Spur FÜR JEDE GRUPPE im gefilterten DF
    for group_name in filtered_dataframe['Gruppe'].unique():
        df_group_filtered = filtered_dataframe[filtered_dataframe['Gruppe'] == group_name]
        group_color = GRUPPEN_FARBEN.get(group_name, 'gray')
        
        highlight_hover_texts = [
            f"Schuh: {row['Schuhmodell']} (Gefiltert)<br>"
            f"Hersteller: {row['Gruppe']}<br>"
            f"Support (X): {row['Support_X']}<br>"
            f"Performance (Y): {row['Performance_Y']}<br>"
            f"Volumen (Z): {row['Volumen_Z']}"
            for index, row in df_group_filtered.iterrows()
        ]

        fig.add_trace(go.Scatter3d(
            x=df_group_filtered['Support_X'],
            y=df_group_filtered['Performance_Y'],
            z=df_group_filtered['Volumen_Z'],
            mode='markers',
            marker=dict(size=10, color=group_color, opacity=1.0), # **FARBE WIRD AUS GRUPPEN_FARBEN GENOMMEN**
            name=f'Gefiltert ({group_name})',
            showlegend=False,
            hoverinfo='text',
            hovertext=highlight_hover_texts
        ))
    
    # 2.3 Permanentes Hinzufügen der Schuhnamen als Annotationen (nur für gefilterte)
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
    
    # 2.4 Layout konfigurieren
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            xaxis=dict(
                title=dict(
                    text=achsen_namen['Support_X'],
                    font=dict(size=14, color="#333"),
                ),
                tickvals=list(achsen_ticks_3d['Support_X'].keys()),
                ticktext=[achsen_ticks_3d['Support_X'].get(k, '') for k in range(MIN_VAL, MAX_VAL + 1)],
                range=[MIN_VAL - 0.5, MAX_VAL + 0.5],
                nticks=MAX_VAL - MIN_VAL + 1
            ),
            yaxis=dict(
                title=dict(
                    text=achsen_namen['Performance_Y'],
                    font=dict(size=14, color="#333"),
                ),
                tickvals=list(achsen_ticks_3d['Performance_Y'].keys()),
                ticktext=[achsen_ticks_3d['Performance_Y'].get(k, '') for k in range(MIN_VAL, MAX_VAL + 1)],
                range=[MIN_VAL - 0.5, MAX_VAL + 0.5],
                nticks=MAX_VAL - MIN_VAL + 1
            ),
            zaxis=dict(
                title=dict(
                    text=achsen_namen['Volumen_Z'],
                    font=dict(size=14, color="#333"),
                ),
                tickvals=list(achsen_ticks_3d['Volumen_Z'].keys()),
                ticktext=[achsen_ticks_3d['Volumen_Z'].get(k, '') for k in range(MIN_VAL, MAX_VAL + 1)],
                range=[MIN_VAL - 0.5, MAX_VAL + 0.5],
                nticks=MAX_VAL - MIN_VAL + 1
            ),
            annotations=annotations
        ),
        showlegend=True
    )
    return fig

# --- 3. DASH LAYOUT ERSTELLUNG ---
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
---
        html.Div(
            style={'display': 'flex', 'flex-direction': 'column', 'gap': '30px', 'padding': '20px', 'border-top': '1px solid #ddd'},
            children=[
                # --- Slider X-Achse (Support) ---
                html.Div([
                    html.Label(f'**Filter:** {achsen_namen["Support_X"]}', style={'fontWeight': 'bold'}),
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
                    html.Label(f'**Filter:** {achsen_namen["Performance_Y"]}', style={'fontWeight': 'bold'}),
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
                    html.Label(f'**Filter:** {achsen_namen["Volumen_Z"]}', style={'fontWeight': 'bold'}),
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

# --- 4. CALLBACKS ---
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
