from flask import Flask, jsonify, render_template, redirect
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

AUTH0_DOMAIN = 'ksantosh95.us.auth0.com'
API_AUDIENCE = 'bugTracker'
AUTH0_CLIENT_ID = 'ui6xQlOy9NVhh31d0w8UvPjSpaMrZKLS'
AUTH0_CALLBACK_URL= 'http://127.0.0.1:5000/tickets'

@app.route("/", methods=["GET"])
def generate_auth_url():
    
    url = f'https://{AUTH0_DOMAIN}/authorize' \
            f'?audience={API_AUDIENCE}' \
            f'&response_type=token&client_id=' \
            f'{AUTH0_CLIENT_ID}&redirect_uri=' \
            f'{AUTH0_CALLBACK_URL}'

    return redirect(url)



from models.TicketModel import Ticket

from controllers import UserController

@app.route("/createticket")
def createticket():
    return render_template('ticketform.html')

@app.route("/tickets")
def tickets():
    return render_template('tickets.html')

@app.errorhandler(500)
def error_500(error):
    return jsonify({
    'success': False,
    'error': 500,
    'message': 'Server side error'
    }), 500


if __name__ == '__main__':
    app.run()