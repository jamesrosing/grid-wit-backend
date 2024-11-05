from flask import Flask, jsonify
from flask_cors import CORS
from grid_wit.api.routes import api
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Crossword API",
        "status": "ok",
        "documentation": "/api/"
    })

if __name__ == "__main__":
    logger.info("Starting Crossword Puzzle API in development mode...")
    # Use environment variable for port with fallback to 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    ) 