import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

# --- 1. DATEN-SETUP (mit angepassten 1-10 Skalenwerten) ---

# Skalen-Konfiguration für die 1-10 Achsen:
# Die Achsen werden von 1 bis 10 skaliert.
# Die Text-Labels werden nur an den relevanten Originalpunkten angezeigt.

# X-Achse: Steifigkeit/Support
# 1: Super Soft
# 4: Soft
# 7: Support
# 10: Max Support
support_ticks = {
    1: 'Super Soft', 2: '', 3: '', 4: 'Soft', 5: '',
    6: '', 7: 'Support', 8: '', 9: '', 10: 'Max Support'
}

# Y-Achse: Leistungsniveau (Performance)
# 1: Kids'
# 2: Introductory
# 5: Progressive / All-Round
# 8: Advanced / Performance
# 10: Pure Performance
performance_ticks = {
    1: "Kids'", 2: 'Introductory', 3: '', 4: '', 5: 'Progressive / All-Round',
    6: '', 7: '', 8: 'Advanced / Performance', 9: '', 10: 'Pure Performance'
}

# Z-Achse: Fußvolumen
# 2: Narrow Volume
# 5: Normal Volume
# 8: Wide Volume
volumen_ticks = {
    1: '', 2: 'Narrow Volume', 3: '', 4: '', 5: 'Normal Volume',
    6: '', 7: '', 8: 'Wide Volume', 9: '', 10: ''
}


data = {
    'Schuhmodell': [
        'Miura', 'Futura', 'Katana', 'Katana Laces', 'Kataki', 'Python', 'Cobra', 'Solution Comp', 'Solution', 'Theory',
        'Cobra K-ID', 'Skwama', 'TC Pro', 'Testarossa', 'Speedsyer', 'Miura VS', 'Finale', 'Zenit', 'Mythos', 'Mythos Eco',
        'Cobra Eco', 'Tarantulace', 'Tarantula', 'Aragon', 'Finale VS', 'Gekko', 'Stickit', 'Tarantula JR', 'Tarantula RN',
        'Miura XX'
    ],
    # Achsen-Zuordnung: X=Support, Y=Performance, Z=Volumen
    'Support_X': [
        7, 4, 7, 10, 7, 4, 4, 4, 7, 4,
        4, 4, 10, 7, 1, 10, 7, 7, 7, 7,
        4, 7, 7, 7, 7, 1, 1, 7, 7, 10
    ],
    'Performance_Y': [
        8, 8, 5, 8, 8, 8, 5, 10, 8, 10,
        5, 8, 8, 10, 10, 8, 5, 5, 5, 5,
        5, 2, 2, 2, 5, 1, 1, 1, 1, 10
    ],
    'Volumen_Z': [
        2, 5, 5, 5, 2, 5, 5, 5, 5, 5,
        5, 5, 5, 8, 5, 8, 5, 5, 5, 5,
        5, 5, 8, 8, 8, 5, 5, 5, 5, 2
    ]
}

df = pd.DataFrame(data)

# Finale Achsenbeschriftungen
achsen_namen = {
    'Support_X': 'Steifigkeit/Support',
    'Performance_Y': 'Leistungsniveau',
    'Volumen_Z': 'Fußvolumen'
}
achsen_ticks = {
    'Support_X': support_ticks,
    'Performance_Y': performance_ticks,
    'Volumen_Z': volumen_ticks
}

# Skalenbereich
AXIS_RANGE = [1, 10]

# --- 2. LAYOUT-ERSTELLUNG ---
app = dash.Dash(__name__)
server = app.server

# Maximale und minimale Achsenwerte (jetzt immer 1 und 10)
min_val, max_val = 1, 10

