from app import db
from sqlalchemy.dialects.postgresql import JSON


class Comment(db.Model):
    c_id = db.Column(db.Integer, primary_key=True)
    t_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    date = db.Column(db.String(20))
    comment = db.Column(db.String)



    def __init__(self,c_id, t_id, user_id, date, comment):
        self.c_id = c_id
        self.t_id = t_id
        self.user_id = user_id
        self.date = date
        self.comment = comment


    def __repr__(self):
        return '<id {}>'.format(self.c_id)

    def json_format(self):
        return {
            "ticket_id":self.t_id,
            "user_id":self.user_id,
            "date":self.date,
            "comment":self.comment
        }


    def insert(self):
        db.session.add(self)
        db.session.commit()
        

    def update(self):
        db.session.commit()