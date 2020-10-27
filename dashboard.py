import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# general dash tutorial --> https://www.youtube.com/watch?v=hSPmj7mK6ng

app = dash.Dash(__name__)

# read data set
df = pd.read_csv('year_data/2010.csv')

# dash components and html goes here
app.layout = html.Div([

    html.H1("Suicides in India Dashboard", style={'text-align': 'center'}),

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

    # these returns match to the output array in @app.callback
    return container, fig


if __name__ == '__main__':
    app.run_server(debug=True)
