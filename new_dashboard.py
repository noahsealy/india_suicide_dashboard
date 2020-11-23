import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df = pd.read_csv('processed_suicide_data.csv')
data = pd.read_csv('data.csv')

app.layout = dbc.Container([

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
        children=[
            dbc.Col(
                children=[
                    dcc.Graph(id='suicide_map', figure={}),
                    html.Br(),
                    html.P(id='year_display', children={}),
                    html.P(id='selected_display', children={}),

                    dcc.Slider(
                        id='select_year',
                        min=2001,
                        max=2012,
                        step=1,
                        value=2012,
                    ),

                ]
            )
        ]
    ),
    html.Hr(),

    dbc.Row(
        children=[
            dbc.Col(
                children=[
                    html.P(children='Select Type Code:'),
                    dcc.Dropdown(id='type_code_select',
                                 options=[{'label': 'Profession', 'value': 0},
                                          {'label': 'Cause', 'value': 1},
                                          {'label': 'Social Status', 'value': 2},
                                          {'label': 'Education', 'value': 3}],
                                 value=0),
                ],
                className='col-4'
            ),
            dbc.Col(
                children=[
                    html.P(children='Select Gender:'),
                    dcc.Dropdown(id='gender_select',
                                 options=[{'label': 'Male', 'value': 0},
                                          {'label': 'Female', 'value': 1},
                                          {'label': 'Male & Female', 'value': 2}],
                                 value=2,
                                 clearable=False),
                ],
                className='col-4'
            ),
            dbc.Col(
                children=[
                    html.P(children='Select Age Range:'),
                    dcc.Dropdown(id='age_select',
                                 options=[{'label': '0-14', 'value': 0},
                                          {'label': '15-29', 'value': 1},
                                          {'label': '30-44', 'value': 2},
                                          {'label': '45-59', 'value': 3},
                                          {'label': '60+', 'value': 4}],
                                 value=2,
                                 clearable=False),
                ],
                className='col-4'
            ),
        ]
    ),

    dbc.Row(
        children=[
            dbc.Col(
                children=[
                    dcc.Graph(id='trends_figure', figure={}),
                ]
            )
        ]
    ),

    # dbc.Row(
    #     children=[
    #         dbc.Col(
    #             children=[
    #                 dcc.Dropdown(id='confusion_x_select', value=0,
    #                              options=[{'label': 'Profession', 'value': 0},
    #                                       {'label': 'Cause', 'value': 1},
    #                                       {'label': 'Education Level', 'value': 2},
    #                                       {'label': 'Social Status', 'value': 3}],
    #                              clearable=False),
    #             ],
    #             className='col-6'
    #         ),
    #         dbc.Col(
    #             children=[
    #                 dcc.Dropdown(id='confusion_y_select', value=1,
    #                              options=[{'label': 'Profession', 'value': 0},
    #                                       {'label': 'Cause', 'value': 1},
    #                                       {'label': 'Education Level', 'value': 2},
    #                                       {'label': 'Social Status', 'value': 3}],
    #                              clearable=False),
    #             ],
    #             className='col-6'
    #
    #         )
    #     ],
    # ),
    # dbc.Row(
    #     children=[
    #         dbc.Col(
    #             children=[
    #                 dcc.Graph(id='feature_description', figure={}),
    #                 html.P(id='risk_level', children={}),
    #                 html.P(children='Note: if a single state was selected, this data is based on that state from 2001 '
    #                                 'to 2012 data.')
    #             ]
    #         )
    #     ]
    # ),
    # html.Hr(),

])


# connect Plotly graphs and Dash components
@app.callback(
    [Output(component_id='year_display', component_property='children'),
     Output(component_id='suicide_map', component_property='figure')],
    [Input(component_id='select_year', component_property='value')]
)
def update_graph(slider_select):
    container = "Year: {}".format(slider_select)

    dff = df[df['Year'] == slider_select]

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
        hover_data=['State', 'Total'],
        # color_continuous_scale=px.colors.sequential.YlOrRd,
        color_continuous_scale='Reds',
        range_color=[0, 20000],
        labels={'Total': 'Total Suicides'},
        # template='plotly_dark',
    )

    fig.update_geos(fitbounds="locations", visible=False)

    return container, fig


@app.callback(Output(component_id='selected_display', component_property='children'),
              [Input(component_id='suicide_map', component_property='clickData'),
               Input(component_id='suicide_map', component_property='selectedData')])
def display_selected_state(clicked, selected):
    try:
        if selected is None:
            selected = clicked

        # extract selected data
        states = []
        for point in selected['points']:
            for attr, value in point.items():
                if attr == 'location':
                    states.append(str(value))

        # return string for display
        states_ret = 'State(s): '
        for state in states:
            states_ret = states_ret + str(state) + ', '

        return states_ret
    except TypeError:
        return 'States(s): Maharashtra,'


@app.callback(Output(component_id='trends_figure', component_property='figure'),
              [Input(component_id='suicide_map', component_property='clickData'),
               Input(component_id='suicide_map', component_property='selectedData'),
               Input(component_id='type_code_select', component_property='value'),
               Input(component_id='gender_select', component_property='value'),
               Input(component_id='age_select', component_property='value')])
