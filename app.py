from flask import Flask, jsonify, request
import geojson 
from shapely.geometry import LineString, Point
import graph

app = Flask(__name__, static_folder='', static_url_path='')
lamp_posts = graph.load_lamp_posts('amsterdam_street_lights.geojson')
lamp_post_index = graph.create_lamp_post_index(lamp_posts)
g_light = graph.graph_light('simplified_transport.json', lamp_posts, lamp_post_index)
g_default = graph.graph_default('simplified_transport.json')

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

    ret_light = geojson.Feature(geometry=LineString(path_light))
    ret_default = geojson.Feature(geometry=LineString(path_default))

    return jsonify((ret_light, ret_default))

@app.route('/rate-wijk', methods=['POST'])
def rate_wijk():
    wijk = request.json.get('wijk')
    rating = request.json.get('rating')

    # Process the rating (e.g., store it in a database or file)
    # For now, we'll just print it
    print(f"Received rating for {wijk}: {rating}")

    return jsonify({"message": "Rating submitted successfully"})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
