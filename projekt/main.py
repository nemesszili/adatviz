import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json

import pycountry
from read_prepare_csv import population, road_motorways, by_road_user, by_age, by_vehicle, vehicle_stock

external_css = ['https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css']

external_js = ['https://code.jquery.com/jquery-3.3.1.slim.min.js',
			   'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js',
			   'https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/js/bootstrap.min.js'
			  ]

app = dash.Dash(
	__name__,
	external_scripts=external_js,
	external_stylesheets=external_css,
)

layout = dict(
	width = 700,
	height = 700,
	geo = dict(
		resolution = '50',
		scope = 'europe',
		lonaxis = dict(
			range = [-20, 30],
			dtick = 0
		),
		lataxis = dict(
			range = [35, 75],
			dtick = 0
		),
		showframe = True,
		showcoastlines = True,
		projection = dict(
			type = 'Mercator'
		),
	),
	clickmode='event+select'
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

categoryDropdownOptions = {
	'by_road_user': [],
	'by_vehicle': [],
	'by_age': []
}

for cat in list(by_road_user['Category'].unique()):
	categoryDropdownOptions['by_road_user'].append({'label': cat, 'value': cat})
for cat in list(by_vehicle['Category'].unique()):
	categoryDropdownOptions['by_vehicle'].append({'label': cat, 'value': cat})
for cat in list(by_age['Category'].unique()):
	categoryDropdownOptions['by_age'].append({'label': cat, 'value': cat})

app.layout = html.Div(children=[
	html.H1('Mortality statistics of Europe (2001-2016)', className='text-center', id='header'),

	html.Div(className='row', children=[
		html.Div(className='col-sm', children=[
			html.Div(
				style={'marginLeft': '50px', 'marginBottom': '20px', 'width': 600},
				children=[
				html.Div('Select year: ', style={'width': '18rem'}),
				dcc.Slider(
					id='year-slider',
					min=2001,
					max=2016,
					value=2001,
					marks={str(year): str(year) for year in range(2001, 2017)}
				)
			]),
			dcc.Graph(
				id='map',
				hoverData={'points': [
					{
						"curveNumber": 0,
						"pointNumber": 4,
						"pointIndex": 4,
						"location": "DEU",
						"text": "Germany"
    				}
				]},
				figure=dict(data=data, layout=layout)
			)
		]),

		html.Div(className='col-sm', children=[
			html.Div(className='row', children=[
				html.Div(
					className='col-sm',
					children=[
						html.Div(
							className='card',
							children=[
								html.Div('Country information', className='card-header'),
								html.Div(
									className='card-body text-left', 
									children=[
										html.H5(id='country', className='card-title'),
										html.P(
											className='card-text',
											children=[
												html.P(id='population'),
												html.P(id='roads', style={'white-space': 'pre-line'}),
												html.P(id='vehicleStock', style={'white-space': 'pre-line'})
											])
									])
							])
					]),
				html.Div(
					className='col-sm',
					style={'marginLeft': '10px'},
					children=[
						html.Div(children=[
							html.Div('Mortality by:', style={'width': '18rem'}),
							dcc.Dropdown(
								id='dataset',
								style={'width': '18rem'},
								options=[
									{'label': 'Road user', 'value': 'by_road_user'},
									{'label': 'Vehicle', 'value': 'by_vehicle'},
									{'label': 'Age', 'value': 'by_age'},
								],
								value='by_road_user',
							),
						]),
						html.Div(children=[
							html.Div('Select category:', style={'width': '18rem'}),
							dcc.Dropdown(
								id='category',
								style={'width': '18rem'},
								options=categoryDropdownOptions['by_road_user'],
								value=categoryDropdownOptions['by_road_user'][0]
							),
						]),
						html.Div(children=[
							html.Div('Unit:', style={'width': '18rem'}),
							dcc.Dropdown(
								id='unit',
								style={'width': '18rem'},
								options=[
									{'label': 'Number', 'value': 'num'},
									{'label': 'Per million inhabitants', 'value': 'million'}
								],
								value='num'
							)
						]),
					]
				),
				html.Div(className='col-sm')
			]),
			html.Div(className='row', children=[
				html.Div(className='col-sm', children=[
					dcc.Graph(id='hist-comparison')
				]),
			])
		])
	]),

	
	html.Div(id='output-container')
])

@app.callback(
	dash.dependencies.Output(component_id='country',component_property='children'),
	[dash.dependencies.Input(component_id='map',component_property='hoverData')],
	[dash.dependencies.State(component_id='year-slider',component_property='value')]
)
def map_hover1(hoverData, year):
	ret = ""
	if hoverData:
		hoverData = hoverData['points'][0]
		ret  = hoverData['text']

	return ret

@app.callback(
	dash.dependencies.Output(component_id='population',component_property='children'),
	[dash.dependencies.Input(component_id='map',component_property='hoverData')],
	[dash.dependencies.State(component_id='year-slider',component_property='value')]
)
def map_hover2(hoverData, year):
	ret = ""
	if hoverData:
		hoverData = hoverData['points'][0]
		country = hoverData['location']
		val = float(population[(population['CODE'] == country) & (population['TIME'] == year)]['Value'].values[0]) / 1000000
		ret = "Population: %.2f million" % (val)

	return ret

@app.callback(
	dash.dependencies.Output(component_id='roads',component_property='children'),
	[dash.dependencies.Input(component_id='map',component_property='hoverData')],
	[dash.dependencies.State(component_id='year-slider',component_property='value')]
)
def map_hover3(hoverData, year):
	ret = ""
	if hoverData:
		hoverData = hoverData['points'][0]
		country = hoverData['location']
		roads = road_motorways[(road_motorways['CODE'] == country) & (road_motorways['TIME'] == year)]
		ret = ""
		for index, row in roads.iterrows():
			val = int(row['Value'])
			if val > 0:
				ret += row['TRA_INFR'] + ": " + str(val) + " km\n"
			else:
				ret += row['TRA_INFR'] + ": N/A\n"

	return ret

@app.callback(
	dash.dependencies.Output(component_id='vehicleStock',component_property='children'),
	[dash.dependencies.Input(component_id='map',component_property='hoverData')],
	[dash.dependencies.State(component_id='year-slider',component_property='value')]
)
def map_hover4(hoverData, year):
	ret = ""
	if hoverData:
		hoverData = hoverData['points'][0]
		country = hoverData['location']
		val = int(vehicle_stock[(vehicle_stock['CODE'] == country) & (vehicle_stock['TIME'] == year)]['Value'].values[0])
		pop = population[(population['CODE'] == country) & (population['TIME'] == year)]
		if len(pop) > 1:
			pop = pop.drop_duplicates(subset=['CODE'], keep='first')
		pop = pop['Value']
		pop /= 1e6
		pop = float(pop.values[0])
		if val > 0:
			ret = "Vehicle Stock: " + str(val) + " 000\n"
			if pop > 0:
				ret += "Motoriaztion rate: %.2f" % (val / pop)
		else:
			ret = "Vehicle Stock: N/A"

	return ret

@app.callback(
	dash.dependencies.Output(component_id='category',component_property='options'),
	[dash.dependencies.Input(component_id='dataset', component_property='value')]
)
def update_categories_options(value):
	return categoryDropdownOptions[value]

@app.callback(
	dash.dependencies.Output(component_id='category', component_property='value'),
	[dash.dependencies.Input(component_id='category', component_property='options')]
)
def update_categories_value(options):
	return options[0]['value']

val_to_label = {
	'by_road_user': 'Road user',
	'by_vehicle': 'Vehicle',
	'by_age': 'Age'
}

@app.callback(
	dash.dependencies.Output(component_id='map',component_property='figure'),
	[
		dash.dependencies.Input(component_id='category', component_property='value'),
	 	dash.dependencies.Input(component_id='year-slider', component_property='value'),
	 	dash.dependencies.Input(component_id='dataset', component_property='value'),
	 	dash.dependencies.Input(component_id='unit', component_property='value')
	]
)
def update_map(category, year, dataset, unit):
	if dataset == 'by_road_user':
		data_to_pres = by_road_user[(by_road_user['Category'] == category) & (by_road_user.TIME == year)]
	elif dataset == 'by_vehicle':
		data_to_pres = by_vehicle[(by_vehicle['Category'] == category) & (by_vehicle.TIME == year)]
	elif dataset == 'by_age':
		data_to_pres = by_age[(by_age['Category'] == category) & (by_age.TIME == year)]
	
	val = data_to_pres['Value']
	if unit == 'million':
		country = data_to_pres['CODE']
		pop = population[(population['CODE'].isin(country)) & (population['TIME'] == year)]
		pop = pop.drop_duplicates(subset=['CODE'], keep='first')
		pop = pop['Value']
		pop /= 1e6
		val = data_to_pres['Value'].div(pop.values)
	
	return {
		"data": [
			dict(
				type = 'choropleth',
				locations = data_to_pres['CODE'],
				z = val,
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
					title = val_to_label[dataset]
				),
			)],
		"layout": layout
	}

