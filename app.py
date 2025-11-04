import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# --- 1. DATEN-SETUP ---
# Die drei orthogonalen Achsen sind:
# X: Leistungsniveau (Performance)
# Y: Fußvolumen (Volume)
# Z: Steifigkeit/Support (Support)

# Daten der Kletterschuhe (simulierte Werte basierend auf der Analyse)
# Skalen:
# Performance (X): 1 (Anfänger) bis 10 (Pure Performance)
# Volumen (Y): 1 (Narrow) bis 3 (Wide)
# Support (Z): 1 (Super Soft) bis 4 (Max Support)

data = {
    'Schuhmodell': [
        'Miura', 'Futura', 'Katana', 'Katana Laces', 'Kataki', 'Python', 'Cobra', 'Solution Comp', 'Solution', 'Theory',
        'Cobra K-ID', 'Skwama', 'TC Pro', 'Testarossa', 'Speedsyer', 'Miura VS', 'Finale', 'Zenit', 'Mythos', 'Mythos Eco',
        'Cobra Eco', 'Tarantulace', 'Tarantula', 'Aragon', 'Finale VS', 'Gekko', 'Stickit', 'Tarantula JR', 'Tarantula RN',
        'Miura XX'
    ],
    'Performance_X': [
        9, 9, 7, 8, 8, 8, 7, 10, 9, 10,  # Performance/Advanced
        8, 8, 8, 10, 10, 9, 5, 6, 4, 4,  # Performance/Advanced/Progressive/All-Round
        6, 2, 2, 3, 5, 1, 1, 1, 1, 10   # All-Round/Beginner/Introductory
    ],
    'Volumen_Y': [
        1, 2, 2, 2, 1, 2, 2, 2, 2, 2,
        2, 2, 2, 3, 2, 3, 2, 2, 2, 2,
        2, 2, 3, 3, 3, 2, 2, 2, 2, 1
    ],
    'Support_Z': [
        3, 2, 3, 4, 3, 2, 2, 2, 3, 2,
        2, 2, 4, 3, 1, 4, 3, 3, 3, 3,
        2, 3, 3, 3, 3, 1, 1, 3, 3, 4
    ]
}

df = pd.DataFrame(data)

# Achsenbeschriftungen
achsen_namen = {
    'Performance_X': 'Leistungsniveau (X-Achse: 1=Anfänger, 10=Pro)',
    'Volumen_Y': 'Fußvolumen (Y-Achse: 1=Schmal, 3=Breit)',
    'Support_Z': 'Steifigkeit/Support (Z-Achse: 1=Soft, 4=Max Support)'
}

# --- 2. LAYOUT-ERSTELLUNG ---
# Initialisiere die Dash-App
app = dash.Dash(__name__)
server = app.server # Wichtig für Gunicorn und Render.com

# Maximale Werte für die Slider
max_x, max_y, max_z = df['Performance_X'].max(), df['Volumen_Y'].max(), df['Support_Z'].max()
min_x, min_y, min_z = df['Performance_X'].min(), df['Volumen_Y'].min(), df['Support_Z'].min()

app.layout = html.Div(
    style={'backgroundColor': '#f9f9f9', 'padding': '20px'},
    children=[
        html.H1("🧗 Kletterschuh-Analyse (3D-XYZ-Plot)", style={'textAlign': 'center', 'color': '#333'}),
        html.P("Interaktive 3D-Visualisierung basierend auf Leistungsniveau (X), Fußvolumen (Y) und Support (Z).",
               style={'textAlign': 'center', 'color': '#555'}),

        # Container für 3D-Plot
        dcc.Graph(id='kletterschuh-3d-plot', style={'height': '600px', 'margin-bottom': '20px'}),

        html.Div(
            style={'display': 'flex', 'flex-direction': 'column', 'gap': '30px', 'padding': '20px', 'border-top': '1px solid #ddd'},
            children=[
                # --- Slider X-Achse (Performance) ---
                html.Div([
                    html.Label(f'Filter X-Achse: {achsen_namen["Performance_X"]}', style={'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='x-range-slider',
                        min=min_x, max=max_x, step=1,
                        marks={i: str(i) for i in range(min_x, max_x + 1)},
                        value=[min_x, max_x]
                    ),
                ]),

                # --- Slider Y-Achse (Volumen) ---
                html.Div([
                    html.Label(f'Filter Y-Achse: {achsen_namen["Volumen_Y"]}', style={'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='y-range-slider',
                        min=min_y, max=max_y, step=1,
                        marks={i: str(i) for i in range(min_y, max_y + 1)},
                        value=[min_y, max_y]
                    ),
                ]),

                # --- Slider Z-Achse (Support) ---
                html.Div([
                    html.Label(f'Filter Z-Achse: {achsen_namen["Support_Z"]}', style={'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='z-range-slider',
                        min=min_z, max=max_z, step=1,
                        marks={i: str(i) for i in range(min_z, max_z + 1)},
                        value=[min_z, max_z]
                    ),
                ]),
            ]
        )
    ]
)

# --- 3. CALLBACKS (Interaktivität und Filterung) ---
@app.callback(
    Output('kletterschuh-3d-plot', 'figure'),
    [Input('x-range-slider', 'value'),
     Input('y-range-slider', 'value'),
     Input('z-range-slider', 'value')]
)
def update_graph(x_range, y_range, z_range):
    # 1. Daten filtern
    filtered_df = df[
        (df['Performance_X'] >= x_range[0]) & (df['Performance_X'] <= x_range[1]) &
        (df['Volumen_Y'] >= y_range[0]) & (df['Volumen_Y'] <= y_range[1]) &
        (df['Support_Z'] >= z_range[0]) & (df['Support_Z'] <= z_range[1])
    ]

    # 2. 3D-Plot erstellen
    fig = go.Figure(
        data=[
            # Alle Schuhe (grau)
            go.Scatter3d(
                x=df['Performance_X'],
                y=df['Volumen_Y'],
                z=df['Support_Z'],
                mode='markers',
                marker=dict(size=6, color='lightgray', opacity=0.3),
                name='Alle Schuhe',
                hoverinfo='text',
                hovertext=df['Schuhmodell']
            ),
            # Gefilterte/Highlighted Schuhe (farbig)
            go.Scatter3d(
                x=filtered_df['Performance_X'],
                y=filtered_df['Volumen_Y'],
                z=filtered_df['Support_Z'],
                mode='markers',
                marker=dict(size=10, color='red', opacity=1.0),
                name='Gefilterte Schuhe',
                hoverinfo='text',
                hovertext=filtered_df['Schuhmodell']
            )
        ]
    )

    # 3. Layout konfigurieren (Rotierbar/Zoombar ist Standard in Scatter3d)
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            xaxis_title=achsen_namen['Performance_X'],
            yaxis_title=achsen_namen['Volumen_Y'],
            zaxis_title=achsen_namen['Support_Z'],
            # Feste Achsenbereiche für bessere Visualisierung beim Filtern
            xaxis=dict(range=[0.5, 10.5]),
            yaxis=dict(range=[0.5, 3.5]),
            zaxis=dict(range=[0.5, 4.5]),
        ),
        showlegend=True
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)