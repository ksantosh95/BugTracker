from app import db
from sqlalchemy.dialects.postgresql import JSON


class Month_config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mth_id = db.Column(db.Integer)
    mth_name = db.Column(db.String(40))
    year = db.Column(db.Integer)


    def __init__(self, mth_id, mth_name, year):
        self.mth_id = mth_id
        self.mth_name = mth_name
        self.year = year



    def __repr__(self):
        return '<id {}>'.format(self.user_id)

    def json_format(self):
        return {
            "mth_name":self.mth_name,
            "p_id":self.p_id,
            "cnt":self.cnt
        }
    
    def piechart_json(self):
        return {
            "priority":self.priority,
            "cnt":self.cnt
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()
        

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

