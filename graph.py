from shapely.geometry import LineString, Point, shape
import networkx as nx
import geojson
from geojson import dump
from shapely.ops import nearest_points
from rtree import index
import math

def load_lamp_posts(path):
    with open(path) as file:
        data = geojson.load(file)
    lamp_posts = []
    for feature in data['features']:
        if feature['geometry']['type'] == 'Point':
            lamp_posts.append(tuple(feature['geometry']['coordinates']))
    return lamp_posts

def load_crime_polygons(path):
    with open(path) as file:
        data = geojson.load(file)
    crime_polygons = []
    for feature in data['features']:
        if feature['geometry']['type'] == 'Polygon':
            polygon = shape(feature['geometry'])
            crime_rate = feature['properties'].get('CriminalityScore', 0)
            district = feature['properties'].get('district', '')  
            crime_polygons.append((polygon, crime_rate, district))
    return crime_polygons

def create_lamp_post_index(lamp_posts):
    idx = index.Index()
    for i, lamp in enumerate(lamp_posts):
        idx.insert(i, (lamp[0], lamp[1], lamp[0], lamp[1]))
    return idx

def graph_light(path, lamp_posts, lamp_post_index):
    print("Creating light graph...")
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

def graph_district(path, districts, district_ratings):
    print("Creating criminality graph...")
    with open(path) as file:
        data = geojson.load(file)

    G = nx.Graph()
    k = 5
    district_idx = build_spatial_index(districts)

    for feature in data['geometries']:
        if feature['type'] == 'LineString':
            coords = feature['coordinates']
            for i in range(len(coords) - 1):
                p1 = tuple(coords[i])
                p2 = tuple(coords[i + 1])
                line_segment = [p1, p2]
                distance = Point(p1).distance(Point(p2))
                crime_rate = get_crime_rate_for_line(line_segment, districts, district_idx, district_ratings)

                # heuristic with exponential growth
                adjusted_distance = distance * math.exp(k * crime_rate)
                
                G.add_edge(p1, p2, weight=adjusted_distance)
    print("Done!")
    return G

def build_spatial_index(crime_polygons):
    idx = index.Index()
    for i, (polygon, crime_rate, district) in enumerate(crime_polygons):
        idx.insert(i, polygon.bounds)
    return idx

def get_crime_rate_for_line(line, crime_polygons, district_idx, district_ratings):
    line = LineString(line)
    total_crime_rate = 0
    count = 0

    # Get potential intersecting polygons using spatial index
    possible_matches = list(district_idx.intersection(line.bounds))
    
    for idx in possible_matches:
        polygon, crime_rate, district = crime_polygons[idx]
        if polygon.intersects(line):
            adjusted_crime_rate = crime_rate
            if district in district_ratings:
                avg_rating = sum(district_ratings[district]) / len(district_ratings[district])
                # Adjust crime rate based on the average rating (scale rating to be between 0 and 1)
                adjusted_crime_rate = crime_rate * (1 - (avg_rating / 10))
            total_crime_rate += adjusted_crime_rate
            count += 1

    return total_crime_rate / count if count > 0 else 0

def graph_default(path):
    print("Creating default graph...")
    with open(path) as file:
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

def count_lamp_posts_near_line(line, lamp_posts, lamp_post_index, distance_threshold=0.01):
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
