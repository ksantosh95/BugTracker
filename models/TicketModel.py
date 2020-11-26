from app import db
from sqlalchemy.dialects.postgresql import JSON


class Ticket(db.Model):
    t_id = db.Column(db.Integer, primary_key=True)
    t_title = db.Column(db.String(40))
    t_desc = db.Column(db.String(100))
    emp_id = db.Column(db.Integer)
    submitter_id = db.Column(db.Integer)
    p_id = db.Column(db.Integer)
    t_priority = db.Column(db.String(40))
    t_status = db.Column(db.String(40))
    t_type = db.Column(db.String(40))
    t_create_date = db.Column(db.String(40))
    t_close_date = db.Column(db.String(40))

    def __init__(self, t_title, t_desc, emp_id, submitter_id, p_id, t_priority, t_status, t_type, t_create_date, t_close_date):
        self.t_title = t_title
        self.t_desc = t_desc
        self.emp_id = emp_id
        self.submitter_id = submitter_id
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
            "emp_id":self.emp_id,
            "submitter_id":self.submitter_id,
            "p_id":self.p_id,
            "priority":self.t_priority,
            "status":self.t_status,
            "type":self.t_type,
            "create_date":self.t_create_date,
            "close_date":self.t_close_date
        
        }


    def insert(self):
        db.session.add(self)
        db.session.commit()
        

    def update(self):
        db.session.commit()