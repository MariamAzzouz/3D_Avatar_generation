from app2.config import db
import json

class Avatar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    measurements_json = db.Column(db.Text)  # Stored as JSON string
    customizations_json = db.Column(db.Text)  # Stored as JSON string
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.measurements_json = '{}'
        self.customizations_json = '{}'
    
    def get_measurements(self):
        return json.loads(self.measurements_json) if self.measurements_json else {}
    
    def set_measurements(self, value):
        self.measurements_json = json.dumps(value)
    
    def get_customizations(self):
        return json.loads(self.customizations_json) if self.customizations_json else {}
    
    def set_customizations(self, value):
        self.customizations_json = json.dumps(value)
    
    # Define relationships
    user = db.relationship('User', backref=db.backref('avatar', lazy=True, uselist=False)) 