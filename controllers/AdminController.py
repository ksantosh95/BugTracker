#################################################################################################
#                                                                                               #
#   Module          :   Admin Controller                                                        #
#   Operations      :                                                                           #
#   1.  Fetch user list             /admin/user-list                                Admin       #    
#   2.  Fetch info for              /admin/create-user                              Admin       #
#       creating new user                                                                       #
#   3.  Submit New User             /admin/user-submit                              Admin       #
#   4.  Fetch existing info         /admin/edit-user/<int:user_id>                  Admin       #
#       for user                                                                                #
#   5.  Update user info            /admin/user-update                              Admin       #
#   6.  Delete user                 /admin/delete-user/<int:user_id>                Admin       #
#   7.  Assign user to project      /admin/assign-user-project                      Admin       #  
#   8.  Delete project for a user   /admin/delete-project-user/                     Admin       #
#   9.  Delete user from a project  /admin/delete-project-user-project-details/     Admin       #
#   10. List of all projects        /admin/projects                                 Admin       #
#   11. List of all tickets         /admin/tickets                                  Admin       #
#   12. Delete ticket               /admin/delete-ticket/<int:ticket_id>            Admin       #
#   13. Fetch info for ticket       /admin/edit-ticket/<int:ticket_id>              Admin       #  
#   Last Update     :    Added function for updating tickets                                    #
#   Last Update date:   21 Dec 2020                                                             #
#                                                                                               #
#################################################################################################

from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session
from app import app, db
import os, sys
from datetime import date
from sqlalchemy import text
from datetime import datetime
import constants
from models.TicketModel import Ticket
from models.ProjectModel import Project
from models.UserProjMapModel import Map_user_proj
from models.UsersModel import Users

from controllers import NotificationController


############################################# 1 #################################################
#   USER MANAGEMENT :   Get list of all user accounts                                           #
################################################################################################# 
@app.route('/admin/user-list', methods=['GET'])
def admin_get_users():
    userinfo = session.get('profile')
    user_list = Users.query.filter(Users.user_role != "Admin").all()
    user = [Users.json_format(u) for u in user_list]  
    data = {
        "user" : user,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "user-list",
        "userinfo" : userinfo
    }
    return render_template('admin-mainpage.html', data = data)


############################################# 2 #################################################
#   USER CREATION   :   Create a new user                                                       #
#################################################################################################
@app.route("/admin/create-user")
def create_user():
    userinfo = session.get('profile')  
    project_name_list = Project.query.all()
    project_name_list_json = [Project.json_format(row) for row in project_name_list]
    data = {
        "project" : project_name_list_json,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page": "create-user"
    }
    return render_template('userform.html', data = data)

############################################# 3 #################################################
#   SUBMIT USER :   Submit user information                                                     #
#   Algorithm   :   1.  Read input values from the form                                         #
#                   2.  Update user info in the USER table                                      #
#                   3.  Update project and user role in the User-Project mapping table          #
#   Routing     :   Admin submits form ->   User created    ->  Admin user list page            #
#################################################################################################
@app.route("/admin/user-submit", methods=['POST'])
def submit_user():
    user_name = request.form.get('user_name')
    user_email = request.form.get('user_email')
    user_role = request.form.get('user_role')
    project_id = request.form.get('project')
    user_pwd = "bugTracker123"
    today = date.today()
    update_date = today.strftime("%d/%m/%Y")
   
    user_entry = Users(user_name, user_email,user_pwd, user_role, update_date)
    try:
        user_entry.insert()
    except:
        print(sys.exc_info())
        abort(500)

    map_entry = Map_user_proj(user_entry.user_id, project_id, user_role, update_date, "")
    try:
        map_entry.insert()
    except:
        print(sys.exc_info())
        abort(500)

    return redirect("/admin/user-list")

