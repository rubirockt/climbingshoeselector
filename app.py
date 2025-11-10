import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import os
from flask import send_from_directory

# --- 1. Konfigurations- und Datenladeroutinen ---

def load_config(filepath='config.csv'):
    """Lädt die Anwendungskonfiguration aus config.csv und erstellt vollständige Dateipfade."""
    try:
        df_config = pd.read_csv(filepath, index_col='Key')
        config = df_config['Value'].to_dict()
        
        # Erstellt vollständige, relative Pfade basierend auf der Konfiguration
        config['SHOE_DATA_PATH'] = os.path.join(config['DATA_DIR'], config['SHOE_DATA_FILE'])
        config['MANUFACTURER_COLORS_PATH'] = os.path.join(config['DATA_DIR'], config['MANUFACTURER_FILE'])
        
        # Speichert den Basis-Pfad für Bilder (wird im Callback verwendet)
        config['IMAGE_ASSET_URL_BASE'] = os.path.join("/", config['DATA_DIR'], config['IMAGE_SUBDIR'])
        
        return config
    except FileNotFoundError:
        print(f"FATAL ERROR: Konfigurationsdatei '{filepath}' nicht gefunden.")
        # Fallback auf Hardcoded-Pfade, um den Betrieb zu ermöglichen
        return {
            'DATA_DIR': 'data/',
            'SHOE_DATA_PATH': 'data/climbingshoedata.csv',
            'MANUFACTURER_COLORS_PATH': 'data/manufacturer.csv',
            'IMAGE_SUBDIR': 'images/',
            'IMAGE_ASSET_URL_BASE': '/data/images/'
        }
    except Exception as e:
        print(f"FATAL ERROR beim Laden der Konfiguration: {e}. Prüfe die Struktur von {filepath}.")
        return None 

def load_manufacturer_colors(filepath):
    """
    Lädt die Hersteller-Farben und gibt ein Dictionary zurück.
    Fügt automatisch den Fallback-Hersteller 'Other' hinzu.
    """
    # Angepasste Farben für bessere Sichtbarkeit auf weißem Hintergrund
    gruppencodes = {'Other': 'gray', 'La Sportiva': '#F1C31E', 'Scarpa': '#0097D9'} 
    try:
        df_colors = pd.read_csv(filepath)
        # Überschreibt Fallbacks nur, wenn der Hersteller in der Datei existiert
        for index, row in df_colors.iterrows():
            gruppencodes[row['Hersteller']] = row['Farbcode']
            
        return gruppencodes
    except FileNotFoundError:
        print(f"FEHLER: Hersteller-Datei {filepath} nicht gefunden. Verwende Fallback-Farben.")
        return gruppencodes
    except Exception as e:
        print(f"FEHLER beim Laden der Herstellerfarben: {e}. Prüfe die Struktur von {filepath}.")
        return gruppencodes

def load_climbing_shoe_data(filepath, manufacturer_colors):
    """
    Lädt und bereinigt die Kletterschuhdaten, wendet Robustheitsregeln an und fügt Farben hinzu.
    """
    try:
        df = pd.read_csv(filepath)
        
        if 'id' not in df.columns:
            df['id'] = range(1, len(df) + 1)
        df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
        
        numeric_cols = ['Support_X', 'Performance_Y', 'Volumen_Z']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(5.5)
            df[col] = df[col].clip(lower=1.0, upper=10.0)

        df['Hersteller'] = df['Hersteller'].fillna('Not provided').astype(str)
        
        def get_display_manufacturer(m):
            # Nutzt den Hersteller, wenn Farbe bekannt, ansonsten 'Other'
            return m if m in manufacturer_colors else 'Other'

        df['Anzeige_Hersteller'] = df['Hersteller'].apply(get_display_manufacturer)
        df['Farbcode'] = df['Anzeige_Hersteller'].map(manufacturer_colors)
        
        # Wird für den Hover-Namen des 3D-Plots verwendet (immer noch Hersteller + Modell)
        df['Vollständiges_Modell'] = df['Anzeige_Hersteller'] + ' ' + df['Schuhmodell']

        # Spalte für die Tabellendarstellung: Hersteller + **Modell** (fett)
        df['Formatierter_Modellname'] = df['Anzeige_Hersteller'] + ' **' + df['Schuhmodell'] + '**'
        
        return df

    except FileNotFoundError:
        print(f"FATAL ERROR: Schuhdaten-Datei {filepath} nicht gefunden.")
        return pd.DataFrame() 
    except Exception as e:
        print(f"FATAL ERROR beim Verarbeiten der Schuhdaten: {e}")
        return pd.DataFrame() 

