from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from .models import db, License

api = Blueprint('api', __name__)

@api.route('/licenses', methods=['GET'])
def list_licenses():
    try:
        licenses = License.query.all()
        return jsonify([license.to_dict() for license in licenses])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/add_license', methods=['POST'])
def add_license():
    try:
        data = request.json
        now = datetime.now()
        
        subscription_periods = {
            "1 Week": timedelta(weeks=1),
            "1 Month": timedelta(days=30),
            "3 Months": timedelta(days=90),
            "6 Months": timedelta(days=180),
            "1 Year": timedelta(days=365)
        }
        
        if data['subscription_type'] in subscription_periods:
            expiration_date = now + subscription_periods[data['subscription_type']]
        else:
            expiration_date = now + timedelta(
                days=int(data.get('days', 0)),
                hours=int(data.get('hours', 0))
            )

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
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/toggle_active/<int:id>', methods=['POST'])
def toggle_active(id):
    try:
        license = License.query.get_or_404(id)
        license.active = not license.active
        db.session.commit()
        return jsonify({'message': 'License status toggled successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/delete_license/<int:id>', methods=['DELETE'])
def delete_license(id):
    try:
        license = License.query.get_or_404(id)
        db.session.delete(license)
        db.session.commit()
        return jsonify({'message': 'License deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/reset_key', methods=['POST'])
def reset_key():
    try:
        data = request.json
        license = License.query.filter_by(key=data['key']).first_or_404()
        license.device_id = None
        license.activated = False
        db.session.commit()
        return jsonify({'message': 'Key reset successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/check_key_details', methods=['POST'])
def check_key_details():
    try:
        data = request.json
        license = License.query.filter_by(key=data['key']).first()
        
        if not license:
            return jsonify({'valid': False, 'reason': 'Key not found.'})

        if license.activated and not license.multi_device and license.device_id != data['device_id']:
            return jsonify({'valid': False, 'reason': 'This key is already used on another device.'})

        if not license.activated or license.multi_device:
            if not license.multi_device:
                license.device_id = data['device_id']
            license.activated = True
            db.session.commit()

        if not license.active or license.expiration_date <= datetime.now():
            return jsonify({'valid': False, 'reason': 'The key is either inactive or expired.'})

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
    except Exception as e:
        return jsonify({'error': str(e)}), 500
