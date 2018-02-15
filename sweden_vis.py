import numpy as np
import pandas as pd

from bokeh.layouts import column, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, LinearColorMapper
from bokeh.models.widgets import Select
from bokeh.palettes import Plasma10
from bokeh.plotting import curdoc, figure, output_file, show


def update_data(attrname, old, new):
    if select.value == 'Population':
        newSource = pop_dict
        hover.tooltips = [('Name', '@name'),
                          ('Population', '@data'),
                          ('Long, Lat', '($x, $y)')]

    if select.value == 'Population density':
        newSource = density_dict
        hover.tooltips = [('Name', '@name'),
                          ('Population density', '@data')]

    if select.value == 'Population change':
        newSource = change_dict
        hover.tooltips = [('Name', '@name'),
                          ('Population change', '@data')]

    if select.value == 'Car ownership per 1000 inhabitans':
        newSource = cars_dict
        hover.tooltips = [('Name', '@name'),
                          ('Car density', '@data')]

    if select.value == 'County area':
        newSource = pop_dict
        hover.tooltips = [('Name', '@name'),
                          ('Area', '@data')]

    ds.data = newSource


geo_data = pd.read_json('./data/sweden_geo.json')

population_data = pd.read_csv('./data/befolkning_kv1-3_2017.csv')
population_data['county_name'] = population_data['county_name'].str.replace('\s+', '')
population_data['population'] = population_data['population'].str.replace('\s', '')
population_data['population_change'] = \
    population_data['population_change'].str.replace('\s', '')
population_data.sort_values(by='county_name', inplace=True)
population_data.reset_index(drop=True, inplace=True)

car_data = pd.read_csv('./data/bilinnehav_per_1000_2017.csv')
car_data.sort_values(by='county_name', inplace=True)
car_data.reset_index(drop=True, inplace=True)

area_data = pd.read_csv('./data/kommun_area.csv')
area_data.sort_values(by='county_name', inplace=True)
area_data.reset_index(drop=True, inplace=True)

output_file('sweden_population.html')

longs = []
lats = []
for c in range(geo_data.shape[0]):
    county_longs = []
    county_lats = []
    for i in range(len(geo_data['geometry'][c]['coordinates'][0])):
        county_longs.append(geo_data['geometry'][c]['coordinates'][0][i][0])
        county_lats.append(geo_data['geometry'][c]['coordinates'][0][i][1])
    longs.append(county_longs)
    lats.append(county_lats)

county_names = [name for name in population_data['county_name']]
county_pops = [int(pop) for pop in population_data['population']]
county_change = [int(chng) for chng in population_data['population_change']]
county_cars = [cars for cars in car_data['cars_per_1000_citizens']]
county_areas = [area for area in area_data['area']]
county_pop_density = [round(int(pop) / int(area), 2)
                      for pop, area in zip(population_data['population'], area_data['area'])]

palette = Plasma10
palette.reverse()
color_mapper = LinearColorMapper(palette=palette)
TOOLS = 'pan,wheel_zoom,box_zoom,reset,hover,save'

pop_dict = dict(x=longs,
                y=lats,
                name=county_names,
                data=county_pops,
                col=np.log(county_pops))
change_dict = dict(x=longs,
                   y=lats,
                   name=county_names,
                   data=county_change,
                   col=county_change)
cars_dict = dict(x=longs,
                 y=lats,
                 name=county_names,
                 data=county_cars,
                 col=county_cars)
area_dict = dict(x=longs,
                 y=lats,
                 name=county_names,
                 data=county_areas,
                 col=(-1) * county_areas)
density_dict = dict(x=longs,
                    y=lats,
                    name=county_names,
                    data=county_pop_density,
                    col=np.log(county_pop_density))

source = ColumnDataSource(pop_dict)

p = figure(plot_width=500, plot_height=1000,
           title='Swedish county populations in 2017', tools=TOOLS,
           x_axis_location=None, y_axis_location=None)
p.grid.grid_line_color = None

patch = p.patches('x', 'y', source=source,
                  fill_color={'field': 'col', 'transform': color_mapper},
                  fill_alpha=0.7, line_color='white', line_width=0.5)
ds = patch.data_source

hover = p.select_one(HoverTool)
hover.point_policy = 'follow_mouse'
hover.tooltips = [('Name', '@name'),
                  ('Population', '@data'),
                  ('Long, Lat', '($x, $y)')]

select = Select(title='Data:', options=['Population',
                                        'Population density',
                                        'Population change',
                                        'Car ownership per 1000 inhabitans',
                                        'County area'])
select.on_change('value', update_data)

layout = column(widgetbox(select), p)
curdoc().add_root(layout)
show(layout)
