import folium
from folium.plugins import MarkerCluster
import pandas as pd
import webbrowser
from shapely.geometry import LineString, Point
import networkx as nx
import geojson

#Define coordinates of where we want to center our map
ams_coords = [52.3676, 4.9041]

def style(feature):
    return {
        'color': 'blue',       
        'weight': 2,           
        'opacity': 1           
    }

ams_map = folium.Map(location = ams_coords, zoom_start = 13)
folium.GeoJson('simplified_transport.json', style_function=style).add_to(ams_map)

def create_graph(geojson_data):
    G = nx.Graph()

    for feature in geojson_data['geometries']:
        if feature['type'] == 'LineString':
            coords = feature['coordinates']
            for i in range(len(coords) - 1):
                p1 = tuple(coords[i])
                p2 = tuple(coords[i + 1])
                distance = Point(p1).distance(Point(p2))
                G.add_edge(p1, p2, weight=distance)
    return G

# Function to find the shortest path using NetworkX
def find_shortest_path(G, start, end):
    print("Start point:", start)
    print("End point:", end)
    
    shortest_path = nx.shortest_path(G, source=start, target=end, weight='weight')
    print("Shortest path:", shortest_path)
    
    return shortest_path

# Function to convert path to GeoJSON format
def path_to_geojson(path):
    return geojson.Feature(geometry=LineString(path))

ams_path = open('simplified_transport.json')
ams_data = geojson.load(ams_path)
G = create_graph(ams_data)

start_coords = (4.8677, 52.35668)  
end_coords = (4.86459, 52.33480)   


shortest_path = find_shortest_path(G, start_coords, end_coords)
shortest_path_geojson = path_to_geojson(shortest_path)

folium.GeoJson(shortest_path_geojson, name='shortest_path', 
               style_function=lambda x: {'color': 'red', 'weight': 3}).add_to(ams_map)

# Display
ams_map.save('ams_map.html')
webbrowser.open('ams_map.html')



