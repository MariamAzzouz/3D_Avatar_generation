from app.config import db
import json

class Avatar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    measurements = db.Column(db.Text)  # Stored as JSON string
    customizations = db.Column(db.Text)  # Stored as JSON string
    
    def __init__(self, user_id):
        self.user_id = user_id
    
    @property
    def measurements_dict(self):
        return json.loads(self.measurements) if self.measurements else {}
    
    @measurements.setter
    def measurements(self, value):
        self.measurements = json.dumps(value)
    
    @property
    def customizations_dict(self):
        return json.loads(self.customizations) if self.customizations else {}
    
    @customizations.setter
    def customizations(self, value):
        self.customizations = json.dumps(value) 
