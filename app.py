from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/bugtrackerdb"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')
    return response



from models.TicketModel import Ticket

from controllers import SubmitterController

@app.route("/asd")
def test():
    return render_template('TicketForm.html')


@app.errorhandler(500)
def error_500(error):
    return jsonify({
    'success': False,
    'error': 500,
    'message': 'Server side error'
    }), 500


if __name__ == '__main__':
    app.run()