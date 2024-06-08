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

@app.route('/find-light-path', methods=['POST'])
def find_path():
    start_lat = request.json.get('start_lat')
    start_lng = request.json.get('start_lng')
    end_lat = request.json.get('end_lat')
    end_lng = request.json.get('end_lng')

    start = graph.get_closest_node(g_light, (start_lng, start_lat))
    end = graph.get_closest_node(g_light, (end_lng, end_lat))

    path = graph.find_shortest_path(g_light, start, end)

    return jsonify(geojson.Feature(geometry=LineString(path)))

@app.route('/find-default-path', methods=['POST'])
def find_path():
    start_lat = request.json.get('start_lat')
    start_lng = request.json.get('start_lng')
    end_lat = request.json.get('end_lat')
    end_lng = request.json.get('end_lng')

    start = graph.get_closest_node(g_default, (start_lng, start_lat))
    end = graph.get_closest_node(g_default, (end_lng, end_lat))

    path = graph.find_shortest_path(g_default, start, end)

    return jsonify(geojson.Feature(geometry=LineString(path)))

if __name__ == '__main__':
    app.run(port=5001, debug=True)
