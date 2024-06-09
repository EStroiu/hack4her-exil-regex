from flask import Flask, jsonify, request
import geojson 
from shapely.geometry import LineString, Point
import graph
import json

district_ratings = {}

print("Starting Flask app...")
app = Flask(__name__, static_folder='', static_url_path='')

def load_district_ratings(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_district_ratings(filepath, ratings):
    with open(filepath, 'w') as f:
        json.dump(ratings, f, indent=4)

district_ratings_file = 'district_ratings.json'
district_ratings = load_district_ratings(district_ratings_file)

districts = graph.load_crime_polygons('amsterdam_wijken_normalized.geojson')
district_idx = graph.build_spatial_index(districts)

def update_district_graph():
    global g_district
    g_district = graph.graph_district('simplified_transport.json', districts, district_idx, district_ratings)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/find-path', methods=['POST'])
def find_light_path():
    start_lat = request.json.get('start_lat')
    start_lng = request.json.get('start_lng')
    end_lat = request.json.get('end_lat')
    end_lng = request.json.get('end_lng')

    start = graph.get_closest_node(g_default, (start_lng, start_lat))
    end = graph.get_closest_node(g_default, (end_lng, end_lat))

    path_light = graph.find_shortest_path(g_light, start, end)
    path_default = graph.find_shortest_path(g_default, start, end)
    path_district = graph.find_shortest_path(g_district, start, end)

    ret_light = geojson.Feature(geometry=LineString(path_light))
    ret_default = geojson.Feature(geometry=LineString(path_default))
    ret_district = geojson.Feature(geometry=LineString(path_district))
    
    return jsonify((ret_light, ret_default, ret_district))

@app.route('/rate-wijk', methods=['POST'])
def rate_wijk():
    wijk = request.json.get('wijk')
    rating = request.json.get('rating')

    print(f"Received rating for {wijk}: {rating}")

    if wijk not in district_ratings:
        district_ratings[wijk] = []
    district_ratings[wijk].append(rating)

    new_ratings = [int(r) for r in district_ratings[wijk]]
    new_avg = sum(new_ratings) / len(new_ratings)
    print(new_avg)

    save_district_ratings(district_ratings_file, district_ratings)

    update_district_graph()

    return jsonify({"message": "Rating submitted successfully"})

def update_district_graph():
    global g_district
    crime_polygons = graph.load_crime_polygons('amsterdam_wijken_normalized.geojson')
    g_district = graph.graph_district('simplified_transport.json', crime_polygons, district_ratings)

if __name__ == '__main__':
    print("Getting lamp posts...")
    lamp_posts = graph.load_lamp_posts('amsterdam_street_lights.geojson')
    lamp_post_index = graph.create_lamp_post_index(lamp_posts)
    print("Computing graphs...")
    districts = graph.load_crime_polygons('amsterdam_wijken_normalized.geojson')
    g_light = graph.graph_light('simplified_transport.json', lamp_posts, lamp_post_index)
    g_default = graph.graph_default('simplified_transport.json')
    g_district = graph.graph_district('simplified_transport.json', districts, district_ratings)
    print("Done!")

    app.run(debug=False)
