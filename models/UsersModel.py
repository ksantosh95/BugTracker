from app import db
from sqlalchemy.dialects.postgresql import JSON


class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(40))
    user_email = db.Column(db.String(40))
    user_pwd = db.Column(db.String(100))
    user_role = db.Column(db.String(20))
    update_date = db.Column(db.String(40))

    def __init__(self, user_id,user_name, user_email, user_pwd, user_role, update_date):
        self.user_id = user_id
        self.user_name = user_name
        self.user_email = user_email
        self.user_pwd = user_pwd
        self.user_role = user_role
        self.update_date = update_date


    def __repr__(self):
        return '<id {}>'.format(self.user_id)

    def json_format(self):
        return {
            "id":self.user_id,
            "name":self.user_name,
            "email":self.user_email,
            "role":self.user_role,
            "last_update_date":self.update_date
        
        }


    def insert(self):
        db.session.add(self)
        db.session.commit()
        

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()