# --- Globale Dateninitialisierung ---
CONFIG = load_config()
if CONFIG is None:
    raise Exception("Anwendung konnte aufgrund eines Konfigurationsfehlers nicht gestartet werden.")

MANUFACTURER_COLORS = load_manufacturer_colors(CONFIG['MANUFACTURER_COLORS_PATH'])
DF_SHOES = load_climbing_shoe_data(CONFIG['SHOE_DATA_PATH'], MANUFACTURER_COLORS)

if DF_SHOES.empty:
    raise Exception("Anwendung konnte aufgrund fehlender oder fehlerhafter Schuhdaten nicht gestartet werden.")

# --- Dash App Setup ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

PLACEHOLDER_IMAGE_URL = '/assets/placeholder.svg'

# --- Funktionen für Tooltip-Erstellung (für die DataTable) ---
def create_tooltip_data(df_filtered):
    """
    Erstellt die Tooltip-Datenstruktur, zugeordnet zur sichtbaren Spalte 
    'Formatierter_Modellname'.
    """
    tooltip_data = []
    
    for index, row in df_filtered.iterrows():
        tooltip_item = {}
        # Der Tooltip wird der Spalte 'Formatierter_Modellname' zugewiesen
        tooltip_item['Formatierter_Modellname'] = {
            'value': (
                f"Hersteller: {row['Anzeige_Hersteller']}\n\n"
                f"Support: {row['Support_X']:.1f}\n\n"
                f"Performance: {row['Performance_Y']:.1f}\n\n"
                f"Volumen: {row['Volumen_Z']:.1f}"
            ),
            'type': 'markdown'
        }
        tooltip_data.append(tooltip_item)
    return tooltip_data

# --- App Layout ---

