import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
import socket


import json



df_states=pd.read_csv("df_states.csv")
df_brasil=pd.read_csv("df_brasil.csv")


brazil_states=json.load(
    open("Dashboard COVID-19/geojson/brazil_geo.json","r")
)



df_states_=df_states[df_states["data"]=="2020-02-25"]
df_data=df_states[df_states["estado"]=="RJ"]
select_columns={
    "casosAcumulado":"Casos Acumulados",
    "casosNovos":"Novos Casos",
    "obitosAcumulado":"Óbitos Totais",
    "obitosNovos":"óbitos por dia"
}



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
CENTER_LAT, CENTER_LON = -14.272572684355336, -51.25567404158474

# Defina as colunas que podem ser selecionadas no dropdown
select_columns = {
    "casosNovos": "Novos Casos",
    "casosAcumulado": "Casos Acumulados",
    "obitosNovos": "Novos Óbitos",
    "obitosAcumulado": "Óbitos Acumulados",
    "Recuperadosnovos": "Recuperados",
    "emAcompanhamentoNovos": "Em Acompanhamento"
}

# FIG 1 (Mapa Coroplético)
fig = px.choropleth_mapbox(
    df_states,  # Usando df_states (sem o underscore)
    geojson=brazil_states,
    locations="estado",
    color="casosNovos",
    center={"lat": -3.7400803, "lon": -38.4781625},
    zoom=4,
    mapbox_style="carto-darkmatter",
    color_continuous_scale="Redor",
    opacity=0.4,
    hover_data={
        "casosAcumulado": True,
        "casosNovos": True,
        "obitosNovos": True,
        "estado": True
    }
)

fig.update_layout(
    paper_bgcolor="#242424",
    autosize=True,
    margin=go.layout.Margin(l=0, r=0, t=0, b=0),
    showlegend=False
)


# FIG 2 (Gráfico de Linha/Barra)
fig2 = go.Figure(layout={"template": "plotly_dark"})
if 'data' in df_brasil.columns and 'casosAcumulado' in df_brasil.columns:
    fig2.add_trace(go.Scatter(x=df_brasil["data"], y=df_brasil["casosAcumulado"]))
fig2.update_layout(
    paper_bgcolor="#242424",
    plot_bgcolor="#242424",
    autosize=True,
    margin=dict(l=10, r=10, t=10, b=10),
    showlegend=False
)
# Layout
app.layout = dbc.Container(
    dbc.Row([
        dbc.Col([  # Col for left content
            html.Div([
                html.Img(id="logo", src=app.get_asset_url("logo_dark.png"), height=50),
                html.H5("Evolução Covid - 19"),
                dbc.Button("BRASIL", color="primary", id="location-button", size="lg")
            ]),
            html.P("Informe a data na qual deseja obter informações:", style={"margin-top": "40px"}),
            dbc.Col([  # Col for date picker
                html.Div(id="div-test", children=[
                    dcc.DatePickerSingle(
                        id="date-picker",
                        min_date_allowed=df_brasil["data"].min(),
                        max_date_allowed=df_brasil["data"].max(),
                        date=df_brasil["data"].max(),
                        display_format="DD/MM/YYYY",
                        style={"border": "0px solid black"}
                    )
                ], style={"padding": "25px", "background-color": "#242424"})
            ], md=5),
            dbc.Row([
                dbc.Col([  # Col for recovered cases card
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("Casos Recuperados"),
                            html.H3(style={"color": "#adfc92"}, id="casos-recuperados-text"),
                            html.Span("Em acompanhamento"),
                            html.H3(id="em-acompanhamento-text"),
                        ])
                    ], color="light", outline=True, style={
                        "margin-top": "10px",
                        "box-shadow": "0 4px 4px 0 rgba(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.19)",
                        "color": "#FFFFFF"
                    })
                ], md=4),
                dbc.Col([  # Col for confirmed cases card
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("Casos Confirmados Totais"),
                            html.H3(style={"color": "#389fd6"}, id="casos-confirmados-text"),
                            html.Span("Novos casos na data"),
                            html.H3(id="novos-casos-text"),
                        ])
                    ], color="light", outline=True, style={
                        "margin-top": "10px",
                        "box-shadow": "0 4px 4px 0 rgba(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.19)",
                        "color": "#FFFFFF"
                    })
                ], md=4),
                dbc.Col([  # Col for deaths card
                    dbc.Card([
                        dbc.CardBody([
                            html.Span("Óbitos confirmados"),
                            html.H3(style={"color": "#DF2935"}, id="obitos-text"),
                            html.Span("Óbitos na data"),
                            html.H3(id="obitos-na-data-text"),
                        ])
                    ], color="light", outline=True, style={
                        "margin-top": "10px",
                        "box-shadow": "0 4px 4px 0 rgba(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.19)",
                        "color": "#FFFFFF"
                    })
                ], md=4)
            ]),
            html.Div([
                html.P("Selecione o tipo de dado que deseja visualizar", style={"margin-top": "25px"}),
                dcc.Dropdown(
                    id="location-dropdown",
                    options=[{"label": j, "value": i} for i, j in select_columns.items()],
                    value="casosNovos",
                    style={"margin-top": "10px"}
                ),
                dcc.Graph(id="line-graph", figure=fig2)
            ]),

        ], md=5),  # Esta coluna ocupa 5 partes da largura total
        dbc.Col([
            dcc.Loading(id="loading-1", type="default",
                        children=[dcc.Graph(id="choropleth-map", figure=fig, style={"height": "130vh", "margin-right": "10px"})])  # Col for choropleth map
            ,
        ], md=7)  # Esta coluna ocupa 7 partes da largura total
    ], className="gx-0"),  # Remoção do no_gutters e uso da classe gx-0 para remover espaços
    fluid=True
)

