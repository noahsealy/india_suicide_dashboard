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
    # dbc.Row(
    #     dbc.Col(
    #         children=[
    #             html.H1("Suicides in India Dashboard", style={'text-align': 'center'}),
    #         ]
    #     )
    # ),
    # html.Hr(),
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
                    dcc.Dropdown(id='description_select', value=[], options=[],
                                 clearable=False, searchable=False
                                 ),
                    dcc.Graph(id='feature_description', figure={}),
                    html.P(id='risk_level', children={}),
                    html.P(children='Note: if a single state was selected, this data is based on that state from 2001 '
                                    'to 2012 data.')
                ],
                className='col-6'
            )
        ]
    ),
    html.Hr(),
    dbc.Row(
        children=[
            dbc.Col(
                children=[
                    dcc.Dropdown(id='data_by_select',
                                 value='profession',
                                 options=[{'label': 'Data by Profession', 'value': 'profession'},
                                          {'label': 'Data by Cause', 'value': 'cause'},
                                          {'label': 'Data by Gender', 'value': 'gender'}, ],
                                 className='col-3', clearable=False, searchable=False
                                 )
                ]
            )
        ]
    ),
    dbc.Row(
        children=[
            dcc.Graph(id='data_by_figure', figure={})
        ],
        justify='center',
        align='center'
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
        color='Total',  # z
        # cluster
        hover_data=['State', 'Total', 'Causes_Bankruptcy or Sudden change in Economic Status',
                    'Causes_Cancellation/Non-Settlement of Marriage', 'Causes_Cancer', 'Causes_Causes Not known',
                    'Causes_Death of Dear Person', 'Causes_Divorce', 'Causes_Dowry Dispute'],
        # color_continuous_scale=px.colors.sequential.YlOrRd,
        color_continuous_scale='Reds',
        range_color=[0, 20000],
        labels={'Total': 'Total Suicides in India'},
        # template='plotly_dark',
    )

    fig.update_geos(fitbounds="locations", visible=False)

    return container, fig


# for selecting map data
@app.callback(
    [Output(component_id='selected_print', component_property='children'),
     Output(component_id='description_select', component_property='value'),
     Output(component_id='description_select', component_property='options')],
    [Input(component_id='suicide_map', component_property='clickData'),
     Input(component_id='suicide_map', component_property='selectedData')]
)
def select_data(clicked, selected):
    try:
        if selected is None:
            selected = clicked

        locations_str = ['State(s) Selected: ']
        locations = []
        for point in selected['points']:
            for attr, value in point.items():
                if attr == 'location':
                    locations_str.append(str(value) + ", ")
                    locations.append(str(value))

        # combine all select states into one df series
        # this is what the figures will use for data
        selected_states = dff[dff['State'].isin(locations)]

        # find all column options and slice them for labels to look better
        feature_description_select = []
        for col in selected_states.columns:
            if 'Professional_Profile_' in col:
                label = col[21:]
                feature_description_select.append({'label': label, 'value': col})
            elif 'Education_Status_' in col:
                label = col[17:]
                feature_description_select.append({'label': label, 'value': col})
            elif 'Social_Status_' in col:
                label = col[14:]
                feature_description_select.append({'label': label, 'value': col})

        # set default value
        feature_description_value = feature_description_select[0]['value']

        return locations_str, feature_description_value, feature_description_select

    # init data
    except TypeError:
        temp = dff[dff['State'] == 'Maharashtra']

        # find all column options and slice them for labels to look better
        feature_description_select = []
        for col in temp.columns:
            if 'Professional_Profile_' in col:
                label = col[21:]
                feature_description_select.append({'label': label, 'value': col})
            elif 'Education_Status_' in col:
                label = col[17:]
                feature_description_select.append({'label': label, 'value': col})
            elif 'Social_Status_' in col:
                label = col[14:]
                feature_description_select.append({'label': label, 'value': col})

        # set default value
        feature_description_value = feature_description_select[0]['value']

        return ['States(s) Selected: Maharashtra'], feature_description_value, feature_description_select


@app.callback([Output(component_id='feature_description', component_property='figure'),
               Output(component_id='risk_level', component_property='children')],
              [Input(component_id='description_select', component_property='value'),
               Input(component_id='suicide_map', component_property='clickData'),
               Input(component_id='suicide_map', component_property='selectedData')])
