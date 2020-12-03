from app import db
from sqlalchemy.dialects.postgresql import JSON


class Employee(db.Model):
    emp_id = db.Column(db.Integer, primary_key=True)
    emp_name = db.Column(db.String(40))
    emp_email = db.Column(db.String(40))
    emp_pwd = db.Column(db.String(100))
    emp_role = db.Column(db.String(20))
    update_date = db.Column(db.String(40))

    def __init__(self, emp_name, emp_email, emp_pwd, emp_role, update_date):
        self.emp_name = emp_name
        self.emp_email = emp_email
        self.emp_pwd = emp_pwd
        self.emp_role = emp_role
        self.update_date = update_date


    def __repr__(self):
        return '<id {}>'.format(self.emp_id)

    def json_format(self):
        return {
            "id":self.emp_id,
            "name":self.emp_name,
            "email":self.emp_email,
            "role":self.emp_role,
            "last_update_date":self.update_date
        
        }


    def insert(self):
        db.session.add(self)
        db.session.commit()
        

    def update(self):
        db.session.commit()