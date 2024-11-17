from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configure database
database_url = os.environ.get('DATABASE_URL')
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///licenses.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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

@app.route('/api/licenses', methods=['GET'])
def list_licenses():
    try:
        licenses = License.query.all()
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_license', methods=['POST'])
def add_license():
    try:
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
        return jsonify({'message': 'License added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/toggle_active/<int:id>', methods=['POST'])
def toggle_active(id):
    try:
        license = License.query.get(id)
        if license:
            license.active = not license.active
            db.session.commit()
            return jsonify({'message': 'License status toggled successfully'}), 200
        return jsonify({'message': 'License not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_license/<int:id>', methods=['DELETE'])
def delete_license(id):
    try:
        license = License.query.get(id)
        if license:
            db.session.delete(license)
            db.session.commit()
            return jsonify({'message': 'License deleted successfully'}), 200
        return jsonify({'message': 'License not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset_key', methods=['POST'])
def reset_key():
    try:
        data = request.json
        license = License.query.filter_by(key=data['key']).first()
        if license:
            license.device_id = None
            license.activated = False
            db.session.commit()
            return jsonify({'message': 'Key reset successfully'}), 200
        return jsonify({'message': 'License not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check_key_details', methods=['POST'])
def check_key_details():
    try:
        data = request.json
        license = License.query.filter_by(key=data['key']).first()
        
        if license:
            if license.activated and not license.multi_device and license.device_id != data['device_id']:
                return jsonify({'valid': False, 'reason': 'This key is already used on another device.'})

            if not license.activated or license.multi_device:
                if not license.multi_device:
                    license.device_id = data['device_id']
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
            return jsonify({'valid': False, 'reason': 'The key is either inactive or expired.'})
        return jsonify({'valid': False, 'reason': 'Key not found.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
