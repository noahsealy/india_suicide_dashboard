import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

# general dash tutorial --> https://www.youtube.com/watch?v=hSPmj7mK6ng

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# read data set
dff = pd.read_csv('year_data/2012.csv')

# dash components and html goes here
app.layout = html.Div([

    dbc.Row(
        children=[
            dbc.Col(
                html.Img(
                    src='https://cdn.dal.ca/content/dam/dalhousie/images/dept/communicationsandmarketing/01%20DAL%20FullMark-Blk.jpg.lt_412f83be03abff99eefef11c3f1ec3a4.res/01%20DAL%20FullMark-Blk.jpg',
                    width='240px'),
                className='col-2'
            ),
            dbc.Col(
                [
                    html.P(children='Welcome Data Bender!', className='display-4 text-center', style={'font-size': 38}),
                    html.P(children='Unleash your data bending powers.', className='lead text-center'),
                ],
                className='col-8'
            ),
            dbc.Col(
                [
                    html.P(children='Visual Analytics', className='lead text-center'),
                    html.Div(children='CSCI 6612', className='lead text-center'),
                ],
                className='col-2 pt-2'
            ),
        ]
    ),
    html.Hr(),

    dbc.Row(
        dbc.Col(
            children=[
                html.H1("Suicides in India Dashboard", style={'text-align': 'center'}),
            ]
        )
    ),
    html.Hr(),

    dbc.Row(
        children=[
            dbc.Col(
                children=[
                    html.H1('Data Map'),
                    dcc.Graph(id='suicide_map', figure={}),
                    html.Br(),

                    dcc.Slider(
                        id='select_year',
                        min=2001,
                        max=2012,
                        step=1,
                        value=2012,
                    ),
                    html.Div(id='output_container', children=[])
                ],
                className='col-6'
            ),
            dbc.Col(
                children=[
                    html.P(id='selected_print',
                           children={},
                    ),
                    dcc.Graph(id='feature_description', figure={})
                ],
                className='col-6'
            )
        ]
    ),

    dbc.Row(
        children=[
            dbc.Col(
                children=[
                    dcc.Graph(id='gender_bar', figure={})
                ],
                className='col-4'
            ),
            dbc.Col(
                children=[
                    dcc.Graph(id='professions_bar', figure={})
                ],
                className='col-4'
            ),
            dbc.Col(
                children=[
                    dcc.Graph(id='causes_bar', figure={})
                ],
                className='col-4'
            ),
        ]
    ),
    html.Hr(),

])


# connect Plotly graphs and Dash components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='suicide_map', component_property='figure')],
    [Input(component_id='select_year', component_property='value')]
)
def update_graph(slider_select):

    container = "The year chosen by user was: {}".format(slider_select)

    dff = pd.read_csv('year_data/' + str(slider_select) + '.csv')

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        # api for map of india
        # found here https://stackoverflow.com/questions/60910962/is-there-any-way-to-draw-india-map-in-plotly
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw"
                "/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='State',
        color='Total', #z
        #cluster
        hover_data=['State', 'Total', 'Causes_Bankruptcy or Sudden change in Economic Status',
                    'Causes_Cancellation/Non-Settlement of Marriage', 'Causes_Cancer', 'Causes_Causes Not known',
                    'Causes_Death of Dear Person', 'Causes_Divorce', 'Causes_Dowry Dispute'],
        #color_continuous_scale=px.colors.sequential.YlOrRd,
        color_continuous_scale='Reds',
        range_color=[0, 20000],
        labels={'Total': 'Total Suicides in India'},
        #template='plotly_dark',
    )

    fig.update_geos(fitbounds="locations", visible=False)

    return container, fig