# Print do IP
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
print(f"🌐 http://127.0.0.1:8050\n")
#==========================INTERATIVIDADE========================#
@app.callback(
    [
        Output("casos-recuperados-text", "children"),
        Output("em-acompanhamento-text", "children"),
        Output("casos-confirmados-text", "children"),
        Output("novos-casos-text", "children"),
        Output("obitos-text", "children"),
        Output("obitos-na-data-text", "children"),
    ],
    [Input("date-picker", "date"), Input("location-button", "children")]
)
def display_status(date, location):
    if location == "BRASIL":
        df_data_on_date = df_brasil[df_brasil["data"] == date]
    else:
        df_data_on_date = df_states[(df_states["estado"] == location) & (df_states["data"] == date)]

    recuperados_novos = "-" if df_data_on_date.empty or pd.isna(df_data_on_date["Recuperadosnovos"].values[0]) else f"{int(df_data_on_date['Recuperadosnovos'].values[0]):,}".replace(",", ".")
    acompanhamentos_novos = "-" if df_data_on_date.empty or pd.isna(df_data_on_date["emAcompanhamentoNovos"].values[0]) else f"{int(df_data_on_date['emAcompanhamentoNovos'].values[0]):,}".replace(",", ".")
    casos_acumulados = "-" if df_data_on_date.empty or pd.isna(df_data_on_date["casosAcumulado"].values[0]) else f"{int(df_data_on_date['casosAcumulado'].values[0]):,}".replace(",", ".")
    casos_novos = "-" if df_data_on_date.empty or pd.isna(df_data_on_date["casosNovos"].values[0]) else f"{int(df_data_on_date['casosNovos'].values[0]):,}".replace(",", ".")
    obitos_acumulado = "-" if df_data_on_date.empty or pd.isna(df_data_on_date["obitosAcumulado"].values[0]) else f"{int(df_data_on_date['obitosAcumulado'].values[0]):,}".replace(",", ".")
    obitos_novos = "-" if df_data_on_date.empty or pd.isna(df_data_on_date["obitosNovos"].values[0]) else f"{int(df_data_on_date['obitosNovos'].values[0]):,}".replace(",", ".")

    return (
        recuperados_novos,
        acompanhamentos_novos,
        casos_acumulados,
        casos_novos,
        obitos_acumulado,
        obitos_novos
    )



@app.callback(Output("line-graph", "figure"),
              [
                  Input("location-dropdown", "value"),
                  Input("location-button", "children"),
              ])
def plot_line_graph(plot_type, location):
    if location == "BRASIL":
        df_data_on_location = df_brasil.copy()
    else:
        df_data_on_location = df_states[df_states["estado"] == location]

    fig2 = go.Figure(layout={"template": "plotly_dark"})

    if not df_data_on_location.empty and "data" in df_data_on_location.columns and plot_type in df_data_on_location.columns:
        if plot_type in ["casosNovos", "obitosNovos"]:
            fig2.add_trace(go.Bar(x=df_data_on_location["data"], y=df_data_on_location[plot_type], name=select_columns[plot_type]))
        else:
            fig2.add_trace(go.Scatter(x=df_data_on_location["data"], y=df_data_on_location[plot_type], name=select_columns[plot_type]))

    fig2.update_layout(
        paper_bgcolor="#242424",
        plot_bgcolor="#242424",
        autosize=True,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False
    )
    return fig2


@app.callback(
    Output("choropleth-map", "figure"),
    [Input("date-picker", "date")]
)
def update_map(date):
    df_data_on_states = df_states[df_states["data"] == date]

    fig = px.choropleth_mapbox(
        df_data_on_states,
        geojson=brazil_states,
        locations="estado",  # Usando a coluna 'estado' (abreviações)
        color="casosAcumulado",
        center={"lat": CENTER_LAT, "lon": CENTER_LON},
        zoom=4,
        mapbox_style="carto-darkmatter",
        color_continuous_scale="Redor",
        opacity=0.55,
        hover_data={
            "casosAcumulado": True,
            "casosNovos": True,
            "obitosNovos": True,
            "nomeRegiaoSaude": True,  # Exibindo o nome da região de saúde no hover
            "estado": True             # Exibindo a abreviação do estado no hover
        }
    )
    fig.update_layout(
        paper_bgcolor="#242424",
        autosize=True,
        margin=go.layout.Margin(l=0, r=0, t=0, b=0),
        showlegend=False
    )
    return fig

@app.callback(
    Output("location-button", "children"),
    [Input("choropleth-map", "clickData"),
     Input("location-button", "n_clicks")]
)
def update_location(click_data, n_clicks):
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]

    if click_data is not None and changed_id != "location-button.n_clicks":
        state = click_data["points"][0]["location"]
        return "{}".format(state)
    else:
        return "BRASIL"

# Roda o servidor
if __name__ == "__main__":
    app.run(debug=True)

#==========================INTERATIVIDADE========================#