import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd

import pycountry
from read_prepare_csv import population, road_motorways, by_road_user, by_age, by_vehicle, vehicle_stock

external_css = ['https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css']

external_js = ['https://code.jquery.com/jquery-3.3.1.slim.min.js',
'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js',
'https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/js/bootstrap.min.js'
]

app = dash.Dash(__name__)
for css in external_css:
	app.css.append_css({"external_url": css})
for js in external_js:
	app.scripts.append_script({"external_url": js})

layout = dict(
	width = 1024,
	height = 768,
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

data = dict(
		type = 'choropleth',
		locations = [],
		z = [],
		text = [],
		colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
			[0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
		autocolorscale = False,
		reversescale = True,
		marker = dict(
			line = dict (
				color = 'rgb(180,180,180)',
				width = 0.5
			)
		),
		colorbar = dict(
			autotick = True
		),
	)

yearDropdownOptions = []
for i in range(2001, 2017):
	yearDropdownOptions.append({'label': i, 'value': i})

categoryDropdownOptions = {
	'by_road_user': [],
	'by_vehicle': [],
	'by_age': []
}

for cat in list(by_road_user['Category'].unique()):
	categoryDropdownOptions['by_road_user'].append({'label': cat, 'value': cat});
for cat in list(by_vehicle['Category'].unique()):
	categoryDropdownOptions['by_vehicle'].append({'label': cat, 'value': cat});
for cat in list(by_age['Category'].unique()):
	categoryDropdownOptions['by_age'].append({'label': cat, 'value': cat});

app.layout = html.Div(children=[
	html.H1('Mortality statistics of Europe (2001-2016)', className='text-center', id='header'),

	html.Div(className='row', children=[
		html.Div(className='col-sm',children=[
			dcc.Graph(
				id='example-graph',
				figure=dict( data=data, layout=layout)
			)
		]),

		html.Div(className='col-sm', children=[
			html.Div(children=[
				html.Div('Mortality by: ', className='col-sm'),
				dcc.Dropdown(
					id='my-dropdown',
					options=[
						{'label': 'Road user', 'value': 'by_road_user'},
						{'label': 'Vehicle', 'value': 'by_vehicle'},
						{'label': 'Age', 'value': 'by_age'},
					],
					value='by_road_user',
				),
			]),
			html.Div(children=[
				html.Div('Select category'),
				dcc.Dropdown(
					id='category-dropdown',
					options=categoryDropdownOptions['by_road_user'],
					value=categoryDropdownOptions['by_road_user'][0]
				),
			]),
			html.Div(children=[
				html.Div('Select year: ', className='col-sm'),
				dcc.Dropdown(
					id='year-dropdown',
					options=yearDropdownOptions,
					value=2001
				)
			]),
			html.Div(children=[
				html.P(id='country', className='text-center font-weight-bold'),
				html.P(id='population'),
				html.P(id='roads'),
				html.P(id='vehicleStock'),
			]),

		])
	]),

	
	html.Div(id='output-container')
])

@app.callback(
	dash.dependencies.Output(component_id='header', component_property='children'),
	[dash.dependencies.Input(component_id='example-graph', component_property='clickData')]
)
def display_selected_data(clickData):
	print(clickData)
	return "testing"


@app.callback(
	dash.dependencies.Output(component_id='country',component_property='children'),
	[dash.dependencies.Input(component_id='example-graph',component_property='hoverData')],
	[dash.dependencies.State(component_id='year-dropdown',component_property='value')]
)
def map_hover1(hoverData, year):
	ret = ""
	if hoverData != None:
		hoverData = hoverData['points'][0]
		ret  = hoverData['text']

	return ret

@app.callback(
	dash.dependencies.Output(component_id='population',component_property='children'),
	[dash.dependencies.Input(component_id='example-graph',component_property='hoverData')],
	[dash.dependencies.State(component_id='year-dropdown',component_property='value')]
)
def map_hover2(hoverData, year):
	ret = "Hover over a country which is not white :)"
	if hoverData != None:
		hoverData = hoverData['points'][0]
		country = hoverData['location']
		ret = "Population: " + str(population[(population['CODE'] == country) & (population['TIME'] == year)]['Value'].values[0])

	return ret

@app.callback(
	dash.dependencies.Output(component_id='roads',component_property='children'),
	[dash.dependencies.Input(component_id='example-graph',component_property='hoverData')],
	[dash.dependencies.State(component_id='year-dropdown',component_property='value')]
)
def map_hover3(hoverData, year):
	ret = "Hover over a country which is not white :)"
	if hoverData != None:
		hoverData = hoverData['points'][0]
		country = hoverData['location']
		roads = road_motorways[(road_motorways['CODE'] == country) & (road_motorways['TIME'] == year)]
		ret = "Roads: "
		for index, row in roads.iterrows():
			ret += row['TRA_INFR'] + " - " + str(row['Value']) + " km"
			ret += "  "

	return ret

@app.callback(
	dash.dependencies.Output(component_id='vehicleStock',component_property='children'),
	[dash.dependencies.Input(component_id='example-graph',component_property='hoverData')],
	[dash.dependencies.State(component_id='year-dropdown',component_property='value')]
)
def map_hover4(hoverData, year):
	ret = "Hover over a country which is not white :)"
	if hoverData != None:
		hoverData = hoverData['points'][0]
		country = hoverData['location']
		ret = "Vehicle Stock: " + str(vehicle_stock[(vehicle_stock['CODE'] == country) & (vehicle_stock['TIME'] == year)]['Value'].values[0]) + " thousand"

	return ret

@app.callback(
	dash.dependencies.Output(component_id='category-dropdown',component_property='options'),
	[dash.dependencies.Input(component_id='my-dropdown', component_property='value')]
)
def update_categories_options(value):
	return categoryDropdownOptions[value]

@app.callback(
	dash.dependencies.Output(component_id='category-dropdown',component_property='value'),
	[dash.dependencies.Input(component_id='category-dropdown', component_property='options')]
)
def update_categories_value(options):
	return options[0]['value']

@app.callback(
	dash.dependencies.Output(component_id='example-graph',component_property='figure'),
	[
	 dash.dependencies.Input(component_id='category-dropdown', component_property='value'),
	 dash.dependencies.Input(component_id='year-dropdown', component_property='value'),
	 dash.dependencies.Input(component_id='my-dropdown', component_property='value'),
	]
)
def update_map(category, year, value):
	if value == 'by_road_user':
		data_to_pres = by_road_user[(by_road_user['Category'] == category) & (by_road_user.TIME == year)]
	elif value == 'by_vehicle':
		data_to_pres = by_vehicle[(by_vehicle['Category'] == category) & (by_vehicle.TIME == year)]
	elif value == 'by_age':
		data_to_pres = by_age[(by_age['Category'] == category) & (by_age.TIME == year)]
	
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
						)
					),
					colorbar = dict(
						autotick = True,
						title = value
					),
				)],
				"layout":layout
	}

if __name__ == '__main__':
	app.run_server(debug=True)