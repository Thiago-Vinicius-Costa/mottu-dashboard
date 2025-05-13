
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


# Dados de churn
df = pd.read_excel("Base_Completa_Churn_Mottu.xlsx")
df.columns = [col.strip().replace(" ", "_").lower() for col in df.columns]
df['motivo_do_churn'] = df['motivo_do_churn'].str.strip()
df['mês_do_churn'] = df['mês_do_churn'].str.strip()

# Dados de supply chain
supply = pd.read_excel("Insumos_Supply_Chain_Mottu.xlsx")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard Unificado Mottu"

app.layout = html.Div([
    html.H2("Dashboard Interativo - Mottu", style={"textAlign": "center"}),
#editei daqui 
dcc.Tabs([
    dcc.Tab(label='Parte 1 - Supply Chain', children=[
        dcc.Graph(
            figure=go.Figure([
                go.Bar(
                    x=supply["Filial"],
                    y=supply["Custo por Viagem (mil R$)"],
                    name="Custo por Viagem (mil R$)",
                    marker_color="indianred",
                    yaxis="y1"
                ),
                go.Scatter(
                    x=supply["Filial"],
                    y=supply["Tempo Médio Atual (dias)"],
                    name="Tempo Médio Atual (dias)",
                    mode="lines+markers",
                    marker=dict(color="blue"),
                    line=dict(color="blue"),
                    yaxis="y2"
                )
            ]).update_layout(
                title="Custo por Viagem vs Tempo Médio de Entrega por Filial",
                xaxis=dict(title="Filial"),
                yaxis=dict(
                    title="Custo por Viagem (mil R$)",
                    titlefont=dict(color="indianred"),
                    tickfont=dict(color="indianred")
                ),
                yaxis2=dict(
                    title="Tempo Médio Atual (dias)",
                    titlefont=dict(color="blue"),
                    tickfont=dict(color="blue"),
                    overlaying="y",
                    side="right"
                ),
                legend=dict(x=0.5, y=1.15, orientation="h", xanchor="center"),
                margin=dict(l=60, r=60, t=80, b=60),
                template="plotly_white"
            )
        )
    ]),
#ate aqui
        dcc.Tab(label='Parte 2 - Churn', children=[
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Label("Faixa de Idade:"),
                        dcc.RangeSlider(
                            id='idade-slider',
                            min=int(df['idade'].min()),
                            max=int(df['idade'].max()),
                            step=1,
                            marks={i: str(i) for i in range(int(df['idade'].min()), int(df['idade'].max())+1, 5)},
                            value=[int(df['idade'].min()), int(df['idade'].max())]
                        )
                    ], width=6),
                    dbc.Col([
                        html.Label("Região:"),
                        dcc.Dropdown(
                            id='regiao-dropdown',
                            options=[{"label": r, "value": r} for r in sorted(df['região'].unique())],
                            value=list(df['região'].unique()),
                            multi=True
                        )
                    ], width=6),
                ]),

                dbc.Row([
                    dbc.Col([
                        html.Label("Motivo do Churn:"),
                        dcc.Dropdown(
                            id='motivo-dropdown',
                            options=[{"label": m, "value": m} for m in sorted(df['motivo_do_churn'].unique())],
                            value=list(df['motivo_do_churn'].unique()),
                            multi=True
                        )
                    ], width=6),
                    dbc.Col([
                        html.Label("Mês do Churn:"),
                        dcc.Dropdown(
                            id='mes-dropdown',
                            options=[{"label": m, "value": m} for m in df['mês_do_churn'].unique()],
                            value=list(df['mês_do_churn'].unique()),
                            multi=True
                        )
                    ], width=6),
                ]),

                html.Br(),

                dbc.Row([
                    dbc.Col(dcc.Graph(id='grafico-motivos'), width=6),
                    dbc.Col(dcc.Graph(id='grafico-regiao'), width=6)
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='grafico-idade'), width=6),
                    dbc.Col(dcc.Graph(id='grafico-sazonalidade'), width=6)
                ])
            ], style={"padding": "20px"})
        ])
    ])
])

@app.callback(
    [Output('grafico-motivos', 'figure'),
     Output('grafico-regiao', 'figure'),
     Output('grafico-idade', 'figure'),
     Output('grafico-sazonalidade', 'figure')],
    [Input('idade-slider', 'value'),
     Input('regiao-dropdown', 'value'),
     Input('motivo-dropdown', 'value'),
     Input('mes-dropdown', 'value')]
)
def atualizar_graficos(idade_range, regioes, motivos, meses):
    filtro = df[
        (df['idade'] >= idade_range[0]) &
        (df['idade'] <= idade_range[1])
    ]
    if regioes:
        filtro = filtro[filtro['região'].isin(regioes)]
    if motivos:
        filtro = filtro[filtro['motivo_do_churn'].isin(motivos)]
    if meses:
        filtro = filtro[filtro['mês_do_churn'].isin(meses)]

    fig1 = px.histogram(filtro, y="motivo_do_churn", title="Motivos do Churn", color_discrete_sequence=["indianred"])
    fig2 = px.histogram(filtro, x="região", title="Distribuição por Região", color_discrete_sequence=["teal"])
    fig3 = px.histogram(filtro, x="idade", title="Distribuição de Idade", nbins=20, color_discrete_sequence=["orange"])
    fig4 = px.histogram(filtro, x="mês_do_churn", title="Churn por Mês", color_discrete_sequence=["steelblue"])

    return fig1, fig2, fig3, fig4

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