############################################# 4 #################################################
#   EDIT USER INFO  :   Get existing user info the USER ID                                      #
#   Algorithm       :   1.  Fetch User data from USER table for user id                         #
#                       2.  Fetch Project Name for the user based on the user-project map       #
#################################################################################################
@app.route("/admin/edit-user/<int:user_id>")
def get_user_info(user_id):
    userinfo = session.get('profile')  
    user_entry = Users.query.get(user_id)
    user = Users.json_format(user_entry)
    project = Project.query.join(Map_user_proj, Project.p_id == Map_user_proj.p_id)\
                .add_columns(Project.p_name, Project.p_id)\
                    .filter(Map_user_proj.user_id == user_id)
 
    project_name_list = Project.query.all()
    project_name_list_json = [Project.json_format(row) for row in project_name_list]

    data = {
        "project" : project_name_list_json,
        "userinfo" : userinfo,
        "user_project" : project,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "user": user,
        "page": "edit-user"
    }
    return render_template('userform.html', data = data)


############################################# 5 #################################################
#   USER UPDATE :   Update user information                                                     #
#################################################################################################
@app.route("/admin/user-update", methods=['POST'])
def update_user():
    user_id = request.form.get('user_id')
    user = Users.query.get(user_id)
    user.user_name = request.form.get('user_name')
    user.user_role = request.form.get('user_role')
    today = date.today()
    update_date = today.strftime("%d/%m/%Y")
    user.update_date = update_date
    user.update()
    return redirect("/admin/user-list")


############################################# 6 #################################################
#   DELETE USER                                                                                 #
#################################################################################################
@app.route("/admin/delete-user/<int:user_id>")
def delete_user(user_id):
    user = Users.query.get(user_id)
    try:
        user.delete()
    except:
        print(sys.exc_info())
        abort(500)
    return redirect("/admin/user-list")

@app.route("/admin/userdetails/<int:user_id>")
def get_user_history(user_id):
    userinfo = session.get('profile')
    userentry = Users.query.get(user_id)
    user = Users.json_format(userentry)
    user_project_list = Project.query.join(Map_user_proj, Project.p_id == Map_user_proj.p_id)\
                    .add_columns(Project.p_id, Project.p_name)\
                        .filter(Map_user_proj.user_id == user_id)

    project_name_list = Project.query.all()
    project_name_list_json = [Project.json_format(row) for row in project_name_list]

    user_role = user['role']
    user_email = user['email']
    if user_role == "Developer":
        ticket_list = Ticket.query.join(Project, Ticket.p_id == Project.p_id)\
                        .add_columns(Ticket.t_id, Ticket.t_title, Ticket.t_status,Project.p_name)\
                            .filter(Ticket.assigned_user_id == user_id)
    elif user_role == "User":
        ticket_list = Ticket.query.join(Project, Ticket.p_id == Project.p_id)\
                        .add_columns(Ticket.t_id, Ticket.t_title, Ticket.t_status, Project.p_name)\
                            .filter(Ticket.submitter_email == user_email)

    data = {
        "project" : project_name_list_json,
        "userinfo" : userinfo,
        "user_project" : user_project_list,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "user" : [user],
        "page": "user-details",
        "ticket": ticket_list
    }
    return render_template('user_details.html', data = data)

############################################# 7 #################################################
#   ASSIGN PROJECTS TO USER AND USER TO PROJECT                                                 #
#   Incoming call   :   1.  Assign Personnel button on User details page                        #
#                       2.  Assign Personnel button on Project details page                     #
#   Algorithm       :   1.  Read input values from the form                                     #
#                       2.  request.form.get('input') signifies whether the input instruction   #
#                            is to update or add the personnel.                                 #                       
#                       3.  If add, Insert information in User-project Mapping table            #
#                       4.  If update, fetch mapping entry and update                           #
#                       5.  Redirect to corresponding page                                      #
#   Routing         :   1.  User details    ->  add  ->  user details                           #
#                       2.  Project details ->  add/update  ->  project details                 #
#################################################################################################
@app.route("/admin/assign-user-project", methods=['POST'])
def assign_user_to_project():
    input_type= request.form.get('input')
    userinfo = session.get('profile')
    user_id = request.form.get('user_id')
    project_id = request.form.get('project')
    role = request.form.get('role')
    page = request.form.get('page')
    today = date.today()
    update_date = today.strftime("%d/%m/%Y")

    if input_type == "Add":
        map_entry = Map_user_proj (user_id, project_id, role,update_date, "" )
        try:
            map_entry.insert()
        except:
            print(sys.exc_info())
            abort(500)
    elif input_type =="Update":
        map_entry = Map_user_proj.query.filter(Map_user_proj.user_id==user_id).filter(Map_user_proj.p_id == project_id).one()
        map_entry.user_role = role
        map_entry.update()
    if page == 'project-details':
        return redirect("/projectdetails/" + project_id)
    else:
        return redirect("/admin/userdetails/" + user_id)

