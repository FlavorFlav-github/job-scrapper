import json
import os
from flask import Flask, request, jsonify, send_file


current_script_path = os.path.dirname(os.path.abspath(__file__))
Base_directory = current_script_path + os.path.sep
output_directory = f"{Base_directory}../glassdoor-scrap-jobs-data/"
output_file_link = f"{output_directory}job_listings_glassdoor.json"
app = Flask(__name__)
expectedToken="MyTokenSecure123"

# Decorator to check for the mandatory header
def require_id_connect_header(expected_value):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if 'id-connect' not in request.headers or request.headers['id-connect'] != expected_value:
                return jsonify({'error': 'You are not authorized'}), 404
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


# Apply the decorator to your endpoint
@app.route('/get_glassdoor_jobs')
@require_id_connect_header(expected_value=expectedToken)
def read_glassdoor_jobs():
    try:  
        with open(output_file_link, "r") as f:
            job_listing_loaded = json.load(f) 
            return jsonify({'message': job_listing_loaded})
    except Exception as e:
        print("Could not read the file job_listings_glassdoor.json", e)
        return jsonify({'message': f'Could not read the job file : {e}'})
    
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)