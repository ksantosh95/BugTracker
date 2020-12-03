from flask import Flask, jsonify, render_template, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from os import environ as env
import constants
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/bugtrackerdb"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = "asdfsdfsd"


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')
    return response

AUTH0_DOMAIN = 'ksantosh95.us.auth0.com'
AUTH0_CLIENT_ID = 'ui6xQlOy9NVhh31d0w8UvPjSpaMrZKLS'
AUTH0_CALLBACK_URL= 'http://127.0.0.1:5000/callback'

AUTH0_CLIENT_SECRET = 'RgE624251yW7O3WBEbYCR3DAB-q0IEk-L-Q1-jqM9_5q7dELbzYvzEbkwUxGayBp'
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = 'bugTracker'

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)



@app.route("/", methods=["GET"])
def login():
    
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('login', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


from models.TicketModel import Ticket
from models.EmployeeModel import Employee
from models.ProjectModel import Project
from models.EmpProjMapModel import Map_emp_proj


from controllers import UserController




@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    
    session['profile'] = {
       'name': userinfo['name'],
       'nickname' : userinfo['nickname']
    }
    return redirect('/tickets')





@app.errorhandler(500)
def error_500(error):
    return jsonify({
    'success': False,
    'error': 500,
    'message': 'Server side error'
    }), 500


if __name__ == '__main__':
    app.run()