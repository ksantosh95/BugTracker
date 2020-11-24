from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Result


@app.route('/')
def insert():
    try:
        entry = Result("xyz",987)
        db.session.add(entry)
        db.session.commit()
    except:
        db.session.rollback()
        print("error")
    finally:
        db.session.close()
        print("closed")
        return ""

    


@app.route('/temp')
def retrieve():
    res = Result.query.all()
    res = [r.format() for r in res]
    return jsonify(res)

    


if __name__ == '__main__':
    app.run()