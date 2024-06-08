from flask import Flask, jsonify, request
import subprocess

app = Flask(__name__, static_folder='', static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/find-path', methods=['POST'])
def find_path():
    
    start_lat = request.json.get('start_lat')
    start_lng = request.json.get('start_lng')
    end_lat = request.json.get('end_lat')
    end_lng = request.json.get('end_lng')

    print('Starting point:', start_lat, start_lng)
    print('Ending point:', end_lat, end_lng)

    # subprocess.run(['python3', 'script.py'])
    subprocess.run(['python3', 'script.py', str(start_lat), str(start_lng), str(end_lat), str(end_lng)])
    
    # Return a response
    return jsonify({'message': 'Python script executed successfully'})

if __name__ == '__main__':
    app.run(debug=True)
