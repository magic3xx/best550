import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure logging
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
else:
    app.logger.setLevel(logging.INFO)

# Get the DATABASE_URL from environment variable
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # If it starts with postgres://, replace it with postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # If DATABASE_URL is not set, use a default SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///licenses.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class License(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)
    expiration_date = db.Column(db.DateTime, nullable=False)
    subscription_type = db.Column(db.String(20), nullable=False)
    support_name = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    activated = db.Column(db.Boolean, default=False)
    key_type = db.Column(db.String(20), nullable=False)
    multi_device = db.Column(db.Boolean, default=False)


@app.route('/')
def serve_app():
    return send_from_directory('.', 'index.html')

@app.route('/api/licenses', methods=['GET'])
def list_licenses():
    try:
        app.logger.info("Attempting to fetch licenses")
        licenses = License.query.all()
        app.logger.info(f"Successfully fetched {len(licenses)} licenses")
        return jsonify([{
            'id': license.id,
            'key': license.key,
            'active': license.active,
            'expiration_date': license.expiration_date.isoformat(),
            'subscription_type': license.subscription_type,
            'support_name': license.support_name,
            'device_id': license.device_id,
            'activated': license.activated,
            'key_type': license.key_type
        } for license in licenses])
    except Exception as e:
        app.logger.error(f"Error fetching licenses: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_license', methods=['POST'])
def add_license():
    data = request.json
    key = data['key']
    subscription_type = data['subscription_type']
    support_name = data['support_name']
    key_type = data['key_type']
    multi_device = data.get('multi_device', False)

    # Calculate expiration date based on subscription type
    now = datetime.now()
    if subscription_type == "1 Week":
        expiration_date = now + timedelta(weeks=1)
    elif subscription_type == "1 Month":
        expiration_date = now + timedelta(days=30)  # Assuming 30 days for a month
    elif subscription_type == "3 Months":
        expiration_date = now + timedelta(days=90)
    elif subscription_type == "6 Months":
        expiration_date = now + timedelta(days=180)
    elif subscription_type == "1 Year":
        expiration_date = now + timedelta(days=365)
    else:
        # For custom durations, use the provided days and hours
        days = int(data['days'])
        hours = int(data['hours'])
        expiration_date = now + timedelta(days=days, hours=hours)

    new_license = License(
        key=key,
        expiration_date=expiration_date,
        subscription_type=subscription_type,
        support_name=support_name,
        key_type=key_type,  # Added comma here
        multi_device=multi_device 
    )

    db.session.add(new_license)
    db.session.commit()

    return jsonify({'message': 'License added successfully'}), 201

@app.route('/api/toggle_active/<int:id>', methods=['POST'])
def toggle_active(id):
    license = License.query.get(id)
    if license:
        license.active = not license.active
        db.session.commit()
        return jsonify({'message': 'License status toggled successfully'}), 200
    return jsonify({'message': 'License not found'}), 404

@app.route('/api/delete_license/<int:id>', methods=['DELETE'])
def delete_license(id):
    license = License.query.get(id)
    if license:
        db.session.delete(license)
        db.session.commit()
        return jsonify({'message': 'License deleted successfully'}), 200
    return jsonify({'message': 'License not found'}), 404

@app.route('/api/reset_key', methods=['POST'])
def reset_key():
    data = request.json
    key = data['key']
    license = License.query.filter_by(key=key).first()
    if license:
        license.device_id = None
        license.activated = False
        db.session.commit()
        return jsonify({'message': 'Key reset successfully'}), 200
    return jsonify({'message': 'License not found'}), 404

@app.route('/api/check_key_details', methods=['POST'])
def check_key_details():
    app.logger.info(f"Received key activation request: {request.json}")
    data = request.json
    key = data.get('key')
    device_id = data.get('device_id')

    license = License.query.filter_by(key=key).first()
    if license:
        if license.activated and not license.multi_device and license.device_id != device_id:
            return jsonify({'valid': False, 'reason': 'This key is already used on another device.'})

        if not license.activated or license.multi_device:
            if not license.multi_device:
                license.device_id = device_id
            license.activated = True
            db.session.commit()

        if license.active and license.expiration_date > datetime.now():
            remaining_time = license.expiration_date - datetime.now()
            remaining_minutes = (remaining_time.days * 24 * 60) + (remaining_time.seconds // 60)

            return jsonify({
                'valid': True,
                'expiration_date': license.expiration_date.strftime('%Y-%m-%d'),
                'subscription_type': license.subscription_type,
                'support_name': license.support_name,
                'remaining_time': {
                    'days': remaining_time.days,
                    'hours': remaining_time.seconds // 3600,
                    'minutes': remaining_minutes % 60
                },
                'multi_device': license.multi_device
            })
        else:
            return jsonify({'valid': False, 'reason': 'The key is either inactive or expired.'})

    return jsonify({'valid': False, 'reason': 'Key not found.'})

@app.route('/api/run_migrations', methods=['GET'])
def run_migrations():
    try:
        app.logger.info("Starting database migrations")
        with app.app_context():
            db.create_all()
        app.logger.info("Database migrations completed successfully")
        return jsonify({'message': 'Migrations completed successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error during migrations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug', methods=['GET'])
def debug_info():
    try:
        app.logger.info("Fetching debug info")
        engine = db.get_engine()
        inspector = db.inspect(engine)
        tables = inspector.get_table_names()
        app.logger.info(f"Tables in database: {tables}")
        return jsonify({
            'database_url': app.config['SQLALCHEMY_DATABASE_URI'],
            'tables': tables,
            'app_config': {k: str(v) for k, v in app.config.items() if k != 'SQLALCHEMY_DATABASE_URI'}
        })
    except Exception as e:
        app.logger.error(f"Error fetching debug info: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