app.layout = dbc.Container([
    # Geänderte Überschrift, reduzierte Schriftgröße und Abstand entfernt
    html.H1("Kletterschuh-Finder", className="mt-4 mb-0 text-center", style={'fontSize': '2.1rem'}),
    
    # --- BLOCK 1: 3D Plot (OBEN) ---
    dbc.Row([
        # FIX: Padding von p-4 auf p-0 reduziert, um unnötige Margen auf Mobilgeräten zu beseitigen.
        dbc.Col(
            dcc.Graph(
                id='3d-scatter-plot', 
                style={'height': '70vh'}, 
                className="mt-4"
            ), 
            width=12,
            className="p-0" # Angepasst, um volle Breite zu nutzen
        )
    ]), 
    
    # --- BLOCK 2: Filter, Liste und Bildvorschau (UNTEN) ---
    dbc.Row([ 
        # Spalte 1: Filter-Regler (Linke Seite) (Breite: 5/12)
        dbc.Col([
            html.Div(id='filter-container', children=[
                html.H4("Filterkriterien", className="mb-3", style={'fontSize': '1.05rem'}),
                
                # Zentrierte Überschrift und vereinfachter Text
                html.H5("Support", className="mt-2 text-center", style={'fontSize': '0.9rem'}),
                dcc.RangeSlider(
                    id='support-slider',
                    min=1, max=10, step=0.1, value=[1, 10],
                    marks={i: str(i) for i in range(1, 11)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                
                # Zentrierte Überschrift und vereinfachter Text
                html.H5("Performance", className="mt-4 text-center", style={'fontSize': '0.9rem'}),
                dcc.RangeSlider(
                    id='performance-slider',
                    min=1, max=10, step=0.1, value=[1, 10],
                    marks={i: str(i) for i in range(1, 11)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                
                # Zentrierte Überschrift und vereinfachter Text
                html.H5("Volumen", className="mt-4 text-center", style={'fontSize': '0.9rem'}),
                dcc.RangeSlider(
                    id='volume-slider',
                    min=1, max=10, step=0.1, value=[1, 10],
                    marks={i: str(i) for i in range(1, 11)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),

                html.Label("Hersteller filtern", className="mt-4"),
                dcc.Dropdown(
                    id='manufacturer-checklist',
                    options=[{'label': m, 'value': m} for m in sorted(DF_SHOES['Anzeige_Hersteller'].unique())],
                    value=sorted(DF_SHOES['Anzeige_Hersteller'].unique()),
                    multi=True,
                    className="mt-2"
                )
            ])
        ], md=5, className="p-4 bg-light rounded-3 shadow-sm", style={'minHeight': '500px'}), 

        # Spalte 2: Dynamische Liste und Bildvorschau (Rechte Seite) (Breite: 7/12)
        dbc.Col([
            dbc.Row([
                # Unterspalte 2.1: DataTable (Breite: 7/12 der rechten Spalte)
                dbc.Col([
                    # Abstand zur Tabelle auf 3px reduziert
                    html.H4("Geeignete Modelle", style={'fontSize': '1.05rem', 'marginBottom': '3px'}),
                    html.Div(
                        id='filtered-list-container',
                        style={'height': '100%', 'overflowY': 'auto'}, 
                        children=[
                            dash_table.DataTable(
                                id='shoes-table',
                                columns=[
                                    # Nur die kombinierte Spalte mit Hersteller und Modell wird angezeigt.
                                    {"name": "Modell", "id": "Formatierter_Modellname", "presentation": "markdown"},
                                ],
                                # Daten werden im Callback aktualisiert
                                # Nur die Spalte 'Formatierter_Modellname' wird für die Tabelle vorbereitet
                                data=DF_SHOES[['Formatierter_Modellname']].to_dict('records'),
                                
                                style_header={'display': 'none'}, # Überschriften weiterhin ausblenden
                                
                                # marginTop/paddingTop auf 0px gesetzt, um Abstand zu eliminieren
                                style_table={'overflowY': 'scroll', 'maxHeight': '380px', 'width': '100%', 'marginTop': '0px', 'paddingTop': '0px'}, 
                                
                                row_selectable='single', 
                                selected_rows=[0], 
                                # Tooltip-Daten verwenden nun 'Formatierter_Modellname'
                                tooltip_data=create_tooltip_data(DF_SHOES),
                                tooltip_duration=None,
                                
                                style_data={
                                    'fontSize': '12pt', 
                                    'padding': '5px 10px',
                                    # Textfarbe Schwarz für die gesamte Zelle
                                    'color': '#000000', 
                                },
                                
                                # Bedingte Formatierung nur für Zeilenfarben (keine Herstellerfarben mehr)
                                style_data_conditional=[
                                    {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                                ],
                            )
                        ]
                    )
                ], md=7, className="h-100 d-flex flex-column"), 

                # Unterspalte 2.2: Bildvorschau (Breite: 5/12 der rechten Spalte)
                dbc.Col([
                    html.H4("Modell-Vorschau", className="mb-2", style={'fontSize': '1.05rem'}),
                    html.Div(
                        id='image-display-area',
                        style={'height': 'calc(100% - 30px)'}, 
                        children=[
                            html.Div(
                                id='image-preview-container',
                                className="d-flex justify-content-center align-items-center",
                                style={'height': '70%', 'border': '1px solid #ddd', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9', 'marginBottom': '10px'},
                                children=[
                                    html.Img(id='shoe-image', src=PLACEHOLDER_IMAGE_URL, style={'maxHeight': '100%', 'maxWidth': '100%', 'objectFit': 'contain'})
                                ]
                            ),
                            html.Div(
                                id='shoe-name-info',
                                className="text-center",
                                children=[
                                    html.H3(id='shoe-full-name', children='Scarpa Drago', style={'cursor': 'pointer'}),
                                    dbc.Tooltip( 
                                        id='shoe-name-tooltip',
                                        target='shoe-full-name',
                                        placement='top'
                                    )
                                ]
                            )
                        ]
                    )
                ], md=5, className="h-100 d-flex flex-column")
            ], className="g-4 h-100") 
        ], md=7, className="p-4", style={'minHeight': '500px'}), 
    ], className="g-4")
], fluid=True)


# --- Callbacks ---

# Callback 1: Filtert die Daten und aktualisiert Plot & DataTable
@app.callback(
    [
        dash.Output('3d-scatter-plot', 'figure'),
        dash.Output('shoes-table', 'data'),
        dash.Output('shoes-table', 'tooltip_data'),
        dash.Output('shoes-table', 'selected_rows')
    ],
    [
        dash.Input('support-slider', 'value'),
        dash.Input('performance-slider', 'value'),
        dash.Input('volume-slider', 'value'),
        dash.Input('manufacturer-checklist', 'value')
    ],
    dash.State('shoes-table', 'selected_rows')
)
def update_plot_and_table(support_range, performance_range, volume_range, selected_manufacturers, current_selected_rows):
    # Filterung der Daten
    df_filtered = DF_SHOES[
        (DF_SHOES['Support_X'] >= support_range[0]) & (DF_SHOES['Support_X'] <= support_range[1]) &
        (DF_SHOES['Performance_Y'] >= performance_range[0]) & (DF_SHOES['Performance_Y'] <= performance_range[1]) &
        (DF_SHOES['Volumen_Z'] >= volume_range[0]) & (DF_SHOES['Volumen_Z'] <= volume_range[1]) &
        (DF_SHOES['Anzeige_Hersteller'].isin(selected_manufacturers if selected_manufacturers is not None else []))
    ].copy()
    
    # --- SORTIERUNG HINZUGEFÜGT ---
    # Sortiert die gefilterten Daten alphabetisch nach dem kombinierten Namen
    # Dies stellt sicher, dass die Tabelle immer alphabetisch sortiert ist.
    df_filtered.sort_values(by='Vollständiges_Modell', inplace=True)

    # Erstellung des 3D-Plots
    fig = px.scatter_3d(
        df_filtered, 
        x='Support_X', 
        y='Performance_Y', 
        z='Volumen_Z',
        color='Anzeige_Hersteller',
        # hover_name verwendet weiterhin 'Vollständiges_Modell'
        hover_name='Vollständiges_Modell',
        color_discrete_map=MANUFACTURER_COLORS,
        title=None, 
        labels={
            'Support_X': 'Support (Steifigkeit)', 
            'Performance_Y': 'Performance (Aggressivität)', 
            'Volumen_Z': 'Volumen (Breite/Höhe)',
            'Anzeige_Hersteller': 'Marke'
        }
    )
    # FIX: Setze legend.bgcolor auf transparent
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[0.5, 10.5], ticktext=['1', '2', '3', '4', '5', '6', '7', '8', '9', 'Max'], tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), 
            yaxis=dict(range=[0.5, 10.5]), 
            zaxis=dict(range=[0.5, 10.5], ticktext=['1', '2', '3', '4', '5', '6', '7', '8', '9', 'Max. Volumen'], tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        ),
        # FIX: Legenden-Hintergrund transparent
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)',
            title=dict(text='Marke')
        ),
        # Fügt eine kleine Marge hinzu, falls der p-0 Container zu eng ist
        margin=dict(l=5, r=5, t=5, b=5)
    )

    # Aktualisierung der DataTable-Daten, nun nur mit der formatierten, kombinierten Spalte
    table_data = df_filtered[['Formatierter_Modellname']].to_dict('records')
    
    # Aktualisierung der Tooltip-Daten
    tooltip_data = create_tooltip_data(df_filtered)

    # Versuch, die Auswahl beizubehalten, ansonsten Standard auf erste Zeile
    new_selected_rows = []
    if current_selected_rows is not None and current_selected_rows and current_selected_rows[0] < len(table_data):
        new_selected_rows = [current_selected_rows[0]]
    elif len(table_data) > 0:
        new_selected_rows = [0]
        
    return fig, table_data, tooltip_data, new_selected_rows


# Callback 2: Aktualisiert Bildvorschau und Namen/Tooltip beim Klick auf einen Eintrag in der DataTable
@app.callback(
    [
        dash.Output('shoe-image', 'src'),
        dash.Output('shoe-full-name', 'children'),
        dash.Output('shoe-name-tooltip', 'children')
    ],
    [
        dash.Input('shoes-table', 'selected_rows'),
        dash.Input('shoes-table', 'data')
    ]
)
def update_image_preview(selected_rows, rows):
    default_name = "Kein Schuh ausgewählt"
    default_tooltip = "Bitte wählen Sie einen Schuh aus der Liste."
    
    if selected_rows is None or len(selected_rows) == 0 or len(rows) == 0:
        return PLACEHOLDER_IMAGE_URL, default_name, default_tooltip

    row_index = selected_rows[0]
    
    # Nutze den vollständig formatierten Namen der ausgewählten Zeile zur Suche
    selected_formatted_name = rows[row_index]['Formatierter_Modellname']
    
    # Suche die vollständige Reihe im globalen DataFrame DF_SHOES anhand des formatierten Namens
    shoe_row = DF_SHOES[DF_SHOES['Formatierter_Modellname'] == selected_formatted_name]

    if not shoe_row.empty:
        shoe_data = shoe_row.iloc[0]
        
        # 1. Bild URL
        image_filename = shoe_data['Bildpfad']
        # Die URL muss den Konfigurations-Basispfad nutzen
        if image_filename and pd.notna(image_filename):
            full_image_url = os.path.join(CONFIG['IMAGE_ASSET_URL_BASE'], image_filename)
            # Normalisiere den Pfad für URLs
            image_src = full_image_url.replace('\\', '/').replace('//', '/')
        else:
            image_src = PLACEHOLDER_IMAGE_URL
        
        # 2. Schuhname (Plain Text)
        full_name = f"{shoe_data['Anzeige_Hersteller']} {shoe_data['Schuhmodell']}"
        
        # 3. Tooltip-Inhalt (ohne Achsen-Namen, mit Zeilenumbrüchen)
        tooltip_content = dcc.Markdown(
            f"**Eigenschaften:**\n\n"
            f"Hersteller: **{shoe_data['Hersteller']}**\n\n"
            f"Support: **{shoe_data['Support_X']:.1f}**\n\n"
            f"Performance: **{shoe_data['Performance_Y']:.1f}**\n\n"
            f"Volumen: **{shoe_data['Volumen_Z']:.1f}**"
        )

        return image_src, full_name, tooltip_content
    
    return PLACEHOLDER_IMAGE_URL, default_name, default_tooltip


# --- Gunicorn/WSGI Server Fix und NEUE ROUTE ---
server = app.server

@server.route(f"/{CONFIG['DATA_DIR']}<path:path>")
def serve_static(path):
    # Dient statische Dateien aus dem konfigurierten Datenverzeichnis (z.B. data/)
    return send_from_directory(CONFIG['DATA_DIR'], path)
