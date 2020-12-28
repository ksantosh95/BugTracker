from app import db
from sqlalchemy.dialects.postgresql import JSON


class Ticket(db.Model):
    t_id = db.Column(db.Integer, primary_key=True)
    t_title = db.Column(db.String)
    t_desc = db.Column(db.String)
    assigned_user_id = db.Column(db.Integer)
    submitter_email = db.Column(db.String)
    p_id = db.Column(db.Integer)
    t_priority = db.Column(db.String(40))
    t_status = db.Column(db.String(40))
    t_type = db.Column(db.String(40))
    t_create_date = db.Column(db.String(40))
    t_close_date = db.Column(db.String(40))

    def __init__(self,t_id, t_title, t_desc, assigned_user_id, submitter_email, p_id, t_priority, t_status, t_type, t_create_date, t_close_date):
        self.t_id = t_id
        self.t_title = t_title
        self.t_desc = t_desc
        self.assigned_user_id = assigned_user_id
        self.submitter_email = submitter_email
        self.p_id = p_id
        self.t_priority = t_priority
        self.t_status = t_status
        self.t_type = t_type
        self.t_create_date = t_create_date
        self.t_close_date = t_close_date


    def __repr__(self):
        return '<id {}>'.format(self.t_id)

    def json_format(self):
        return {
            "id":self.t_id,
            "title":self.t_title,
            "desc":self.t_desc,
            "user_id":self.assigned_user_id,
            "submitter_email":self.submitter_email,
            "p_id":self.p_id,
            "priority":self.t_priority,
            "status":self.t_status,
            "type":self.t_type,
            "create_date":self.t_create_date,
            "close_date":self.t_close_date
        
        }

    def array_to_json_format(self):
        return {
            "id": self[0],
            "title":self[1],
            "desc":self[2],
            "user_id":self[3],
            "submitter_email":self[4],
            "p_id":self[5],
            "priority":self[6],
            "status":self[7],
            "type":self[8],
            "create_date":self[9],
            "close_date":self[10]
        }


    def insert(self):
        db.session.add(self)
        db.session.commit()
        

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()