from flask import Flask, jsonify
from flask_cors import CORS
from grid_wit.api.routes import api
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    
    # Add root route
    @app.route('/')
    def home():
        return jsonify({
            "message": "Welcome to the Crossword API",
            "status": "ok",
            "documentation": "/api/"
        })
    
    return app