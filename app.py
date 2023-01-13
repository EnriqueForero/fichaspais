import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import dash_table
# Flask
import flask
from flask import redirect
from flask import render_template
from flask import send_from_directory
import urllib.parse

# Leer y manejar dataframes
import pandas as pd
import numpy as np

# Conectarse a Firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Utils
from my_utils import *

# Use a service account
cred = credentials.Certificate('fichas-pais-key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


# Actual, past and next year

info = db.collection(u'Info').document('data').get().to_dict()
year = info['Current Year']
past_year = info['Past year']
next_year = info['Next year']
year_5 = str(int(year)-4)

# Cargar Lista de paises y de URls

paises = dataFrameFromData(
    db.collection(u'Homologacion').document('data').get().to_dict()
).sort_index()

# Cargar Diccionario
data_dic = db.collection(u'Diccionario').document('data').get().to_dict()

diccionario = pd.DataFrame.from_dict(
    data_dic).reset_index().rename(columns={'index': 'Indicador'})

# Secciones
no_data_layout = html.Div([
    html.Span("No hay datos disponibles para este país.")
])


seccion_turismo = {
    # Header Turismo
    'header': html.Div(html.H4('Turismo'),
                       className="seccion-header",
                       style={'background-color': 'rgb(255, 215, 0)'}),
    # TEC
    'tec-graph': dcc.Loading(
        id="loading-tec",
        type="dot",
        children=html.Div(id="tec", className='seccion'),
    ),
    # Por Departamento
    'dpto-graph': dcc.Loading(
        id="loading-tec-dept",
        type="dot",
        children=html.Div(id="tecdpto", className='seccion'),
    ),
}


seccion_inversion = {
    # Header Inversión
    'header': html.Div(html.H4('Inversión'),
                       className="seccion-header",
                       style={'background-color': 'rgb(0, 128, 128)'}),
    'ide-graph': dcc.Loading(
        id="loading-ied",
        type="dot",
        children=html.Div(id="ied", className='seccion'),
    ),
    'ide-widgets': dcc.Loading(
        id="loading-ied-widgets",
        type="dot",
        children=html.Div(id="ied-widgets", className='widgets'),
    ),
    'ied-table': dcc.Loading(
        id="loading-ied-table",
        type="dot",
        children=html.Div(id="ied-table", className='seccion'),
    ),
}

seccion_exportaciones = {
    # Header Expo
    'header': html.Div(html.H4('Exportaciones'),
                       className="seccion-header",
                       style={'background-color': 'rgb(204, 0, 0)'}),
    'bc-graph': dcc.Loading(
        id="loading-bc",
        type="dot",
        children=html.Div(id="bc-graph", className='seccion'),
    ),
    'bc-widgets': dcc.Loading(
        id="loading-ied-widgets",
        type="dot",
        children=html.Div(id="bc-widgets", className='widgets'),
    ),
    'bc-table': dcc.Loading(
        id="loading-ied-table",
        type="dot",
        children=html.Div(id="bc-table", className='seccion'),
    ),
}


seccion_negocios = {
    'header': html.Div(html.H4('Negocios'),
                       className="seccion-header",
                       style={'background-color': '#111111'}),
    'doing-bus':  html.Div(id="doing-bus", className='seccion')

}

seccion_riesgo = {
    'header': html.Div(html.H4('Riesgo'),
                       className="seccion-header",
                       style={'background-color': '#111111'}),
    'risk':  dcc.Loading(
        id="loading-risk-data",
        type="dot",
        children=html.Div(id="risk", className='seccion'),
    )
}

seccion_indicadores = {
    'header': html.Div(html.H4('Indicadores sociales y económicos'), className="seccion-header", style={'background-color': '#111111'}),
    'accordion': html.Div(id="indicadores", className='seccion')
}


# App
app = dash.Dash(__name__,
                assets_folder="assets",
                assets_url_path='assets',
                url_base_pathname=f"/",
                suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Fichas'
server = app.server

# Layouts

# Header
header = html.Div([
    html.H1("Ficha País",
            id="header-title"),

    dcc.Link(
        html.Img(src=app.get_asset_url(
            'images/logo-procol.png'), className="images", style={
            'max-height': '6vh'
        }),
        href='/',
        refresh=True
    )



], className='header')
# Footer
footer = html.Div([
    html.H2(
        dcc.Link(
            dbc.Button(
                f"Diccionario de Datos",
                color="link",
                id=f"button-diccionario",

            ), href='/diccionario/', refresh=True,
        )
    ),

    dcc.Link(
        html.Img(src=app.get_asset_url(
            'images/logo-min.png'), style={
            'max-height': '6vh'
        }),
        href='/',
        refresh=True
    )

], className='footer')

# Layout Diccionario

layout_diccionario = html.Div([
    html.H1('Diccionario de Datos', style={
        'margin-bottom': '20px',
        'color': 'deepskyblue'
    }),
    dbc.Table.from_dataframe(
        diccionario, striped=True, bordered=True, hover=True, responsive=True),
    footer,
], style={'padding-top': '50px'})


# Layout Principal


def makeLayout(pathname):
    path = pathname.replace("/", "")
    pais = paises.loc[path, 'Valor']

    layout_correct = html.Div([
        header,
        seccion_indicadores['header'],
        seccion_indicadores['accordion'],
        seccion_exportaciones['header'],
        seccion_exportaciones['bc-widgets'],
        seccion_exportaciones['bc-graph'],
        seccion_exportaciones['bc-table'],
        seccion_inversion['header'],
        seccion_inversion['ide-widgets'],
        seccion_inversion['ide-graph'],
        seccion_inversion['ied-table'],
        seccion_turismo['header'],
        seccion_turismo['tec-graph'],
        seccion_turismo['dpto-graph'],
        seccion_riesgo['header'],
        seccion_riesgo['risk'],
        seccion_negocios['header'],
        seccion_negocios['doing-bus'],
        footer
    ])
    return layout_correct


# Layout de error
layout_error = html.Div([
    html.H1("Error 404 página no encontrada!")
], style={'display': 'grid', 'align-items': 'center', 'height': '100vh'})

# Layout inicio

layout_home = html.Div([
    html.H1("Escoja una ficha país"),
    dcc.Dropdown(
        id='home-dropdown',
        style={'padding': '10px', 'text-align': 'center'},
        options=[
            {'label': paises.loc[idx, 'Valor'], 'value':idx} for idx in list(paises.index)
        ],
        placeholder='Escoja un país',
    ),
    html.Span("Procolombia 2022."),
    footer,
], style={'display': 'grid', 'align-items': 'center', 'height': '100vh'})


# HTML
app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
], className='app', id="app")


