from app import db
from sqlalchemy.dialects.postgresql import JSON


class Map_user_proj(db.Model):
    map_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    p_id = db.Column(db.Integer)
    user_role = db.Column(db.String)
    user_assign_date = db.Column(db.String(20))
    user_end_date = db.Column(db.String(20))


    def __init__(self, user_id, p_id, user_role, user_assign_date, user_end_date):
        self.p_id = p_id
        self.user_id = user_id
        self.user_role = user_role
        self.user_assign_date = user_assign_date
        self.user_end_date = user_end_date


    def __repr__(self):
        return '<id {}>'.format(self.map_id)

    def json_format(self):
        return {
            "map_id":self.map_id,
            "p_id":self.p_id,
            "user_id":self.user_id,
            "user_role":self.user_role,
            "user_assign_date":self.user_assign_date,
            "user_end_date":self.user_end_date
        
        }


    def insert(self):
        db.session.add(self)
        db.session.commit()
        

    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()