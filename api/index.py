from flask import Flask, jsonify
from .config import Config
from .models import db
from .routes import api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    app.register_blueprint(api, url_prefix='/api')
    
    @app.route('/')
    def home():
        return jsonify({"message": "License Manager API"})
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
