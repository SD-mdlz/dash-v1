import datetime
import json
from dash import Dash, dcc, html, Input, Output, State, dash_table, ctx, get_asset_url
import dash_bootstrap_components as dbc
import pandas as pd
from sql import upload_data, download_data
from calculate_v3 import calculate
import plotly.express as px
import pyodbc 

pd.options.mode.chained_assignment

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def get_graph(df):
    # print(df)
    df_fig = df[df['Key Figure']=="CLOSING STOCK"]
    df_fig = df_fig[['Country']+['Week '+str(i+1) for i in range(13)]]
    df_fig = df_fig.groupby(['Country'], as_index=False).sum()
    # print(df_fig)
    df_fig = pd.melt(df_fig, id_vars = 'Country', 
                 value_vars = ['Week '+ str(i+1) for i in range(13)], 
                 var_name = 'Week',                 
                 value_name = 'Closing Stock')
    df_fig = df_fig.groupby(['Country'], as_index=False).sum()
    fig = px.bar(df_fig, x='Country', y='Closing Stock', color='Country', title='Closing Stock by Country')
    fig.update_layout(
        title={'x':0.5},
        xaxis={'title': ''})
    return fig

def get_graph_difc(df, country):
    df_fig = df[df['Key Figure']=="DIFC"]
    df_fig = df_fig[['Country']+['Week '+str(i+1) for i in range(13)]]
    df_fig = pd.DataFrame(df_fig.mean(),columns=['DIFC'])
    df_fig['Week'] = df_fig.index
    df_fig.reset_index(inplace=True, drop=True)
    fig = px.line(df_fig, x='Week', y='DIFC')
    fig.update_layout(
        title={
            'text':'DIFC - ' + country if country else 'Weekly DIFC',
            'x':0.5},
        xaxis={'title': ''})
    return fig

# global df
df = calculate(download_data('Baseline'))
# df = calculate(pd.read_csv('Data/data.csv'))

app.layout = dbc.Container(
    [
        dcc.Store(id='data'),
        dbc.Alert(
            id="alert-calculate",
            is_open=False,
            fade=True,
            duration=2500,
            style={"position": "fixed", "top": 20, "right": 10, "width": 350, "zIndex": 1},
        ),
        dbc.Alert(
            id="alert-upload",
            is_open=False,
            fade=True,
            duration=2500,
            style={"position": "fixed", "top": 20, "right": 10, "width": 350, "zIndex": 1},
        ),
        dbc.Row([
            dbc.Col(html.Img(src=get_asset_url('MDLZ Logo.png'), alt='image', height=50), width=1),
            dbc.Col(html.Div('master production schedule application', className='app-header'), width=10),
            dbc.Col(html.Img(src=get_asset_url('CAT Logo.png'), alt='image', height=50), width=1)
        ],
        justify='between',
        class_name='title-bar'
        ),
        dbc.Row([
            dcc.Graph(
                id='graph-country-bar',
                figure=get_graph(df),
                style={'display': 'inline-block', 'width': '50%'}
            ),
            dcc.Graph(
                id='graph-difc-line',
                figure=get_graph_difc(df, None),
                style={'display': 'inline-block', 'width': '50%'}
            ),
        ]),
        dbc.Spinner(
                dash_table.DataTable(
                    id="data-table",
                    columns=[{"name": i, "id": i, "editable": True} if i.startswith('Week') else {"name": i, "id": i, "editable": False} for i in df.columns],
                    data=df.to_dict("records"),
                    editable=True,
                    page_size=12,
                    style_table={
                        # 'height': '600px',
                        'overflowY': 'auto',
                        # 'overflowX': 'auto'
                    },
                    style_data_conditional=[
                        {
                            'if':{
                                'column_id':'Week '+str(i+1),
                                'filter_query': "{Key Figure} = 'PRODUCTION'"
                            },
                            'backgroundColor': '#FFFFCC',
                        } for i in range(13)
                    ]
                    # + [
                    #     {
                    #         'if':{
                    #             'column_id':'Week '+str(i+1),
                    #             'filter_query': "{Key Figure} = 'DIFC' && {Week " + str(i+1) + "} <= 35"
                    #         },
                    #         'backgroundColor': '#FFCDCD',
                    #     } for i in range(13)
                    # ]
                ),
                color='primary'
        ),
        html.Br(),
        dbc.Row([
            dbc.Col(
                dbc.Button(
                    "Calculate", 
                    id="calculate", 
                    color="primary",
                    outline=True
                ),
            ),
            dbc.Col(
                    dbc.Select(['Scenario-' + str(i+1) for i in range(5)], 
                    # placeholder='Select Scenario',
                    id='upload-scenario-dropdown'
                )
            ),
            dbc.Col(
                dbc.Spinner(
                    dbc.Button(
                        "Upload as Scenario", 
                        id="upload-scenario",
                        color="primary",
                        outline=True
                    ),
                    color='primary'
                )
            ),
            dbc.Col(
                dbc.Button(
                    "Upload as Baseline", 
                    id="upload-baseline",
                    color="primary",
                    outline=True
                )
            )
        ],
        class_name='bottom-bar'
        ),
    ],
    fluid=True
)

@app.callback(
    Output('graph-difc-line', 'figure'),
    # Output("data-table","data"),
    Input('graph-country-bar', 'clickData'),
    State("data-table","data"),
    prevent_initial_call=True,
    )
def display_click_data(clickData, data):
    print(clickData)
    df = pd.DataFrame(data)
    if clickData:
        country = json.dumps(clickData["points"][0]["x"])
        country = country.replace('"','')
        if country:
            df = df[df['Country']==country]
        fig = get_graph_difc(df, country)
        return fig

@app.callback(
    Output("graph-country-bar","figure"),
    Output("data-table","data"),
    Output("alert-calculate", "children"),
    Output("alert-calculate", "is_open"),
    Input("calculate", "n_clicks"),
    State("data-table","data"),
    prevent_initial_call=True,
)
def calculateTable(_, data):
    start_time = datetime.datetime.now()
    df_new = pd.DataFrame(data)
    trigger = ctx.triggered_id
    # print(trigger)
    df_new = calculate(df_new)
    end_time = datetime.datetime.now()
    time_required = str(round((end_time-start_time).total_seconds(), 2))
    alert_message = 'Calculation complete! Time required: ' + time_required +'s'

    fig = get_graph(df_new)

    return fig, df_new.to_dict("records"), alert_message, True

@app.callback(
    Output("alert-upload", "children"),
    Output("alert-upload", "is_open"),
    Output("upload-scenario", "n_clicks"),
    Output("upload-baseline", "n_clicks"),
    Input("upload-scenario", "n_clicks"),
    Input("upload-baseline", "n_clicks"),
    State("upload-scenario-dropdown","value"),
    State("data-table","data"),
    prevent_initial_call=True,
)
def uploadBaseline(_, __, scenario, data):

    start_time = datetime.datetime.now()

    df_new = pd.DataFrame(data)
    button_clicked = ctx.triggered_id

    if button_clicked == 'upload-baseline':
        upload_data(df_new, 'Baseline')
    else:
        upload_data(df_new, scenario)

    end_time = datetime.datetime.now()
    time_required = str(round((end_time-start_time).total_seconds(),2))
    alert_message = 'Upload successful! Time required: ' + time_required +'s'
    return alert_message, True,'',''

if __name__ == "__main__":
    app.run(debug=False)