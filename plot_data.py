import geopandas as gpd
import geoplot.crs as gcrs
import geoplot as gplt
import matplotlib.pyplot as plt
import json
import fiona 
import plotly.express as px
import plotly.graph_objects as go
from IPython.display import Image
import geojson


# read geojson files
transportation = gpd.read_file('amsterdam_transportation.geojson')
buildings = gpd.read_file('amsterdam_buildings.geojson')
places = gpd.read_file('amsterdam_places.geojson')

transportation.plot()
plt.savefig('transportation.png')

buildings.plot()
plt.savefig('buildings.png')

places.plot()
plt.savefig('places.png')
