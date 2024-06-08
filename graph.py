from shapely.geometry import LineString, Point
import networkx as nx
import geojson
from geojson import dump

def create_graph(path):
    file = open(path)
    data = geojson.load(file)

    G = nx.Graph()

    for feature in data['geometries']:
        if feature['type'] == 'LineString':
            coords = feature['coordinates']
            for i in range(len(coords) - 1):
                p1 = tuple(coords[i])
                p2 = tuple(coords[i + 1])
                distance = Point(p1).distance(Point(p2))
                G.add_edge(p1, p2, weight=distance)
    return G

def get_closest_node(G, point):
    distances = {node: Point(node).distance(Point(point)) for node in G.nodes}
    closest_node = min(distances, key=distances.get)

    return closest_node

def find_shortest_path(G, start, end):
    return nx.shortest_path(G, source=start, target=end, weight='weight')

def store_path_geojson(path):
    with open('path.geojson', 'w') as f:
        dump(geojson.Feature(geometry=LineString(path)), f)