app.layout = html.Div(
    style={'backgroundColor': '#f9f9f9', 'padding': '20px'},
    children=[
        html.H1("🧗 Kletterschuh-Analyse (3D-XYZ-Plot)", style={'textAlign': 'center', 'color': '#333'}),
        html.P("Interaktive 3D-Visualisierung mit Filterung und benutzerdefinierter Achsenskalierung.",
               style={'textAlign': 'center', 'color': '#555'}),

        # Container für 3D-Plot
        dcc.Graph(id='kletterschuh-3d-plot', style={'height': '650px', 'margin-bottom': '20px'}),

        html.Div(
            style={'display': 'flex', 'flex-direction': 'column', 'gap': '30px', 'padding': '20px', 'border-top': '1px solid #ddd'},
            children=[
                # --- Slider X-Achse (Support) ---
                html.Div([
                    html.Label(f'Filter X-Achse: {achsen_namen["Support_X"]}', style={'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='x-range-slider',
                        min=min_val, max=max_val, step=1,
                        marks={i: str(i) for i in range(min_val, max_val + 1)},
                        value=[min_val, max_val]
                    ),
                ]),

                # --- Slider Y-Achse (Performance) ---
                html.Div([
                    html.Label(f'Filter Y-Achse: {achsen_namen["Performance_Y"]}', style={'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='y-range-slider',
                        min=min_val, max=max_val, step=1,
                        marks={i: str(i) for i in range(min_val, max_val + 1)},
                        value=[min_val, max_val]
                    ),
                ]),

                # --- Slider Z-Achse (Volumen) ---
                html.Div([
                    html.Label(f'Filter Z-Achse: {achsen_namen["Volumen_Z"]}', style={'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='z-range-slider',
                        min=min_val, max=max_val, step=1,
                        marks={i: str(i) for i in range(min_val, max_val + 1)},
                        value=[min_val, max_val]
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
        (df['Support_X'] >= x_range[0]) & (df['Support_X'] <= x_range[1]) &
        (df['Performance_Y'] >= y_range[0]) & (df['Performance_Y'] <= y_range[1]) &
        (df['Volumen_Z'] >= z_range[0]) & (df['Volumen_Z'] <= z_range[1])
    ]

    # 2. 3D-Plot erstellen
    fig = go.Figure()

    # Alle Schuhe (grau)
    fig.add_trace(go.Scatter3d(
        x=df['Support_X'],
        y=df['Performance_Y'],
        z=df['Volumen_Z'],
        mode='markers',
        marker=dict(size=6, color='lightgray', opacity=0.3),
        name='Alle Schuhe',
        hoverinfo='text',
        hovertext=df['Schuhmodell']
    ))

    # Gefilterte/Highlighted Schuhe (farbig)
    fig.add_trace(go.Scatter3d(
        x=filtered_df['Support_X'],
        y=filtered_df['Performance_Y'],
        z=filtered_df['Volumen_Z'],
        mode='markers',
        marker=dict(size=10, color='red', opacity=1.0),
        name='Gefilterte Schuhe',
        hoverinfo='text',
        hovertext=filtered_df['Schuhmodell']
    ))
    
    # 3. Permanentes Hinzufügen der Schuhnamen als Annotationen (nur für gefilterte)
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
    
    # 4. Layout konfigurieren
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            xaxis=dict(
                title=achsen_namen['Support_X'],
                tickvals=list(achsen_ticks['Support_X'].keys()),
                ticktext=list(achsen_ticks['Support_X'].values()),
                range=AXIS_RANGE,
                nticks=10
            ),
            yaxis=dict(
                title=achsen_namen['Performance_Y'],
                tickvals=list(achsen_ticks['Performance_Y'].keys()),
                ticktext=list(achsen_ticks['Performance_Y'].values()),
                range=AXIS_RANGE,
                nticks=10
            ),
            zaxis=dict(
                title=achsen_namen['Volumen_Z'],
                tickvals=list(achsen_ticks['Volumen_Z'].keys()),
                ticktext=list(achsen_ticks['Volumen_Z'].values()),
                range=AXIS_RANGE,
                nticks=10
            ),
            annotations=annotations
        ),
        showlegend=True
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