@app.callback(
	dash.dependencies.Output(component_id='hist-comparison', component_property='figure'),
	[
		dash.dependencies.Input(component_id='map', component_property='selectedData'),
		dash.dependencies.Input(component_id='dataset', component_property='value'),
		dash.dependencies.Input(component_id='category', component_property='value'),
		dash.dependencies.Input(component_id='unit', component_property='value')
	]
)
def update_historical(selectedData, dataset, category, unit):
	if dataset == 'by_road_user':
		data_to_pres = by_road_user[by_road_user['Category'] == category]
	elif dataset == 'by_vehicle':
		data_to_pres = by_vehicle[by_vehicle['Category'] == category]
	elif dataset == 'by_age':
		data_to_pres = by_age[by_age['Category'] == category]

	title = 'Mortality by %s (%s)' % (val_to_label[dataset], category)
	if unit == 'million':
		title += ' per million inhabitants'

	countries = []
	if selectedData:
		for sel in selectedData['points']:
			countries.append(sel['location'])

	traces = []
	for country in countries:
		y_series = data_to_pres[data_to_pres['CODE'] == country]['Value']
		if unit == 'million':
			pop = population[(population['CODE'] == country) & \
							 (population['TIME'] < 2017)]
			if len(pop) > 30:
				pop = pop.iloc[::2, :]
			pop = pop['Value']
			pop /= 1e6
			y_series = y_series.div(pop.values)
		else:
			y_series = y_series.values
		traces.append(go.Scatter(
			x = np.arange(2001, 2017),
			y = y_series,
			mode='lines',
			name=country,
    		connectgaps=True
		))

	return {
		'data': traces,
		'layout': go.Layout(
			title=title,
			margin={'l': 40, 'b': 30, 't': 50, 'r': 40},
            height=450,
            hovermode='closest',
			xaxis=dict(
				tickmode='array'
			)
		)
	}

if __name__ == '__main__':
	app.run_server(debug=True)
