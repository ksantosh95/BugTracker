from flask import Flask, jsonify, render_template, redirect, session, url_for, abort
from flask_sqlalchemy import SQLAlchemy
import os,sys
from os import environ as env
import constants
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

app = Flask(__name__, template_folder='template')
#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/bugtrackerdb"
# FOR HEROKU DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
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
    client_id= AUTH0_CLIENT_ID,
    client_secret= AUTH0_CLIENT_SECRET,
    api_base_url= AUTH0_BASE_URL,
    access_token_url= AUTH0_BASE_URL + '/oauth/token',
    authorize_url= AUTH0_BASE_URL + '/authorize',
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
from models.Ticket_HistoryModel import Ticket_history
from models.UsersModel import Users
from models.ProjectModel import Project
from models.UserProjMapModel import Map_user_proj
from models.CommentModel import Comment
from models.NotificationModel import Notification
from models.MonthConfigModel import Month_config


from controllers import UserController
from controllers import DeveloperController
from controllers import TicketController
from controllers import CommentController
from controllers import ProjectController
from controllers import NotificationController
from controllers import AdminController
from controllers import ManagerController

@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    try :
        role = Users.query.with_entities(Users.user_role).filter_by(user_email = userinfo['name']).one()
        user_id = Users.query.with_entities(Users.user_id).filter_by(user_email = userinfo['name']).one()
    except:
        print(sys.exc_info())
        abort(500)

    session['profile'] = {
       'name': userinfo['name'],
       'nickname' : userinfo['nickname'],
       'role' : role[0],
       'email': userinfo['email'],
       'user_id' : user_id[0]
    }
    return redirect('/landing')

@app.route('/landing')
def redirect_users():
    userinfo = session.get('profile')
    if userinfo['role']== 'Developer':
          return redirect('/tickets')
    elif userinfo['role'] == 'User':
        return redirect('/tickets')
    elif userinfo['role']== 'Admin': 
        return redirect("/admin/user-list")
    elif userinfo['role']== 'Project Manager': 
        return redirect("/manager-dashboard")
    return ""



@app.errorhandler(500)
def error_500(error):
    userinfo = session.get('profile')
    notification_list = NotificationController.get_notifications(userinfo['user_id'])
    notification_count = len(notification_list)
    data = {
        "userinfo" : userinfo,
        "user_id": userinfo['user_id'],
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "Unauthorized",
        "error" : "500",
        "notification" : notification_list,
        "notification_count" : notification_count,
    }
    return render_template('Unauthorized.html', data = data)



@app.errorhandler(404)
def error_404(error):
    userinfo = session.get('profile')
    notification_list = NotificationController.get_notifications(userinfo['user_id'])
    notification_count = len(notification_list)
    data = {
        "userinfo" : userinfo,
        "user_id": userinfo['user_id'],
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "Unauthorized",
        "error" : "404",
        "notification" : notification_list,
        "notification_count" : notification_count,
    }
    return render_template('Unauthorized.html', data = data)


@app.errorhandler(401)
def error_401(error):
    userinfo = session.get('profile')
    notification_list = NotificationController.get_notifications(userinfo['user_id'])
    notification_count = len(notification_list)

    data = {
        "userinfo" : userinfo,
        "user_id": userinfo['user_id'],
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "Unauthorized",
        "error" : "401",
        "notification" : notification_list,
        "notification_count" : notification_count,
    }
    return render_template('Unauthorized.html', data = data)


@app.errorhandler(403)
def error_403(error):
    userinfo = session.get('profile')
    notification_list = NotificationController.get_notifications(userinfo['user_id'])
    notification_count = len(notification_list)

    data = {
        "userinfo" : userinfo,
        "user_id": userinfo['user_id'],
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "Unauthorized",
        "error" : "403",
        "notification" : notification_list,
        "notification_count" : notification_count,
    }
    return render_template('Unauthorized.html', data = data)

if __name__ == '__main__':
    app.run()