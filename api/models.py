from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'active': self.active,
            'expiration_date': self.expiration_date.isoformat(),
            'subscription_type': self.subscription_type,
            'support_name': self.support_name,
            'device_id': self.device_id,
            'activated': self.activated,
            'key_type': self.key_type,
            'multi_device': self.multi_device
        }
