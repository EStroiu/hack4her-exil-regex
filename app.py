from flask import Flask, jsonify, request
import geojson 
from shapely.geometry import LineString, Point
import graph

app = Flask(__name__, static_folder='', static_url_path='')
G = graph.create_graph('simplified_transport.json')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/find-path', methods=['POST'])
def find_path():
    start_lat = request.json.get('start_lat')
    start_lng = request.json.get('start_lng')
    end_lat = request.json.get('end_lat')
    end_lng = request.json.get('end_lng')

    start = graph.get_closest_node(G, (start_lng, start_lat))
    end = graph.get_closest_node(G, (end_lng, end_lat))

    path = graph.find_shortest_path(G, start, end)

    return jsonify(geojson.Feature(geometry=LineString(path)))

@app.route('/rate-wijk', methods=['POST'])
def rate_wijk():
    wijk = request.json.get('wijk')
    rating = request.json.get('rating')

    # Process the rating (e.g., store it in a database or file)
    # For now, we'll just print it
    print(f"Received rating for {wijk}: {rating}")

    return jsonify({"message": "Rating submitted successfully"})

if __name__ == '__main__':
    app.run(debug=True)
