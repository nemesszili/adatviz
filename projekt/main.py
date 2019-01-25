import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd

import pycountry
from read_prepare_csv import population, road_motorways, by_road_user, by_age, by_vehicle, vehicle_stock

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv')


data = [ dict(
        type = 'choropleth',
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(
            autotick = False,
            tickprefix = '',
            title = 'GDP<br>Billions US$'),
      ) ]

layout = dict(
    width = 1024,
    height = 768,
    title = '2014 Global GDP<br>Source:\
            <a href="https://www.cia.gov/library/publications/the-world-factbook/fields/2195.html">\
            CIA World Factbook</a>',
    geo = dict(
        resolution = '50',
        scope = 'europe',
        showframe = True,
        showcoastlines = True,
        projection = dict(
            type = 'Mercator'
        )
    )
)


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=dict( data=data, layout=layout)
    ),

    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'by_road_user', 'value': 'by_road_user'},
            {'label': 'by_vehicle', 'value': 'by_vehicle'},
            {'label': 'by_age', 'value': 'by_age'},
            {'label': 'population', 'value': 'population'},
            {'label': 'roads_motorways', 'value': 'roads_motorways'},
            {'label': 'vehicle_stock', 'value': 'vehicle_stock'}
        ],
    ),
    html.Div(id='output-container')
])

@app.callback(
    dash.dependencies.Output(component_id='example-graph',component_property='figure'),
    [dash.dependencies.Input(component_id='my-dropdown', component_property='value')]
)
def update_map(value):
    if value == 'by_road_user':
        data_to_pres = by_road_user[by_road_user.TIME == 2001]
    elif value == 'by_vehicle':
        data_to_pres = by_vehicle[by_vehicle.TIME == 2001]
    elif value == 'by_age':
        data_to_pres = by_age[by_age.TIME == 2001]
    elif value == 'population':
        data_to_pres = population[population.TIME == 2001]
    elif value == 'roads_motorways':
        data_to_pres = roads_motorways[roads_motorways.TIME == 2001]
    else:
        data_to_pres = vehicle_stock[vehicle_stock.TIME == 2001]
    
    return {
                "data": [
                    dict(
                    type = 'choropleth',
                    locations = data_to_pres['CODE'],
                    z = data_to_pres['Value'],
                    text = data_to_pres['GEO'],
                    colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
                        [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
                    autocolorscale = False,
                    reversescale = True,
                    marker = dict(
                        line = dict (
                            color = 'rgb(180,180,180)',
                            width = 0.5
                        ) ),
                    colorbar = dict(
                        autotick = False,
                        tickprefix = '$',
                        title = value),
                    ) ],
                    "layout":layout
    }

if __name__ == '__main__':
    app.run_server(debug=True)