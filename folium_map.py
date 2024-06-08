import folium
from folium.plugins import MarkerCluster
import pandas as pd
import webbrowser

#Define coordinates of where we want to center our map
ams_coords = [52.3676, 4.9041]

def style(feature):
    return {
        'color': 'blue',       # Line color
        'weight': 2,           # Line thickness
        'opacity': 1           # Line opacity
    }

#Create the map
ams_map = folium.Map(location = ams_coords, zoom_start = 13)
folium.GeoJson('simplified_transport.json', style_function=style).add_to(ams_map)

#Display the map
ams_map.save('ams_map.html')
webbrowser.open('ams_map.html')