def feature_matrix(feature, clicked, selected):
    try:
        if selected is None:
            selected = clicked

        locations = []
        for point in selected['points']:
            for attr, value in point.items():
                if attr == 'location':
                    locations.append(str(value))

        # combine all select states into one df series
        # this is what the figures will use for data
        if len(locations) == 1:
            selected_states = pd.DataFrame()
            for location in locations:
                df = pd.read_csv('state_data/' + str(location) + '.csv')
                selected_states = selected_states.append(df, ignore_index=True)
        else:
            locations = []
            for point in selected['points']:
                for attr, value in point.items():
                    if attr == 'location':
                        locations.append(str(value))

            selected_states = dff[dff['State'].isin(locations)]

        label = ''
        if 'Professional_Profile_' in feature:
            label = feature[21:]
        elif 'Education_Status_' in feature:
            label = feature[17:]
        elif 'Social_Status_' in feature:
            label = feature[14:]

        # find correlation matrix
        corr = selected_states[['Total', feature]].corr(method='pearson')
        # visualize correlation matrix
        corr_map = go.Figure()
        corr_map.add_trace(go.Heatmap(x=['Total', label], y=['Total', label], z=corr, colorscale='reds'))
        corr_map.update_layout(title_text='Correlation Heatmap')

        risk = corr.iloc[0, 1]

        if risk >= .80:
            risk_rating = 'This group is at high risk.'
        elif (risk < .80) and (risk >= 0.50):
            risk_rating = 'This group is at moderate risk.'
        else:
            risk_rating = 'This group is at a low risk.'
        return corr_map, risk_rating

    # init data
    except TypeError:
        selected_states = pd.read_csv('state_data/Maharashtra.csv')

        label = ''
        if 'Professional_Profile_' in feature:
            label = feature[21:]
        elif 'Education_Status_' in feature:
            label = feature[17:]
        elif 'Social_Status_' in feature:
            label = feature[14:]

        # find correlation matrix
        corr = selected_states[['Total', feature]].corr(method='pearson')
        # visualize correlation matrix
        corr_map = go.Figure()
        corr_map.add_trace(go.Heatmap(x=['Total', label], y=['Total', label], z=corr, colorscale='reds'))
        corr_map.update_layout(title_text='Correlation Heatmap')

        risk = corr.iloc[0, 1]

        if risk >= .80:
            risk_rating = 'This group is at high risk.'
        elif (risk < .80) and (risk >= 0.50):
            risk_rating = 'This group is at moderate risk.'
        else:
            risk_rating = 'This group is at a low risk.'
        return corr_map, risk_rating


@app.callback(Output(component_id='data_by_figure', component_property='figure'),
              [Input(component_id='data_by_select', component_property='value'),
               Input(component_id='suicide_map', component_property='clickData'),
               Input(component_id='suicide_map', component_property='selectedData')])
def data_by(figure_select, clicked, selected):
    try:
        if selected is None:
            selected = clicked

        locations_str = ['State(s) Selected: ']
        locations = []
        for point in selected['points']:
            for attr, value in point.items():
                if attr == 'location':
                    locations_str.append(str(value) + ", ")
                    locations.append(str(value))

        # combine all select states into one df series
        # this is what the figures will use for data
        selected_states = dff[dff['State'].isin(locations)]

        if figure_select == 'profession':
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
            professions_bar.add_trace(go.Bar(x=professions_sliced, y=profession_values,
                                      marker=dict(color=profession_values, colorscale='reds')))
            professions_bar.update_layout(title_text='Data by Profession', width=1200)

            return professions_bar

        elif figure_select == 'cause':
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
            causes_bar.add_trace(go.Bar(x=causes_sliced, y=causes_values,
                                        marker=dict(color=causes_values, colorscale='reds')))
            causes_bar.update_layout(title_text='Data by Cause', width=1200)

            return causes_bar

        else:  # gender
            gender_bar = go.Figure()
            gender_bar.add_trace(
                go.Bar(y=['Gender'], x=[selected_states['Female'].sum()], name='Female', orientation='h',
                       marker=dict(color=[selected_states['Female'].sum()], colorscale='reds')))
            gender_bar.add_trace(go.Bar(y=['Gender'], x=[selected_states['Male'].sum()], name='Male', orientation='h',
                                        marker=dict(color=[selected_states['Male'].sum()], colorscale='reds')))
            gender_bar.update_layout(title_text='Data by Gender', width=1200)

            return gender_bar

    # init figure
    except TypeError:
        temp = dff[dff['State'] == 'Maharashtra']

        if figure_select == 'profession':
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

            # chart for profession
            professions_bar = go.Figure()
            professions_bar.add_trace(go.Bar(x=professions_sliced, y=profession_values,
                                      marker=dict(color=profession_values, colorscale='reds')))
            professions_bar.update_layout(title_text='Data by Profession', width=1200)

            return professions_bar

        elif figure_select == 'cause':
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

            # chart for causes
            causes_bar = go.Figure()
            causes_bar.add_trace(go.Bar(x=causes_sliced, y=causes_values,
                                        marker=dict(color=causes_values, colorscale='reds')))
            causes_bar.update_layout(title_text='Data by Cause', width=1200)

            return causes_bar

        else:  # gender
            gender_bar = go.Figure()
            gender_bar.add_trace(
                go.Bar(y=['Gender'], x=[temp['Female'].sum()], name='Female', orientation='h',
                       marker=dict(color=[temp['Female'].sum()], colorscale='reds')))
            gender_bar.add_trace(go.Bar(y=['Gender'], x=[temp['Male'].sum()], name='Male', orientation='h',
                                        marker=dict(color=[temp['Male'].sum()], colorscale='reds')))
            gender_bar.update_layout(title_text='Data by Gender', width=1200)

            return gender_bar


if __name__ == '__main__':
    app.run_server(debug=True)
