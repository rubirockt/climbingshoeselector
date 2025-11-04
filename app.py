import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# --- 1. DATEN-SETUP (Skaliert auf 1.0 - 10.0 mit Gruppeninformation) ---

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
    5.8, 2.0, 2.0, 3.0, 4.8, 1.0, 1.0, 1.0, 1.0, 10.0,
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


# --- SCARPA DATEN (46 Modelle) ---
scarpa_modelle_base = [
    'Mago', 'Booster', 'Drago', 'Drago LV', 'Chimera', 'Furia Air', 'Instinct S', 'Instinct VS', 'Instinct VSR', 'Instinct Wmn', 
    'Instinct VS Wmn', 'Force', 'Force Wmn', 'Helix', 'Helix Wmn', 'Origin', 'Origin Wmn', 'Origin VS', 'Origin VS Wmn', 
    'Reflex - Y', 'Reflex VS', 'Reflex VS Wmn', 'Pik! - Y', 'Veloce', 'Veloce L', 'Veloce Wmn', 'Veloce L Wmn', 
    'Generator', 'Generator Mid', 'Generator Wmn', 'Generator Mid Wmn', 'Vapor S', 'Vapor S Wmn', 'Vapor V', 
    'Vapor V LV', # UMBENANNT: War Vapor V Wmn
    'Arpia V', 'Arpia V Wmn'
]

scarpa_support_x_base = [
    6.5, 4.0, 2.0, 2.0, 4.0, 2.0, 6.5, 6.5, 4.0, 4.0,
    4.0, 6.5, 6.5, 6.5, 6.5, 6.5, 6.5, 4.0, 4.0, 
    4.0, 6.5, 6.5, 4.0, 2.0, 6.5, 2.0, 6.5, 
    9.0, 9.0, 9.0, 9.0, 6.5, 6.5, 6.5, 6.5, 
    6.5, 6.5
]

scarpa_performance_y_base = [
    8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5,
    8.5, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 
    5.0, 5.0, 5.0, 5.5, 5.0, 5.0, 5.0, 5.0, 
    8.5, 8.5, 8.5, 8.5, 9.0, 9.0, 9.0, 9.0, 
    5.5, 5.5
]

scarpa_volumen_z_base = [
    5.5, 5.5, 3.0, 3.0, 3.0, 3.0, 5.5, 8.0, 8.0, 5.5,
    5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 
    5.5, 5.5, 5.5, 5.5, 8.0, 8.0, 8.0, 8.0, 
    5.0, 5.0, 5.0, 5.0, 3.0, 3.0, 3.0, 3.0, 
    8.0, 5.5
]

scarpa_toe_base = [
    'Classic', 'Classic', 'Classic', 'Classic', 'Classic', 'Classic', 'Centre', 'Centre', 'Centre', 'Centre',
    'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 
    'Centre', 'Centre', 'Centre', 'Centre', 'Square', 'Square', 'Square', 'Square',
    'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 'Centre', 
    'Centre', 'Centre', 'Centre'
]

# --- NEUE SCARPA MODELLE (9 Stück) ---
scarpa_modelle_neu = [
    'Vapor', 'Vapor WMN', 'Generator V', 'Generator V WMN', 'Boostic', 'Boostic R', 'Drago - Y', 'Drago XT', 'Instinct VSR LV', 'Instinct'
]

scarpa_support_x_neu = [
    9.0, 9.0, 9.0, 9.0, 6.5, 9.0, 2.0, 4.0, 4.0, 6.5
]

scarpa_performance_y_neu = [
    5.5, 5.5, 5.0, 5.0, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5
]

scarpa_volumen_z_neu = [
    3.0, 3.0, 5.5, 5.5, 5.5, 5.5, 3.0, 3.0, 3.0, 8.0
]

scarpa_toe_neu = [
    'Centre', 'Centre', 'Centre', 'Centre', 'Classic', 'Classic', 'Classic', 'Classic', 'Centre', 'Centre'
]

# Füge die neuen Modelle in die Basislisten ein.
scarpa_modelle = scarpa_modelle_base + scarpa_modelle_neu
scarpa_support_x = scarpa_support_x_base + scarpa_support_x_neu
scarpa_performance_y = scarpa_performance_y_base + scarpa_performance_y_neu
scarpa_volumen_z = scarpa_volumen_z_base + scarpa_volumen_z_neu
scarpa_toe = scarpa_toe_base + scarpa_toe_neu


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

