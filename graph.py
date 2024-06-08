from shapely.geometry import LineString, Point
import networkx as nx
import geojson
from geojson import dump
from shapely.ops import nearest_points
from rtree import index

def load_lamp_posts(path):
    with open(path) as file:
        data = geojson.load(file)
    lamp_posts = []
    for feature in data['features']:
        if feature['geometry']['type'] == 'Point':
            lamp_posts.append(tuple(feature['geometry']['coordinates']))
    return lamp_posts

def create_lamp_post_index(lamp_posts):
    idx = index.Index()
    for i, lamp in enumerate(lamp_posts):
        idx.insert(i, (lamp[0], lamp[1], lamp[0], lamp[1]))
    return idx

def graph_light(path, lamp_posts, lamp_post_index):
    with open(path) as file:
        data = geojson.load(file)

    G = nx.Graph()

    for feature in data['geometries']:
        if feature['type'] == 'LineString':
            coords = feature['coordinates']
            for i in range(len(coords) - 1):
                p1 = tuple(coords[i])
                p2 = tuple(coords[i + 1])
                line_segment = [p1, p2]
                distance = Point(p1).distance(Point(p2))
                lamp_count = count_lamp_posts_near_line(line_segment, lamp_posts, lamp_post_index)
                
                # heuristic
                adjusted_distance = distance / (1 + lamp_count)
                
                G.add_edge(p1, p2, weight=adjusted_distance)
    return G

def graph_district(): 
    return

def graph_default(path):
    with open(path) as file:
        data = geojson.load(file)

    G = nx.Graph()

    for feature in data['geometries']:
        if feature['type'] == 'LineString':
            coords = feature['coordinates']
            for i in range(len(coords) - 1):
                p1 = tuple(coords[i])
                p2 = tuple(coords[i + 1])
                G.add_edge(p1, p2)
    return G

def count_lamp_posts_near_line(line, lamp_posts, lamp_post_index, distance_threshold=0.001):
    count = 0
    line = LineString(line)
    minx, miny, maxx, maxy = line.bounds
    possible_matches = lamp_post_index.intersection((minx, miny, maxx, maxy))
    
    for idx in possible_matches:
        point = Point(lamp_posts[idx])
        if line.distance(point) <= distance_threshold:
            count += 1
    return count

def get_closest_node(G, point):
    distances = {node: Point(node).distance(Point(point)) for node in G.nodes}
    closest_node = min(distances, key=distances.get)
    return closest_node

def find_shortest_path(G, start, end):
    return nx.shortest_path(G, source=start, target=end, weight='weight')

def store_path_geojson(path):
    with open('path.geojson', 'w') as f:
        dump(geojson.Feature(geometry=LineString(path)), f)
