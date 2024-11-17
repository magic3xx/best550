from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import os
import logging
from .models import db, License

app = Flask(__name__, static_folder='.')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure database
database_url = os.environ.get('DATABASE_URL')
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///licenses.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path == "":
        path = "index.html"
    try:
        return send_from_directory('.', path)
    except Exception:
        return send_from_directory('.', 'index.html')

@app.route('/api/licenses', methods=['GET'])
def list_licenses():
    try:
        logger.info("Attempting to fetch licenses")
        licenses = License.query.all()
        logger.info(f"Successfully fetched {len(licenses)} licenses")
        return jsonify([{
            'id': license.id,
            'key': license.key,
            'active': license.active,
            'expiration_date': license.expiration_date.isoformat(),
            'subscription_type': license.subscription_type,
            'support_name': license.support_name,
            'device_id': license.device_id,
            'activated': license.activated,
            'key_type': license.key_type,
            'multi_device': license.multi_device
        } for license in licenses])
    except Exception as e:
        logger.error(f"Error fetching licenses: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_license', methods=['POST'])
def add_license():
    try:
        logger.info("Received add license request")
        data = request.json
        now = datetime.now()
        
        if data['subscription_type'] == "1 Week":
            expiration_date = now + timedelta(weeks=1)
        elif data['subscription_type'] == "1 Month":
            expiration_date = now + timedelta(days=30)
        elif data['subscription_type'] == "3 Months":
            expiration_date = now + timedelta(days=90)
        elif data['subscription_type'] == "6 Months":
            expiration_date = now + timedelta(days=180)
        elif data['subscription_type'] == "1 Year":
            expiration_date = now + timedelta(days=365)
        else:
            days = int(data.get('days', 0))
            hours = int(data.get('hours', 0))
            expiration_date = now + timedelta(days=days, hours=hours)

        new_license = License(
            key=data['key'],
            expiration_date=expiration_date,
            subscription_type=data['subscription_type'],
            support_name=data.get('support_name', ''),
            key_type=data['key_type'],
            multi_device=data.get('multi_device', False)
        )
        
        db.session.add(new_license)
        db.session.commit()
        logger.info(f"Successfully added license with key: {data['key']}")
        return jsonify({'message': 'License added successfully'}), 201
    except Exception as e:
        logger.error(f"Error adding license: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/toggle_active/<int:id>', methods=['POST'])
def toggle_active(id):
    try:
        logger.info(f"Attempting to toggle license with id: {id}")
        license = License.query.get(id)
        if license:
            license.active = not license.active
            db.session.commit()
            logger.info(f"Successfully toggled license with id: {id}")
            return jsonify({'message': 'License status toggled successfully'}), 200
        return jsonify({'message': 'License not found'}), 404
    except Exception as e:
        logger.error(f"Error toggling license: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_license/<int:id>', methods=['DELETE'])
def delete_license(id):
    try:
        logger.info(f"Attempting to delete license with id: {id}")
        license = License.query.get(id)
        if license:
            db.session.delete(license)
            db.session.commit()
            logger.info(f"Successfully deleted license with id: {id}")
            return jsonify({'message': 'License deleted successfully'}), 200
        return jsonify({'message': 'License not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting license: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset_key', methods=['POST'])
def reset_key():
    try:
        data = request.json
        logger.info(f"Attempting to reset key: {data['key']}")
        license = License.query.filter_by(key=data['key']).first()
        if license:
            license.device_id = None
            license.activated = False
            db.session.commit()
            logger.info(f"Successfully reset key: {data['key']}")
            return jsonify({'message': 'Key reset successfully'}), 200
        return jsonify({'message': 'License not found'}), 404
    except Exception as e:
        logger.error(f"Error resetting key: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/check_key_details', methods=['POST'])
def check_key_details():
    try:
        data = request.json
        logger.info(f"Checking key details for: {data['key']}")
        license = License.query.filter_by(key=data['key']).first()
        
        if license:
            if license.activated and not license.multi_device and license.device_id != data['device_id']:
                logger.warning(f"Key {data['key']} is already used on another device")
                return jsonify({'valid': False, 'reason': 'This key is already used on another device.'})

            if not license.activated or license.multi_device:
                if not license.multi_device:
                    license.device_id = data['device_id']
                license.activated = True
                db.session.commit()

            if license.active and license.expiration_date > datetime.now():
                remaining_time = license.expiration_date - datetime.now()
                remaining_minutes = (remaining_time.days * 24 * 60) + (remaining_time.seconds // 60)

                logger.info(f"Successfully validated key: {data['key']}")
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
            logger.warning(f"Key {data['key']} is inactive or expired")
            return jsonify({'valid': False, 'reason': 'The key is either inactive or expired.'})
        logger.warning(f"Key not found: {data['key']}")
        return jsonify({'valid': False, 'reason': 'Key not found.'})
    except Exception as e:
        logger.error(f"Error checking key details: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