# for selecting map data
@app.callback(
    [Output(component_id='selected_print', component_property='children'),
     Output(component_id='feature_description', component_property='figure'),
     Output(component_id='gender_bar', component_property='figure'),
     Output(component_id='professions_bar', component_property='figure'),
     Output(component_id='causes_bar', component_property='figure')],
    [Input(component_id='suicide_map', component_property='clickData'),
     Input(component_id='suicide_map', component_property='selectedData')]
)
def select_data(clicked, selected):
    try:
        if selected is None:
            selected = clicked

        locations_str = []
        locations = []
        for point in selected['points']:
            for attr, value in point.items():
                if attr == 'location':
                    locations_str.append(str(value) + ", ")
                    locations.append(str(value))

        # combine all select states into one df series
        # this is what the figures will use for data
        selected_states = dff[dff['State'].isin(locations)]

        # figure for correlation (IDENTIFY RISK GROUPS)
        correlations = []
        for col in selected_states.columns:
            if col != 'Total' or col != 'State' or col != 'Year' or col != 'Unnamed':
                correlations.append(selected_states['Total'].corr(selected_states[col]))
        print(correlations)

        feature_description = go.Figure()

        gender_bar = go.Figure()
        # bar chart for gender
        gender_bar.add_trace(go.Bar(y=['Gender'], x=[selected_states['Female'].sum()], name='Female', orientation='h',
                             marker=dict(color='pink')))
        gender_bar.add_trace(go.Bar(y=['Gender'], x=[selected_states['Male'].sum()], name='Male', orientation='h',
                             marker=dict(color='blue')))
        gender_bar.update_layout(title_text='Data by Gender')

        # get all professions
        professions = []
        for col in selected_states.columns:
            if 'Professional_Profile_' in col:
                professions.append(col)

        # slice the profession strings so they just say the professions
        professions_sliced = []
        for profession in professions:
            professions_sliced.append(profession[21:])

        # y values for professions
        profession_values = []
        for profession in professions:
            profession_values.append(selected_states[profession].sum())

        # chart for profession
        professions_bar = go.Figure()
        professions_bar.add_trace(go.Bar(x=professions_sliced, y=profession_values))
        professions_bar.update_layout(title_text='Data by Profession')

        # get all causes
        causes = []
        for column in selected_states.columns:
            if 'Causes_' in column:
                causes.append(column)

        # slice the causes strings so they just say the causes
        causes_sliced = []
        for cause in causes:
            causes_sliced.append(cause[7:])

        # y value for causes
        causes_values = []
        for cause in causes:
            causes_values.append(selected_states[cause].sum())

        # chart for causes
        causes_bar = go.Figure()
        causes_bar.add_trace(go.Bar(x=causes_sliced, y=causes_values))
        causes_bar.update_layout(title_text='Data by Cause')

        return locations_str, feature_description, gender_bar, professions_bar, causes_bar

    # init data
    except TypeError:
        temp = dff[dff['State'] == 'Maharashtra']

        feature_description = go.Figure()

        gender_bar = go.Figure()
        gender_bar.add_trace(go.Bar(y=['Gender'], x=temp['Female'], name='Female', orientation='h',
                             marker=dict(color='pink')))
        gender_bar.add_trace(go.Bar(y=['Gender'], x=temp['Male'], name='Male', orientation='h',
                             marker=dict(color='blue')))
        gender_bar.update_layout(title_text='Data by Gender')

        # get all professions
        professions = []
        for col in temp.columns:
            if 'Professional_Profile_' in col:
                professions.append(col)

        # slice the profession strings so they just say the professions
        professions_sliced = []
        for profession in professions:
            professions_sliced.append(profession[21:])

        # y values for professions
        profession_values = []
        for profession in professions:
            profession_values.append(temp[profession].sum())

        professions_bar = go.Figure()
        professions_bar.add_trace(go.Bar(x=professions_sliced, y=profession_values))
        professions_bar.update_layout(title_text='Data by Profession')


        # get all causes
        causes = []
        for column in temp.columns:
            if 'Causes_' in column:
                causes.append(column)

        # slice the causes strings so they just say the causes
        causes_sliced = []
        for cause in causes:
            causes_sliced.append(cause[7:])

        # y value for causes
        causes_values = []
        for cause in causes:
            causes_values.append(temp[cause].sum())

        causes_bar = go.Figure()
        causes_bar.add_trace(go.Bar(x=causes_sliced, y=causes_values))
        causes_bar.update_layout(title_text='Data by Cause')

        return ['Maharashtra'], feature_description, gender_bar, professions_bar, causes_bar


if __name__ == '__main__':
    app.run_server(debug=True)
