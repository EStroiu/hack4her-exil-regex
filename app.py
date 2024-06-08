from flask import Flask, jsonify, render_template
import subprocess

app = Flask(__name__, static_folder='', static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/find-path', methods=['POST'])
def find_path():
    # Execute the Python script
    subprocess.run(['python3', 'script.py'])
    
    # Return a response
    return jsonify({'message': 'Python script executed successfully'})

if __name__ == '__main__':
    app.run(debug=True)