############################################# 8 #################################################
#   DELETE USER  FROM A PROJECT                                                                 #
#   Incoming call   :   User details Page                                                       #
#################################################################################################
@app.route("/admin/delete-project-user/")
def delete_project_user():
    user_id = request.args.get('user_id')
    project_id = request.args.get('project_id')
    map= Map_user_proj.query.filter(Map_user_proj.user_id == user_id).filter(Map_user_proj.p_id == project_id).one()
    map.delete()
    return redirect("/admin/userdetails/" + user_id)

############################################# 9 #################################################
#   DELETE USER FROM PROJECT                                                                    #
#   Incoming call   :   Project Details Page                                                    #
#################################################################################################
@app.route("/admin/delete-project-user-project-details/")
def delete_project_user_projectdetails():
    user_id = request.args.get('user_id')
    project_id = request.args.get('project_id')
    map= Map_user_proj.query.filter(Map_user_proj.user_id == user_id).filter(Map_user_proj.p_id == project_id).one()
    map.delete()
    return redirect("/projectdetails/" + project_id)

############################################# 10 ################################################
#   FETCH ALL PROJECTS LIST                                                                     #
#   Output  :   Admin main page - projects tab                                                  #
#################################################################################################
@app.route('/admin/projects', methods=['GET'])
def admin_get_projects():
    userinfo = session.get('profile')
    project_list = Project.query.all()
    project = [Project.json_format(proj) for proj in project_list]  
    data = {
        "project" : project,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "projects",
        "userinfo" : userinfo
    }
    return render_template('admin-mainpage.html', data = data)


############################################# 11 ################################################
#   FETCH ALL TICKETS                                                                           #
#   Output  :   Admin main page - tickets tab                                                   #
#################################################################################################
@app.route('/admin/tickets', methods=['GET'])
def admin_get_tickets():
    userinfo = session.get('profile')
    ticket_value = Ticket.query.all()
    ticket_value = [t.json_format() for t in ticket_value]
    data = {
        "ticket" : ticket_value,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "tickets",
        "userinfo" : userinfo
    }
    return render_template('admin-mainpage.html', data = data)


############################################# 12 ################################################
#   DELETE TICKET                                                                               #
#################################################################################################
@app.route("/admin/delete-ticket/<int:ticket_id>")
def admin_delete_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    try:
        ticket.delete()
    except:
        print(sys.exc_info())
        abort(500)
    return redirect("/admin/tickets")

############################################# 13 ################################################
#   EDIT TICKET     :   Get existing ticket information for editing                             #
#   Incoming call   :   Edit button on Ticket details page                                      #
#   Output          :   Ticketform.html with prefilled ticket information                       #
#################################################################################################
@app.route("/admin/edit-ticket/<int:ticket_id>")
def get_ticket_info(ticket_id):
    userinfo = session.get('profile')  
    ticket_json = Ticket.query.get(ticket_id)
    ticket = Ticket.json_format(ticket_json) 
    project = Project.query.get(ticket_json.p_id)
    project_name_list = Project.query.all()
    project_name_list_json = [Project.json_format(row) for row in project_name_list]
    priority_array = constants.PRIORITY
    status_array = constants.STATUS
    data = {
        "project" : project_name_list_json,
        "userinfo" : userinfo,
        "user_project" : project,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "ticket": ticket,
        "page": "edit-ticket",
        "priority_array": priority_array,
        "status_array":status_array
    }
    return render_template('ticketform.html', data = data)