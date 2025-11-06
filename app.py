import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import os

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
        return None # Gibt None zurück, um einen klaren Fehler beim Start zu erzwingen

def load_manufacturer_colors(filepath):
    """
    Lädt die Hersteller-Farben und gibt ein Dictionary zurück.
    Fügt automatisch den Fallback-Hersteller 'Other' hinzu.
    """
    # Standard-Fallback-Initialisierung
    gruppencodes = {'Other': 'gray'} 
    try:
        df_colors = pd.read_csv(filepath)
        # Konvertiert das DataFrame in ein Dictionary: {'Hersteller': 'Farbcode'}
        gruppencodes.update(df_colors.set_index('Hersteller')['Farbcode'].to_dict())
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
        
        # Sicherstellen, dass die 'id' Spalte existiert und numerisch ist
        if 'id' not in df.columns:
            df['id'] = range(1, len(df) + 1)
        df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
        
        # --- Robustheit 1: Numerische Spalten bereinigen und konvertieren ---
        numeric_cols = ['Support_X', 'Performance_Y', 'Volumen_Z']
        for col in numeric_cols:
            # Setze NaN-Werte und nicht-numerische Einträge auf 5.5
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(5.5)
            
            # --- Robustheit 2: Skalierung (1-10) prüfen ---
            df[col] = df[col].clip(lower=1.0, upper=10.0)

        # --- Robustheit 3: Hersteller und Farbe zuweisen ---
        
        # Leere oder NaN Hersteller werden temporär auf 'Not provided' gesetzt
        df['Hersteller'] = df['Hersteller'].fillna('Not provided').astype(str)
        
        def get_display_manufacturer(m):
            # Wenn der Hersteller in den geladenen Farben nicht existiert, verwende 'Other'
            return m if m in manufacturer_colors else 'Other'

        df['Anzeige_Hersteller'] = df['Hersteller'].apply(get_display_manufacturer)
        df['Farbcode'] = df['Anzeige_Hersteller'].map(manufacturer_colors)
        
        # --- NEUE SPALTE FÜR EINZELSPALTEN-ANZEIGE (Punkt 3) ---
        df['Vollständiges_Modell'] = df['Anzeige_Hersteller'] + ' ' + df['Schuhmodell']
        
        return df

    except FileNotFoundError:
        print(f"FATAL ERROR: Schuhdaten-Datei {filepath} nicht gefunden.")
        return pd.DataFrame() # Leeres DataFrame bei schwerem Fehler
    except Exception as e:
        print(f"FATAL ERROR beim Verarbeiten der Schuhdaten: {e}")
        return pd.DataFrame() # Leeres DataFrame bei schwerem Fehler

# --- Globale Dateninitialisierung ---
CONFIG = load_config()
if CONFIG is None:
    # Kann nicht fortfahren, wenn die Konfiguration fehlschlägt
    raise Exception("Anwendung konnte aufgrund eines Konfigurationsfehlers nicht gestartet werden.")

MANUFACTURER_COLORS = load_manufacturer_colors(CONFIG['MANUFACTURER_COLORS_PATH'])
DF_SHOES = load_climbing_shoe_data(CONFIG['SHOE_DATA_PATH'], MANUFACTURER_COLORS)

if DF_SHOES.empty:
    raise Exception("Anwendung konnte aufgrund fehlender oder fehlerhafter Schuhdaten nicht gestartet werden.")

# --- Dash App Setup ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# URL für das graue Rechteck (wird in assets/placeholder.svg erwartet)
PLACEHOLDER_IMAGE_URL = '/assets/placeholder.svg'

# --- Funktionen für Tooltip-Erstellung (für die DataTable) ---
def create_tooltip_data(df_filtered):
    """Erstellt die Tooltip-Datenstruktur für die DataTable."""
    tooltip_data = []
    
    # Tooltip-Inhalte für jede Zeile
    for index, row in df_filtered.iterrows():
        tooltip_item = {}
        # Der Tooltip wird nur für die Spalte 'Vollständiges_Modell' angezeigt
        tooltip_item['Vollständiges_Modell'] = {
            'value': (
                f"Hersteller: {row['Anzeige_Hersteller']}\n"
                f"Support (X): {row['Support_X']:.1f}\n"
                f"Performance (Y): {row['Performance_Y']:.1f}\n"
                f"Volumen (Z): {row['Volumen_Z']:.1f}"
            ),
            'type': 'markdown'
        }
        tooltip_data.append(tooltip_item)
    return tooltip_data

