from flask import Flask, jsonify, render_template, redirect, session, url_for, abort
from flask_sqlalchemy import SQLAlchemy
import os,sys
from os import environ as env
import constants
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

app = Flask(__name__, template_folder='template')
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/bugtrackerdb"
# FOR HEROKU DATABASE
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
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

AUTH0_DOMAIN = constants.AUTH0_DOMAIN
AUTH0_CLIENT_ID = constants.AUTH0_CLIENT_ID
AUTH0_CALLBACK_URL= constants.AUTH0_CALLBACK_URL
AUTH0_CLIENT_SECRET = constants.AUTH0_CLIENT_SECRET
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = constants.AUTH0_AUDIENCE

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
from models.Ticket_DetailModel import Ticket_detail
from models.EmployeeModel import Employee
from models.ProjectModel import Project
from models.EmpProjMapModel import Map_emp_proj


from controllers import UserController
from controllers import DeveloperController
from controllers import TicketController


@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    try :
        role = Employee.query.with_entities(Employee.emp_role).filter_by(emp_email = userinfo['name']).one()
    except:
        print(sys.exc_info())
        abort(500)

    session['profile'] = {
       'name': userinfo['name'],
       'nickname' : userinfo['nickname'],
       'role' : role
    }
    return redirect('/dev/tickets')





@app.errorhandler(500)
def error_500(error):
    return jsonify({
    'success': False,
    'error': 500,
    'message': 'Server side error'
    }), 500


if __name__ == '__main__':
    app.run()