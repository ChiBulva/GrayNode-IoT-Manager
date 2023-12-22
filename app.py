# Importing necessary modules
from flask import Flask, render_template, request, jsonify, url_for
import json
import os
import subprocess
import requests
from werkzeug.utils import secure_filename
import uuid  # For generating unique filenames

# Initializing Flask app
app = Flask(__name__)

# Middleware and configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit for uploaded content: 16 MB

# Endpoint: Home page
@app.route('/')
def index():
    image_url = url_for('static', filename='images/map.png')
    return render_template('index.html', image_url=image_url)

# Endpoint: Greeting for 'Chris'
@app.route('/chris', methods=['GET'])
def chris():
    return "Hello Chris"

# Endpoint: Save pin data
@app.route('/save_pins', methods=['POST'])
def save_pins():
    pins = request.json
    with open('JSON/pins.json', 'w') as file:
        json.dump(pins, file)
    return jsonify( { 'status': 'success' } )

# Endpoint: Retrieve pin data
@app.route('/get_pins', methods=['GET'])
def get_pins():
    print("YOYOYO")
    if os.path.exists('JSON/pins.json'):
        with open('JSON/pins.json', 'r') as file:
            pins = json.load(file)
            print(pins)
    else:
        pins = []  # Return an empty list if file does not exist
    return jsonify(pins)

# Endpoint: Get specific fields from JSON
@app.route('/info/json/<path:fields>', methods=['GET'])
def get_info_json(fields):
    # Process fields from request
    field_list = fields.strip("[]").replace("'", "").replace('"', "").split(',')

    if not field_list:
        return jsonify( { 'error': 'No fields provided' } ), 400

    result = []
    if os.path.exists('JSON/pins.json'):
        with open('JSON/pins.json', 'r') as file:
            pins = json.load(file)
            for pin in pins:
                pin_result = {}
                for field in field_list:
                    if field in pin:
                        pin_result[field] = pin[field]
                    elif 'data' in pin and field in pin['data']:
                        pin_result[field] = pin['data'][field]
                if pin_result:
                    result.append(pin_result)
            return jsonify(result)
    else:
        return jsonify( { 'error': 'Data file not found' } ), 404

# Endpoint: Get information in table format
@app.route('/info/table/<path:fields>', methods=['GET'])
def get_info_table(fields):
    # Process fields from request
    field_list = fields.strip("[]").replace("'", "").replace('"', "").split(',')

    if not field_list:
        return "No fields provided", 400

    pins_data = []
    if os.path.exists('JSON/pins.json'):
        with open('JSON/pins.json', 'r') as file:
            pins = json.load(file)
            for pin in pins:
                pin_data = {}
                for field in field_list:
                    if field in pin:
                        pin_data[field] = pin[field]
                    elif 'data' in pin and field in pin['data']:
                        pin_data[field] = pin['data'][field]
                pins_data.append(pin_data)
        return render_template('table_view.html', pins=pins_data, fields=field_list)
    else:
        return "Data file not found", 404

# Endpoint: List all fields from JSON data
@app.route('/info/fields', methods=['GET'])
def get_all_fields():
    field_set = set()
    if os.path.exists('JSON/pins.json'):
        with open('JSON/pins.json', 'r') as file:
            pins = json.load(file)
            print(pins)
            for pin in pins:
                field_set.update(pin.keys())
                if 'data' in pin:
                    field_set.update(pin['data'].keys())
            return jsonify(list(field_set))
    else:
        return jsonify( { 'error': 'Data file not found' } ), 404

# Commented out section: Ping IP functionality
# ...

# Endpoint: Upload image
@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify( { 'status': 'error', 'message': 'No image part' } ), 400

    files = request.files.getlist('image')
    reader_id = request.form['reader_id']

    saved_files = []
    for file in files:
        if file.filename == '':
            continue  # Skip empty files

        if file:  # Validate file type if needed
            filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
            directory = os.path.join('static', 'images', 'RFID', reader_id)
            if not os.path.exists(directory):
                os.makedirs(directory)
            filepath = os.path.join(directory, filename)
            file.save(filepath)
            saved_files.append(filepath)

    if not saved_files:
        return jsonify( { 'status': 'error', 'message': 'No files saved' } ), 400

    return jsonify( { 'status': 'success', 'message': 'Files saved', 'files': saved_files } ), 200

# Endpoint: View RFID images
@app.route('/view/RFID/<reader_id>')
def view_images(reader_id):
    directory = os.path.join('static', 'images', 'RFID', reader_id)
    static_directory = os.path.join('images', 'RFID', reader_id).replace('\\', '/')  # Ensure proper path format

    if os.path.exists(directory):
        images = [os.path.join(static_directory, file).replace('\\', '/') for file in os.listdir(directory)]  # Format paths correctly
        return render_template('view_images.html', images=images, reader_id=reader_id)
    else:
        return "No images found for this reader", 404

# Endpoint: Delete image
@app.route('/delete_image', methods=['DELETE'])
def delete_image():
    image_path = request.args.get('imagePath')
    
    # Construct path to image file
    static_dir = os.path.join(app.root_path, 'static')
    full_path = os.path.join(static_dir, image_path)

    try:
        print(full_path)  # For debugging
        if os.path.exists(full_path):
            os.remove(full_path)
            return jsonify( { 'status': 'success', 'message': 'Image deleted successfully' } )
        else:
            return jsonify( { 'status': 'error', 'message': 'Image not found' } ), 404
    except Exception as e:
        return jsonify( { 'status': 'error', 'message': str(e) } ), 500

# Commented out section: Ping IP functionality
# ...

# App startup configuration
if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000", debug=True)