# --- App Layout ---
app.layout = dbc.Container([
    html.H1("3D Kletterschuh-Finder (Support vs. Performance vs. Volumen)", className="my-4 text-center"),
    
    # --- BLOCK 1: 3D Plot (JETZT OBEN) (Punkt 1) ---
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='3d-scatter-plot', style={'height': '70vh'}, className="mt-4"), 
            width=12,
            className="p-4"
        )
    ]), # g-4 entfernt unnötige Gutter
    
    # --- BLOCK 2: Filter, Liste und Bildvorschau (JETZT UNTEN) (Punkt 1) ---
    dbc.Row([ 
        # Spalte 1: Filter-Regler (Linke Seite)
        dbc.Col([
            html.Div(id='filter-container', children=[
                html.H4("Filterkriterien", className="mb-3"),
                
                html.Label("Minimaler Support (X-Achse)", className="mt-2"),
                dcc.RangeSlider(
                    id='support-slider',
                    min=1, max=10, step=0.1, value=[1, 10],
                    marks={i: str(i) for i in range(1, 11)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                
                html.Label("Minimale Performance (Y-Achse)", className="mt-4"),
                dcc.RangeSlider(
                    id='performance-slider',
                    min=1, max=10, step=0.1, value=[1, 10],
                    marks={i: str(i) for i in range(1, 11)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                
                html.Label("Minimales Volumen (Z-Achse)", className="mt-4"),
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
        ], md=4, className="p-4 bg-light rounded-3 shadow-sm", style={'minHeight': '500px'}), # 4 von 12 Spalten für Filter

        # Spalte 2: Dynamische Liste und Bildvorschau (Rechte Seite)
        dbc.Col([
            dbc.Row([
                # Unterspalte 2.1: DataTable (40% der rechten Spalte)
                dbc.Col([
                    html.H4("Gefilterte Modelle", className="mb-2"),
                    html.Div(
                        id='filtered-list-container',
                        style={'height': '100%', 'overflowY': 'auto'}, 
                        children=[
                            dash_table.DataTable(
                                id='shoes-table',
                                # --- NUR NOCH EINE SICHTBARE SPALTE (Punkt 3) ---
                                # 'Schuhmodell' wird nur für die interne Logik übergeben und versteckt
                                columns=[
                                    {"name": "Modell", "id": "Vollständiges_Modell"},
                                    {"name": "Schuhmodell", "id": "Schuhmodell", "hidden": True} 
                                ],
                                data=DF_SHOES[['Vollständiges_Modell', 'Schuhmodell']].to_dict('records'),
                                style_header={
                                    'backgroundColor': 'rgb(230, 230, 230)',
                                    'fontWeight': 'bold'
                                },
                                # --- MAX HÖHE UND SCROLLBAR (Punkt 2) ---
                                style_table={'overflowY': 'scroll', 'maxHeight': '400px'}, 
                                # Versteckt die Radio-Buttons und erlaubt Auswahl per Klick (Punkt 4)
                                row_selectable='single', 
                                selected_rows=[0], 
                                tooltip_data=create_tooltip_data(DF_SHOES),
                                tooltip_duration=None,
                                # --- SPALTE VERSTECKEN ---
                                style_data_conditional=[
                                    {'if': {'column_id': 'Schuhmodell'}, 'display': 'none'} 
                                ]
                            )
                        ]
                    )
                ], md=5, className="h-100 d-flex flex-column"), # 5 von 12 Spalten der rechten Seite (ca. 40%)

                # Unterspalte 2.2: Bildvorschau (60% der rechten Spalte)
                dbc.Col([
                    html.H4("Modell-Vorschau", className="mb-2"),
                    html.Div(
                        id='image-display-area',
                        style={'height': 'calc(100% - 30px)'}, 
                        children=[
                            # Container für das Bild (flexible Größe)
                            html.Div(
                                id='image-preview-container',
                                className="d-flex justify-content-center align-items-center",
                                style={'height': '70%', 'border': '1px solid #ddd', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9', 'marginBottom': '10px'},
                                children=[
                                    html.Img(id='shoe-image', src=PLACEHOLDER_IMAGE_URL, style={'maxHeight': '100%', 'maxWidth': '100%', 'objectFit': 'contain'})
                                ]
                            ),
                            # Name des Schuhs (dynamisch) mit Tooltip
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
                ], md=7, className="h-100 d-flex flex-column") # 7 von 12 Spalten der rechten Seite (ca. 60%)
            ], className="g-4 h-100") # g-4 beibehlten für Abstand
        ], md=8, className="p-4", style={'minHeight': '500px'}), # 8 von 12 Spalten für DataTable und Bildvorschau
    ], className="g-4") # Haupt-Row Gutter
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
    # State, um die aktuelle Auswahl beizubehalten, falls möglich
    dash.State('shoes-table', 'selected_rows')
)
def update_plot_and_table(support_range, performance_range, volume_range, selected_manufacturers, current_selected_rows):
    # Filterung der Daten
    df_filtered = DF_SHOES[
        (DF_SHOES['Support_X'] >= support_range[0]) & (DF_SHOES['Support_X'] <= support_range[1]) &
        (DF_SHOES['Performance_Y'] >= performance_range[0]) & (DF_SHOES['Performance_Y'] <= performance_range[1]) &
        (DF_SHOES['Volumen_Z'] >= volume_range[0]) & (DF_SHOES['Volumen_Z'] <= volume_range[1]) &
        # Sicherstellen, dass selected_manufacturers nicht None ist
        (DF_SHOES['Anzeige_Hersteller'].isin(selected_manufacturers if selected_manufacturers is not None else []))
    ].copy()

    # Erstellung des 3D-Plots
    fig = px.scatter_3d(
        df_filtered, 
        x='Support_X', 
        y='Performance_Y', 
        z='Volumen_Z',
        color='Anzeige_Hersteller',
        color_discrete_map=MANUFACTURER_COLORS,
        hover_data=['Vollständiges_Modell', 'Support_X', 'Performance_Y', 'Volumen_Z'],
        title="Kletterschuh-Positionierung",
        labels={'Support_X': 'Support (Steifigkeit)', 'Performance_Y': 'Performance (Aggressivität)', 'Volumen_Z': 'Volumen (Breite/Höhe)'}
    )
    fig.update_layout(scene=dict(xaxis=dict(range=[0.5, 10.5]), yaxis=dict(range=[0.5, 10.5]), zaxis=dict(range=[0.5, 10.5])))

    # Aktualisierung der DataTable-Daten (Jetzt mit Vollständiges_Modell und dem versteckten Schuhmodell-Key)
    table_data = df_filtered[['Vollständiges_Modell', 'Schuhmodell']].to_dict('records')
    
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
    # Setzt Default-Werte für den Fall, dass keine Zeile ausgewählt ist
    default_name = "Kein Schuh ausgewählt"
    default_tooltip = "Bitte wählen Sie einen Schuh aus der Liste."
    
    # Prüft, ob eine Zeile ausgewählt wurde und Daten vorhanden sind
    if selected_rows is None or len(selected_rows) == 0 or len(rows) == 0:
        # Gibt das leere Bild und den Standardnamen zurück
        return PLACEHOLDER_IMAGE_URL, default_name, default_tooltip

    # Holt den Index der ausgewählten Zeile
    row_index = selected_rows[0]
    
    # Holt den versteckten Schlüssel 'Schuhmodell' aus den aktuellen (gefilterten) Daten der Tabelle
    selected_shoe_model = rows[row_index]['Schuhmodell']
    
    # Findet die vollständige Zeile im vollständigen DF_SHOES
    shoe_row = DF_SHOES[DF_SHOES['Schuhmodell'] == selected_shoe_model]

    if not shoe_row.empty:
        shoe_data = shoe_row.iloc[0]
        
        # 1. Bild URL
        image_filename = shoe_data['Bildpfad']
        if image_filename and pd.notna(image_filename):
            # Konstruiert den vollständigen Pfad
            full_image_url = os.path.join(CONFIG['IMAGE_ASSET_URL_BASE'], image_filename)
            # Bereinigt den Pfad für URL-Verwendung im Webbrowser
            image_src = full_image_url.replace('\\', '/').replace('//', '/')
        else:
            # Fallback, falls 'Bildpfad' leer ist
            image_src = PLACEHOLDER_IMAGE_URL
        
        # 2. Schuhname (Hersteller + Modell)
        full_name = shoe_data['Vollständiges_Modell']
        
        # 3. Tooltip-Inhalt (Markdown-Format)
        tooltip_content = dcc.Markdown(
            f"**Eigenschaften:**\n"
            f"Hersteller: **{shoe_data['Hersteller']}**\n"
            f"Support (X): **{shoe_data['Support_X']:.1f}**\n"
            f"Performance (Y): **{shoe_data['Performance_Y']:.1f}**\n"
            f"Volumen (Z): **{shoe_data['Volumen_Z']:.1f}**"
        )

        return image_src, full_name, tooltip_content
    
    # Fallback, wenn der Schuhname nicht im DF_SHOES gefunden wird (sollte nicht passieren)
    return PLACEHOLDER_IMAGE_URL, default_name, default_tooltip

# --- Gunicorn/WSGI Server Fix ---
server = app.server
