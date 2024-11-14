import jobs_read_write
from flask import Flask, request, jsonify


app = Flask(__name__)
expectedToken = "MyTokenSecure123"


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
    jobs = jobs_read_write.read_glassdoor_jobs()
    return jsonify({'message': jobs})


@app.route('/get_linkedin_jobs')
@require_id_connect_header(expected_value=expectedToken)
def read_linkedin_jobs():
    jobs = jobs_read_write.read_linkedin_jobs()
    return jsonify({'message': jobs})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