# --- GRUPPENFARBEN (SCARPA auf Schwarz geändert) ---
GRUPPEN_FARBEN = {
    'La Sportiva': '#F1C31E', # Gelb/Orange
    'Scarpa': '#000000',     # Schwarz
}

# --- ACHSEN-CONFIG (Unverändert) ---
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


# --- 2. LAYOUT-ERSTELLUNG (Toe-Filter entfernt) ---
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    style={'backgroundColor': '#f9f9f9', 'padding': '20px'},
    children=[
        html.H1("🧗 Kletterschuh-Analyse (3D-XYZ-Plot)", style={'textAlign': 'center', 'color': '#333'}),
        html.P("Visualisierung mit allen Achsen auf den Bereich 1.0 bis 10.0 skaliert. Slider-Auflösung: 0.1",
               style={'textAlign': 'center', 'color': '#555'}),

        dcc.Graph(id='kletterschuh-3d-plot', style={'height': '650px', 'margin-bottom': '20px'}),

        html.Div(
            style={'display': 'flex', 'flex-direction': 'column', 'gap': '30px', 'padding': '20px', 'border-top': '1px solid #ddd'},
            children=[
                # --- Slider X-Achse (Support) ---
                html.Div([
                    html.Label(f'Filter X-Achse: {achsen_namen["Support_X"]}', style={'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='x-range-slider',
                        min=MIN_VAL, max=MAX_VAL, 
                        step=0.1, 
                        marks=slider_support_labels, 
                        value=[MIN_VAL, MAX_VAL]
                    ),
                ]),

                # --- Slider Y-Achse (Performance) ---
                html.Div([
                    html.Label(f'Filter Y-Achse: {achsen_namen["Performance_Y"]}', style={'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='y-range-slider',
                        min=MIN_VAL, max=MAX_VAL, 
                        step=0.1, 
                        marks=slider_performance_labels, 
                        value=[MIN_VAL, MAX_VAL]
                    ),
                ]),

                # --- Slider Z-Achse (Volumen) ---
                html.Div([
                    html.Label(f'Filter Z-Achse: {achsen_namen["Volumen_Z"]}', style={'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='z-range-slider',
                        min=MIN_VAL, max=MAX_VAL, 
                        step=0.1, 
                        marks=slider_volumen_labels, 
                        value=[MIN_VAL, MAX_VAL]
                    ),
                ]),
            ]
        )
    ]
)

# --- 3. CALLBACKS (Logik angepasst) ---
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

    fig = go.Figure()
    
    # 2. Plotten der Basis-Punkte
    for group_name in df['Gruppe'].unique():
        df_group = df[df['Gruppe'] == group_name]
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

    # 3. Plotten der GEFILTERTEN Punkte (Highlighted)
    highlight_hover_texts = [
        f"Schuh: {row['Schuhmodell']} (Gefiltert)<br>"
        f"Hersteller: {row['Gruppe']}<br>"
        f"Support (X): {row['Support_X']}<br>"
        f"Performance (Y): {row['Performance_Y']}<br>"
        f"Volumen (Z): {row['Volumen_Z']}"
        for index, row in filtered_df.iterrows()
    ]

    fig.add_trace(go.Scatter3d(
        x=filtered_df['Support_X'],
        y=filtered_df['Performance_Y'],
        z=filtered_df['Volumen_Z'],
        mode='markers',
        marker=dict(size=10, color='red', opacity=1.0),
        name='Gefiltert/Hervorgehoben',
        showlegend=False,
        hoverinfo='text',
        hovertext=highlight_hover_texts
    ))
    
    # 4. Permanentes Hinzufügen der Schuhnamen als Annotationen (nur für gefilterte)
    annotations = []
    for index, row in filtered_df.iterrows():
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
    
    # 5. Layout konfigurieren
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            xaxis=dict(
                title=dict(
                    text=achsen_namen['Support_X'],
                    font=dict(size=14, color="#333"),
                    standoff=40
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
                    standoff=40
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
                    standoff=40
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

if __name__ == '__main__':
    app.run_server(debug=True)
