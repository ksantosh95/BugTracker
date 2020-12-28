from app import db
from sqlalchemy.dialects.postgresql import JSON


class Ticket_history(db.Model):
    t_history_id = db.Column(db.Integer, primary_key=True)
    t_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    t_status = db.Column(db.String(20))
    t_update_date = db.Column(db.String(20))
    t_priority = db.Column(db.String(20))


    def __init__(self, t_history_id,t_id, user_id, t_status, t_update_date, t_priority):
        self.t_history_id = t_history_id
        self.t_id = t_id
        self.user_id = user_id
        self.t_status = t_status
        self.t_update_date = t_update_date
        self.t_priority = t_priority


    def __repr__(self):
        return '<id {}>'.format(self.t_history_id)

    def json_format(self):
        return {
            "id":self.t_id,
            "user_id":self.user_id,
            "status":self.t_status,
            "update_date":self.t_update_date,
            "priority":self.t_priority  
        }


    def insert(self):
        db.session.add(self)
        db.session.commit()
        

    def update(self):
        db.session.commit()