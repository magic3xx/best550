from flask import Flask, jsonify, send_from_directory
from .config import Config
from .models import db
from .routes import api
import os

def create_app():
    app = Flask(__name__, static_folder='../dist')
    app.config.from_object(Config)
    
    db.init_app(app)
    
    # Ensure the database directory exists
    os.makedirs('/tmp', exist_ok=True)
    
    # Create tables within application context
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Database initialization error: {str(e)}")
    
    app.register_blueprint(api, url_prefix='/api')
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
