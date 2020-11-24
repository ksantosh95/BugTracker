from app import db
from sqlalchemy.dialects.postgresql import JSON


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    phone = db.Column(db.Integer)


    def __init__(self, name, phone):
        self.name = name
        self.phone = phone

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def format(self):
        return {
            "id":self.id,
            "name":self.name,
            "phone":self.phone
        }