#--------------- Import libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

import geopandas
import json

from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource

#----------------- Lectura y preparación de datos

st.set_page_config(layout="wide")

if 'reportes' not in st.session_state:
	st.session_state.reportes = pd.read_csv("Police_Department_Incident_Reports__2018_to_Present.csv") #path folder of the data file
reportes=st.session_state.reportes
#st.write(reportes) #displays the table of data
#Info de mapa de San Francisco
#sf= geopandas.read_file('C:\\Users\\angel\\Documents\\Analisis_datos\\Tableros\\Realtor_Neighborhoods.csv')
sf = geopandas.read_file('https://raw.githubusercontent.com/JimKing100/SF_Real_Estate_Live/master/data/Realtor%20Neighborhoods.geojson')


# Set the Coordinate Referance System (crs) for projections
# ESPG code 4326 is also referred to as WGS84 lat-long projection
sf.crs = {'init': 'epsg:4326'}

# Rename columns in geojson map file
sf = sf.rename(columns={'geometry': 'geometry','nbrhood':'neighborhood_name'}).set_geometry('geometry')

# Creación del objeto Mapa ----------------------------------

class Map():

	def json_data(self):
		
		# Bokeh uses geojson formatting, representing geographical features, with json
		# Convert to json
		sf_json = json.loads(sf.to_json())
		
		# Convert to json preferred string-like object 
		json_data = json.dumps(sf_json)
		return json_data


	def make_plot(self):

		#Create the figure object
		self.p = figure(height = 650, width = 850,toolbar_location = None, border_fill_color='#EE988C',  
			background_fill_color= '#E1DFDC')
		self.p.xgrid.grid_line_color = None
		self.p.ygrid.grid_line_color = None
		self.p.axis.visible = False
		
		# Add patch renderer to figure. 
		self.p.patches('xs','ys', source = geosource, fill_color = {'field' : 'neighborhood_name'}, line_color = 'black', line_width = 0.25, fill_alpha = 1)
	
	def add_markers(self, tipos_robo):
		df=pd.DataFrame()
		for robo in tipos_robo:
			df=df.append(reportes[reportes['Incident Category']==robo])
		self.p.hex(df['Longitude'],df['Latitude'], size=3, color='#F95B4C', alpha=0.5)

# Creación del objeto Filter----------------------

class Filter():

	def __init__(self):
		self.tipos_robo = pd.unique(reportes['Incident Category'].dropna()).tolist()
		#self.multi_choice.js_on_change("value", CustomJS(code="""
    	#	console.log('multi_choice: value=' + this.value, this.toString())
		#"""))
		#self.button = Button(label="Apply", button_type="success")
		#self.button.js_on_click(CustomJS(code="apply_filter()"))

	def apply_filter(self):
		st.session_state.initial_options = multi_choice
		st.experimental_rerun()
		map_object.make_plot()
		map_object.add_markers(multi_choice)
		map_object.show_plot()
		#st.title (st.session_state.initial_options)


#---------- Empieza inferfaz

#Instanciamos objetos y creamos mapa

map=Map()
geosource = GeoJSONDataSource(geojson = map.json_data())
map.make_plot()

#Obtenemos las opciones iniciales de la memoria de st
if 'initial_options' not in st.session_state:
	st.session_state.initial_options = ["Burglary", 'Assault']
map.add_markers(st.session_state.initial_options)

#Instanciamos el objeto f
f=Filter()

#----------------Interfaz: Mapa y filtro

r1_c1, r1_c2 = st.columns(2)
with r1_c1:
	st.subheader('Reported Crimes - San Francisco, California')
with r1_c2:
	st.subheader('Filter by crime type')

r2_c1, r2_c2, r2_c3 = st.columns([5,2,3])
with r2_c1:
	st.bokeh_chart(map.p, use_container_width=True)
with r2_c2:
	st.write(reportes['Incident Category'].value_counts())
with r2_c3:
	multi_choice = st.multiselect('Select crime types to be shown', f.tipos_robo, st.session_state.initial_options)
	button=st.button('Apply')

if button:
	f.apply_filter()


# ---------------- Gráficos Descriptivos

#preparamos información a mostrar
sub_categ = reportes[reportes['Incident Category'].isin(st.session_state.initial_options) ]['Incident Subcategory'].value_counts() 
sub_categ_chart = px.pie(values = sub_categ.values , names = sub_categ.index.values, color_discrete_sequence=px.colors.sequential.OrRd_r)

day_week = reportes[reportes['Incident Category'].isin(st.session_state.initial_options) ]['Incident Day of Week'].value_counts().to_frame()
try:
	day_week = day_week.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
except:
	pass
day_week['color']='red'
day_week_chart = px.bar(day_week, color='color', color_discrete_map={
	'red':'#F95B4C'})

district =  reportes[reportes['Incident Category'].isin(st.session_state.initial_options) ][['Incident Category','Police District', 'Incident ID']]
district = district.groupby(["Incident Category", "Police District"], as_index=False)['Incident ID'].count()
district.rename(columns={"Incident ID": "Count"}, inplace=True)
district_chart = px.sunburst(district, path=['Incident Category', 'Police District', 'Count'], values='Count')

r3_c1, r3_c2 = st.columns(2)

with r3_c1:
	st.subheader('Subcategories')
	st.plotly_chart(sub_categ_chart, use_container_width=True)
with r3_c2:
	st.subheader('Crimes by day of week')
	st.plotly_chart(day_week_chart, use_container_width=True)

st.subheader('Crimes by District')
st.plotly_chart(district_chart, use_container_width=True)