def trends_fig(clicked, selected, type_code, gender, age):
    try:
        if selected is None:
            selected = clicked

        # extract selected data
        states = []
        for point in selected['points']:
            for attr, value in point.items():
                if attr == 'location':
                    states.append(str(value))

        # return string for display
        states_ret = 'State(s): '
        for state in states:
            states_ret = states_ret + str(state) + ', '

        # keep on refining the data set based on the input
        selected_states = data[data['State'].isin(states)]

        # profession
        if type_code == 0:
            selected_code = selected_states[selected_states['Type_code'] == 'Professional_Profile']
        # cause
        elif type_code == 1:
            selected_code = selected_states[selected_states['Type_code'] == 'Causes']
        # social status, special age range
        elif type_code == 2:
            selected_code = selected_states[selected_states['Type_code'] == 'Social_Status']
        # education, special age range
        else:
            selected_code = selected_states[selected_states['Type_code'] == 'Education_Status']

        # male
        if gender == 0:
            selected_gender = selected_code[selected_code['Gender'] == 'Male']
        # female
        elif gender == 1:
            selected_gender = selected_code[selected_code['Gender'] == 'Female']
        # male & female
        else:
            selected_gender = selected_code

        if age == 0:
            selected_age = selected_gender[selected_gender['Age_group'] == '0-14']
        elif age == 1:
            selected_age = selected_gender[selected_gender['Age_group'] == '15-29']
        elif age == 2:
            selected_age = selected_gender[selected_gender['Age_group'] == '30-44']
        elif age == 3:
            selected_age = selected_gender[selected_gender['Age_group'] == '45-59']
        else:
            selected_age = selected_gender[selected_gender['Age_group'] == '60']

        refined_data = selected_age
        uniqueValues = refined_data['Type'].unique()

        fig = go.Figure()

        years = [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012]

        for type in uniqueValues:
            y = []
            for year in years:
                temp = refined_data[refined_data['Type'] == type]
                y.append(temp[temp['Year'] == year]['Total'].sum())

            fig.add_trace(go.Scatter(x=years,
                                     y=y,
                                     mode='lines+markers', name=type))

        return fig
    except TypeError:
        fig = go.Figure()
        return fig


# # confusion matrix -- to be removed soon...
# @app.callback(
#     [Output(component_id='selected_display', component_property='children'),
#      Output(component_id='feature_description', component_property='figure')],
#     [Input(component_id='suicide_map', component_property='clickData'),
#      Input(component_id='suicide_map', component_property='selectedData'),
#      Input(component_id='confusion_x_select', component_property='value'),
#      Input(component_id='confusion_y_select', component_property='value'),
#      Input(component_id='select_year', component_property='value')]
#
# )
# def select_state(clicked, selected, confusion_x, confusion_y, selected_year):
#     try:
#         if selected is None:
#             selected = clicked
#
#         # extract selected data
#         states = []
#         for point in selected['points']:
#             for attr, value in point.items():
#                 if attr == 'location':
#                     states.append(str(value))
#
#         # return string for display
#         states_ret = 'State(s): '
#         for state in states:
#             states_ret = states_ret + str(state) + ', '
#
#         # grab selected data
#         dff = df[df['State'].isin(states)]
#         selected_states = dff[dff['Year'] == selected_year]
#
#         # split up data
#         profession_col = []
#         profession_label = []
#         education_col = []
#         education_label = []
#         social_col = []
#         social_label = []
#         cause_col = []
#         cause_label = []
#         for feature in selected_states.columns:
#             if 'Professional_Profile_' in feature:
#                 label = feature[21:]
#                 profession_col.append(feature)
#                 profession_label.append(label)
#             elif 'Education_Status_' in feature:
#                 label = feature[17:]
#                 education_col.append(feature)
#                 education_label.append(label)
#             elif 'Social_Status_' in feature:
#                 label = feature[14:]
#                 social_col.append(feature)
#                 social_label.append(label)
#             elif 'Causes_' in feature:
#                 label = feature[7:]
#                 cause_col.append(feature)
#                 cause_label.append(label)
#
#         # select label depending on selection for x
#         if confusion_x == 'Cause':
#             #x = selected_states[cause_col]
#             x = cause_col
#             x_labels = cause_label
#         elif confusion_x == 'Education Level':
#             #x = selected_states[education_col]
#             x = education_col
#             x_labels = education_label
#         elif confusion_x == 'Social Status':
#             #x = selected_states[social_col]
#             x = social_col
#             x_labels = social_label
#         else: #  default to profession for x
#             #x = selected_states[profession_col]
#             x = profession_col
#             x_labels = profession_label
#
#         # select label depending on selection for y
#         if confusion_y == 'Profession':
#             #y = selected_states[profession_col]
#             y = profession_col
#             y_labels = profession_label
#         elif confusion_y == 'Education Level':
#             #y = selected_states[education_col]
#             y = education_col
#             y_labels = education_label
#         elif confusion_y == 'Social Status':
#             #y = selected_states[social_col]
#             y = social_col
#             y_labels = social_label
#         else: #  default to profession for y
#             #y = selected_states[cause_col]
#             y = cause_col
#             y_labels = cause_label
#
#         # # find correlation matrix
#         # corr = selected_states[['Total', feature]].corr(method='pearson')
#
#         x.extend(y)
#         print(selected_states[x])
#         x_labels.extend(y_labels)
#         corr = selected_states[x].corr(method='pearson')
#         #corr = selected_states[x].corrwith(selected_states[y])
#         #corr = selected_states[['Total', feature]].corr(method='pearson')
#         #print(corr)
#         # # visualize correlation matrix
#         corr_map = go.Figure()
#         corr_map.add_trace(go.Heatmap(x=x_labels, y=x_labels, z=corr, colorscale='reds'))
#         #corr_map.add_trace(go.Heatmap(x=x_labels, y=y_labels, z=corr, colorscale='reds'))
#         corr_map.update_layout(title_text='Correlation Heatmap', height=700)
#
#         return states_ret, corr_map
#
#     # init data
#     except TypeError:
#         states = 'Maharashtra'
#
#         fig = go.Figure()
#
#         return 'State(s): ' + states, fig


if __name__ == '__main__':
    app.run_server(debug=True)
