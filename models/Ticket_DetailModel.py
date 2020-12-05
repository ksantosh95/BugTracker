from app import db
from sqlalchemy.dialects.postgresql import JSON


class Ticket_detail(db.Model):
    t_detail_id = db.Column(db.Integer, primary_key=True)
    t_id = db.Column(db.Integer)
    emp_id = db.Column(db.String(40))
    t_status = db.Column(db.String(10))
    t_update_date = db.Column(db.String(20))
    t_comment = db.Column(db.String(100))


    def __init__(self, t_id, emp_id, t_status, t_update_date, t_comment):
        self.t_id = t_id
        self.emp_id = emp_id
        self.t_status = t_status
        self.t_update_date = t_update_date
        self.t_comment = t_comment


    def __repr__(self):
        return '<id {}>'.format(self.t_detail_id)

    def json_format(self):
        return {
            "id":self.t_id,
            "emp_id":self.emp_id,
            "status":self.t_status,
            "update_date":self.t_update_date,
            "comment":self.t_comment  
        }


    def insert(self):
        db.session.add(self)
        db.session.commit()
        

    def update(self):
        db.session.commit()