# Callbacks

# Callback for url
@ app.callback(Output('page-content', 'children'),
               [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == "/":
        return layout_home
    elif pathname.replace("/", "") in list(paises.index):
        return makeLayout(pathname)
    elif pathname == '/diccionario/':
        return layout_diccionario
    else:
        return layout_error


# Callback for title
@app.callback(Output('header-title', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    path = pathname.replace("/", "")
    path = paises.loc[path, 'Valor']
    return f"Ficha País {path}"


# Callbacks Turismo
# Callback TEC

@ app.callback(
    Output(component_id='tec', component_property='children'),
    [Input('url', 'pathname')]
)
def update_output_div(pathname):
    path = pathname.replace("/", "")
    path = paises.loc[path, 'Valor']

    try:
        doc_ref = db.collection(u'Paises').document(
            path).collection('Turismo').document('data')
        data = doc_ref.get().to_dict()
        trace = go.Bar(
            x=list(data.keys()),
            y=list(data.values()),
            text=list(
                map(colFormat, list(data.values()))
            ),
            textfont={'size': 14,
                      'family': 'sans-serif', 'color': '#111111'},
            hoverinfo='skip',
            textposition="outside",
            marker=dict(color="#39CCCC"),
            cliponaxis=False)

        return html.Div([
            dcc.Graph(id="graph-tec", figure={'data': [trace],
                                              'layout': dict(yaxis=dict(showgrid=False, fixedrange=True),
                                                             autosize=True,
                                                             font=dict(
                                                  family="sans-serif", size=14),
                title=dict(text="<b> Llegadas de extranjeros residentes en<br>{}</b>".format(path),
                                                  font=dict(size=18, family='sans-serif')),
                xaxis=dict(showgrid=False, fixedrange=True))})

        ])
    except AttributeError:
        return no_data_layout

# Callback TEC x DEPARTAMENTO


@ app.callback(
    Output(component_id='tecdpto', component_property='children'),
    [Input('url', 'pathname')]
)
def update_tec_depto(pathname):
    path = pathname.replace("/", "")
    path = paises.loc[path, 'Valor']
    try:
        doc_ref = db.collection(u'Paises').document(
            path).collection('TurismoDpto').document('data')
        data = doc_ref.get().to_dict()
        df = dataFrameFromData(data).nlargest(
            5, 'Valor')

        # Trazo
        trace = go.Bar(
            y=br(list(df.index)),
            x=list(df['Valor']),
            hoverinfo='skip',
            orientation='h',
            text=list(
                map(colFormat, list(df['Valor']))
            ),
            textposition="auto",
            cliponaxis=False,
            textfont={'size': 14, 'family': 'sans-serif', 'color': '#fff'},
            marker=dict(color='#001f3f', line=dict(color='#001f3f', width=3)))
        return dcc.Graph(id="graph-tec-dpto", figure={
            'data': [trace],
            'layout': {'autosize': True,
                       'font': dict(family="sans-serif", size=12),
                       'xaxis': dict(showgrid=False, fixedrange=True),
                       'yaxis': dict(autorange="reversed", ticklen=20, showgrid=False, fixedrange=True),
                       'title': {'text': '<b> Principales departamentos de <br> destino en {} </b>'.format(year), 'font': {'size': 18, 'family': 'sans-serif'}}}
        })
    except AttributeError:
        return no_data_layout


# Callback IDE graph and table

@ app.callback(
    Output(component_id='ied', component_property='children'),
    [Input('url', 'pathname')]
)
def update_ied(pathname):
    path = pathname.replace("/", "")
    path = paises.loc[path, 'Valor']
    doc_ref = db.collection(u'Paises').document(
        path).collection('Inversion').document('IDE')
    data = doc_ref.get().to_dict()
    try:
        df = dataFrameFromData(data)
        rank = df.loc['Rank', 'Valor']
        df = df.drop('Rank')
        df = df.sort_index()
        trace = go.Scatter(
            x=list(df.index),
            y=list(df['Valor']),
            line_color='rgb(0,100,80)',
            mode='lines+markers',
            name='Flujos IED')
        graph = dcc.Graph(id="ide-graph", figure={'data': [trace],
                                                  'layout': {'yaxis': {'showdrid': False},
                                                             'font': dict(family="sans-serif", size=14),
                                                             'xaxis': {'showdrid': False, 'fixedrange': True},
                                                             'yaxis': {'showdrid': False, 'fixedrange': True},
                                                             'title': "<b> Flujos IED de {} en Colombia <br> (USD millones) </b>".format(path),
                                                             'font': {'size': 12, 'family': 'sans-serif'}}
                                                  })
        return graph
    except:
        no_data_layout

# Callback inversion widgets


@ app.callback(
    Output(component_id='ied-widgets', component_property='children'),
    [Input('url', 'pathname')]
)
def update_ied_widgets(pathname):
    path = pathname.replace("/", "")
    path = paises.loc[path, 'Valor']

    fdi_col = db.collection(u'Paises').document(path).collection(
        'Inversion').document('FDICOL').get().to_dict()
    fdi_mundo = db.collection(u'Paises').document(path).collection(
        'Inversion').document('FDIMundo').get().to_dict()
    try:
        return [
            html.Div(
                [
                    html.Strong(
                        f'Proyectos de Inversión de Colombia en {path} ({year_5}-{year})'),
                    html.Span(fdi_col["Proyectos"])

                ],
                className='widget-inv'),
            html.Div(
                [
                    html.Strong(
                        f'Proyectos de Inversión de {path} en Colombia ({year_5}-{year})'),
                    html.Span(fdi_mundo["Proyectos"])

                ],
                className='widget-inv'),

        ]
    except TypeError:
        return no_data_layout

# Callback ied table


@ app.callback(
    Output(component_id='ied-table', component_property='children'),
    [Input('url', 'pathname')]


)
def update_ied_table(pathname):
    path = pathname.replace("/", "")
    path = paises.loc[path, 'Valor']
    doc_ref = db.collection(u'Paises').document(
        path).collection('Inversion').document('IDE')
    dataIED = doc_ref.get().to_dict()
    doc_ref = db.collection(u'Paises').document(
        path).collection('Inversion').document('ICE')
    dataICE = doc_ref.get().to_dict()
    try:
        iedrank = dataIED['Rank']
        iedyear = colFormat(round(dataIED[year], 1))
        icerank = dataICE['Rank']
        iceyear = colFormat(round(dataICE[year], 1))

        df = pd.DataFrame({'Millones USD': [iedyear, iceyear],
                           'Ranking': [iedrank, icerank]},
                          index=[f'IED de {path} en Colombia ({year})', f'IED de Colombia en {path} ({year})'])
        df.index.name = '*'
        df = df.reset_index()
        table = dbc.Table.from_dataframe(
            df, striped=True, bordered=True, hover=True, responsive=True)

        return table
    except (AttributeError, TypeError)as e:
        return no_data_layout


# Callback widgets exportaciones
@ app.callback(
    Output(component_id='bc-widgets', component_property='children'),
    [Input('url', 'pathname')]
)
def update_ied_widgets(pathname):
    path = pathname.replace("/", "")
    path = paises.loc[path, 'Valor']
    data = db.collection(u'Paises').document(path).collection(
        'Trademap').document('data').get().to_dict()
    if data != None:
        rank_exp = data['Rank Exportador']
        rank_imp = data['Rank Importador']

        return [
            html.Div(
                [
                    html.Strong(
                        f'Ranking País Exportador ({year})'),
                    html.Span(int(rank_exp))

                ],
                className='widget'),
            html.Div(
                [
                    html.Strong(
                        f'Ranking País Importador ({year})'),
                    html.Span(int(rank_imp))

                ],
                className='widget'),

        ]
    else:
        return no_data_layout


# Callback bc table


@ app.callback(
    Output(component_id='bc-table', component_property='children'),
    [Input('url', 'pathname')]


)
def update_bc_table(pathname):
    path = pathname.replace("/", "")
    path = paises.loc[path, 'Valor']

    # Get data
    doc_ref = db.collection(u'Paises').document(
        path).collection('Balanza').document('data')
    data = doc_ref.get().to_dict()
    if data != None:
        df = pd.DataFrame(data).round(1)
        df = df.sort_values(by=f"Exportaciones {year}")
        df = df[[f'Exportaciones {year}',
                 f'Importaciones {year}', f'Balanza Comercial {year}']]
        for col in df.columns:

            df[col] = df[col].apply(colFormat)
        df.index.name = 'Cadena'
        df = df.reset_index()
        table = dbc.Table.from_dataframe(
            df, striped=True, bordered=True, hover=True, size='sm', responsive=True)
        return [html.Div(html.H4("Relación Comercial (USD FOB Millones)"), className="title-table"), table]
    else:
        return no_data_layout


# Callback BC graph

@ app.callback(
    Output(component_id='bc-graph', component_property='children'),
    [Input('url', 'pathname')]
)
def update_bc_graph(pathname):
    path = pathname.replace("/", "")
    path = paises.loc[path, 'Valor']
    data = db.collection(u'Paises').document(path).collection(
        'Trademap').document('data').get().to_dict()
    if data != None:
        trace1 = go.Bar(
            x=['Exportaciones', 'Importaciones', 'Balanza Comercial'],
            y=[data[f'Valor exportado en {year}'],
               data[f'Valor importado en {year}'],
               data[f'Balanza Comercial {year}']],
            text=[
                colFormat(round(data[f'Valor exportado en {year}'], 1)),
                colFormat(round(data[f'Valor importado en {year}'], 1)),
                colFormat(round(data[f'Balanza Comercial {year}'], 1)),
            ],
            textposition="outside",
            textfont={'size': 12, 'family': 'sans-serif'},
            name=year,
            hoverinfo='skip',
            cliponaxis=False)

        trace2 = go.Bar(
            x=['Exportaciones', 'Importaciones', 'Balanza Comercial'],
            y=[
                data[f'Valor exportado en {past_year}'],
                data[f'Valor importado en {past_year}'],
                data[f'Balanza Comercial {past_year}']
            ],
            text=[
                colFormat(round(data[f'Valor exportado en {past_year}'], 1)),
                colFormat(round(data[f'Valor importado en {past_year}'], 1)),
                colFormat(round(data[f'Balanza Comercial {past_year}'], 1)),
            ],
            name=past_year,
            textposition="outside",
            textfont={'size': 12, 'family': 'sans-serif'},
            hoverinfo='skip',
            cliponaxis=False)

        graph = dcc.Graph(id='bc-graph-bc', figure={'data': [trace1, trace2],
                                                    'layout': {
                                                        'legend': dict(
                                                            yanchor="top",
                                                            y=0.90,
                                                            xanchor="left",
                                                            x=0.80
                                                        ),
            'font': dict(family="sans-serif", size=14),
            'yaxis': dict(showgrid=False, fixedrange=True),
            'xaxis': dict(showgrid=False, fixedrange=True),
            'title': {"text": "<b> Relación Comercial {} - Mundo <br> (USD miles de millones) </b>".format(path), 'font': {'size': 16, 'family': 'sans-serif'}}
        }
        })
        return graph
    else:
        return no_data_layout


# Callback doing bussiness/Indice Competitividad Global

# Get data


@ app.callback(
    Output(component_id='doing-bus', component_property='children'),
    [Input('url', 'pathname')]
)
def getdoingbus_data(pathname):
    path = pathname.replace("/", "")
    path = paises.loc[path, 'Valor']
    try:
        # Doin Business
        data = db.collection(u'Paises').document(path).collection(
            'Negocios').document('DOINGBUS').get().to_dict()
        df = dataFrameFromData(data)
        df = df.sort_index()
        df.index = df.index.str.extract("(\D+)")[0]

        # Indice Competitividad global
        data = db.collection(u'Paises').document(path).collection(
            'Negocios').document('IDXCOMPGLO').get().to_dict()

        card = dbc.Card(
            [
                # INDICE COMP
                dbc.CardHeader(
                    html.H2(
                        dbc.Button(
                            f"Índice de Competitividad Global",
                            color="link",
                            id=f"collapse-button-indice",
                        )
                    )
                ),
                dbc.Collapse(
                    dbc.CardBody([
                        html.Div(
                            [html.Strong(key), html.Span(
                                data[key])],
                            className="list-data")
                        for key in list(data.keys())]),
                    id=f"collapse-indice",
                ),

                dbc.CardHeader(
                    html.H2(
                        dbc.Button(
                            f"Facilidad de hacer Negocios",
                            color="link",
                            id=f"collapse-button",
                        )
                    )
                ),
                # DOING BUSS
                dbc.Collapse(
                    dbc.CardBody([
                        html.Div(
                            [html.Strong(index), html.Span(
                                df.loc[index, 'Valor'])],
                            className="list-data")
                        for index in df.index]),
                    id=f"collapse",
                ),



            ]
        ),
        return card
    except AttributeError:
        return no_data_layout

# Collapse DOING BUSINESS


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# Collapse INDICEE COMPETITIVIDAD


@app.callback(
    Output("collapse-indice", "is_open"),
    [Input("collapse-button-indice", "n_clicks")],
    [State("collapse-indice", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# Callback riesgo


@ app.callback(
    Output(component_id='risk', component_property='children'),
    [Input('url', 'pathname')]
)
def update_risk(pathname):
    path = pathname.replace("/", "")
    path = paises.loc[path, 'Valor']
    # Risk
    data = db.collection(u'Paises').document(path).collection(
        'Risk').document('data').get().to_dict()
    if data != None:
        df = dataFrameFromData(data)
        df = df.sort_index()
        card = dbc.Card(
            dbc.CardBody([
                html.Div(
                    [html.Strong(index), html.Span(
                        df.loc[index, 'Valor'])],
                    className="list-data")
                for index in df.index]),
        )
        return card
    else:
        return no_data_layout


# callback get data indicadores

@ app.callback(
    Output(component_id='indicadores', component_property='children'),
    [Input('url', 'pathname')]
)
def get_data_indicadores(pathname):

    path = pathname.replace("/", "")
    path = paises.loc[path, 'Valor']
    # Get data from firebase
    data_pob = db.collection(u'Paises').document(path).collection(
        'Indicadores').document('Poblacion').get().to_dict()
    data_bienestar = db.collection(u'Paises').document(path).collection(
        'Indicadores').document('Bienestar').get().to_dict()
    data_empleo = db.collection(u'Paises').document(path).collection(
        'Indicadores').document('Empleo').get().to_dict()
    data_produccion = db.collection(u'Paises').document(path).collection(
        'Indicadores').document('Produccion').get().to_dict()
    accordion = html.Div(
        [make_item(1, data_pob), make_item(2, data_bienestar),
         make_item(3, data_produccion), make_item(4, data_empleo)], className="accordion"
    )
    return accordion


# Callback open accordion indicadores
@app.callback(
    [Output(f"collapse-{i}", "is_open") for i in range(1, 5)],
    [Input(f"group-{i}-toggle", "n_clicks") for i in range(1, 5)],
    [State(f"collapse-{i}", "is_open") for i in range(1, 5)],
)
def toggle_accordion(n1, n2, n3, n4, is_open1, is_open2, is_open3, is_open4):
    ctx = dash.callback_context

    if not ctx.triggered:
        return False, False, False, False
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "group-1-toggle" and n1:
        return not is_open1, False, False, False
    elif button_id == "group-2-toggle" and n2:
        return False, not is_open2, False, False
    elif button_id == "group-3-toggle" and n3:
        return False, False, not is_open3, False
    elif button_id == "group-4-toggle" and n4:
        return False, False, False, not is_open4,

    return False, False, False


# Callback homepage


@ app.callback(
    [Output('url', 'pathname'), Output('url', 'refresh')],
    [Input('home-dropdown', 'value')]
)
def update_page_home(value):
    return f'/{value}/', False

if __name__ == '__main__':
    app.run_server(debug=True)
