from app import db
from sqlalchemy.dialects.postgresql import JSON


class Notification(db.Model):
    n_id = db.Column(db.Integer, primary_key=True)
    t_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    n_type = db.Column(db.String)

    def __init__(self, t_id, user_id, n_type):
        self.t_id = t_id
        self.user_id = user_id
        self.n_type = n_type



    def __repr__(self):
        return '<id {}>'.format(self.n_id)

    def json_format(self):
        return {
            "n_id":self.n_id,
            "t_id":self.t_id,
            "user_id":self.user_id,
            "n_type":self.n_type,
        
        }



    def insert(self):
        db.session.add(self)
        db.session.commit()
        

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()