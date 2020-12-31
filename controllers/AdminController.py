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
from sqlalchemy import text, func
from datetime import datetime
import constants
from models.TicketModel import Ticket
from models.ProjectModel import Project
from models.UserProjMapModel import Map_user_proj
from models.UsersModel import Users

from controllers import NotificationController


def is_valid_remove(user_id):
    if int(user_id) <= constants.DEMO_ADMIN_ID:
        return False
    return True

############################################# 1 #################################################
#   USER MANAGEMENT :   Get list of all user accounts                                           #
################################################################################################# 
@app.route('/admin/user-list', methods=['GET'])
def admin_get_users():
    userinfo = session.get('profile')
    if userinfo['role']!= 'Admin':
        abort(401)
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
    if userinfo['role']!= 'Admin':
        abort(401)
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
    #update_date = today.strftime("%d/%m/%Y")
    update_date= constants.CURRENT_DATE

    user_id = db.session.query(func.max(Users.user_id)).all()
    if user_id[0][0] == None:
        user_entry = Users(1, user_name, user_email,user_pwd, user_role, update_date)
    else:
        user_entry = Users(user_id[0][0] + 1, user_name, user_email,user_pwd, user_role, update_date)
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
    if userinfo['role']!= 'Admin':
        abort(401)
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
    #update_date = today.strftime("%d/%m/%Y")
    update_date =constants.CURRENT_DATE
    user.update_date = update_date
    user.update()
    return redirect("/admin/user-list")


############################################# 6 #################################################
#   DELETE USER                                                                                 #
#################################################################################################
@app.route("/admin/delete-user/<int:user_id>")
def delete_user(user_id):
    userinfo = session.get('profile')
    if user_id < 20 and userinfo['user_id'] == constants.DEMO_ADMIN_ID:
        abort(403)
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
    if userinfo['role']!= 'Admin':
        abort(401)
    userentry = Users.query.get(user_id)
    user = Users.json_format(userentry)
    user_project_list = Project.query.join(Map_user_proj, Project.p_id == Map_user_proj.p_id)\
                    .add_columns(Project.p_id, Project.p_name)\
                        .filter(Map_user_proj.user_id == user_id)


    sql = text("""select p_id,p_name,p_desc,p_start_date, p_end_date from project where p_id
                 not in (select p_id from map_user_proj where user_id ="""+str(user_id)+""")""")
    result = db.session.execute(sql)
    project_name_list = [row for row in result]
    project_name_list_json = [Project.json_format(p) for p in project_name_list]  


    ticket_list =""
    user_role = user['role']
    user_email = user['email']
    #For developer, get list of assigned tickets
    if user_role == "Developer":
        ticket_list = Ticket.query.join(Project, Ticket.p_id == Project.p_id)\
                        .add_columns(Ticket.t_id, Ticket.t_title, Ticket.t_status,Project.p_name)\
                            .filter(Ticket.assigned_user_id == user_id)
    #For user, get list of submitted tickets
    elif user_role == "User":
        ticket_list = Ticket.query.join(Project, Ticket.p_id == Project.p_id)\
                        .add_columns(Ticket.t_id, Ticket.t_title, Ticket.t_status, Project.p_name)\
                            .filter(Ticket.submitter_email == user_email)
    #For manager, get list of submitted tickets
    elif user_role == "Manager":
        ticket_list = Ticket.query.join(Project, Ticket.p_id == Project.p_id)\
                        .add_columns(Ticket.t_id, Ticket.t_title, Ticket.t_status, Project.p_name)\
                            .filter(Ticket.submitter_email == user_email)
    
    delete_is_valid = is_valid_remove(user_id)

    data = {
        "project" : project_name_list_json,
        "userinfo" : userinfo,
        "user_project" : user_project_list,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "user" : [user],
        "page": "user-details",
        "ticket": ticket_list,
        "is_valid_remove":delete_is_valid
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
    if userinfo['role']!= 'Admin':
        abort(401)
    user_id = request.form.get('user_id')
    project_id = request.form.get('project')
    role = request.form.get('role')
    page = request.form.get('page')
    today = date.today()
    #update_date = today.strftime("%d/%m/%Y")
    update_date = constants.CURRENT_DATE
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
    userinfo = session.get('profile')
    if userinfo['role']!= 'Admin':
        abort(401)

    
    user_id = request.args.get('user_id')

    delete_is_valid = is_valid_remove(user_id)
    if not delete_is_valid:
        abort(403)
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
    userinfo = session.get('profile')
    if userinfo['role']!= 'Admin':
        abort(401)

  
    user_id = request.args.get('user_id')

    delete_is_valid = is_valid_remove(user_id)
    if not delete_is_valid:
        abort(403)
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
    if userinfo['role']!= 'Admin':
        abort(401)
    project_list = Project.query.all()
    project= [Project.json_format(row) for row in project_list]
    print(project)
    data = {
        "project" : project,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "projects",
        "userinfo" : userinfo,
    }
    return render_template('admin-mainpage.html', data = data)


############################################# 11 ################################################
#   FETCH ALL TICKETS                                                                           #
#   Output  :   Admin main page - tickets tab                                                   #
#################################################################################################
@app.route('/admin/tickets', methods=['GET'])
def admin_get_tickets():
    userinfo = session.get('profile')
    if userinfo['role']!= 'Admin':
        abort(401)
    ticket_value = Ticket.query.join(Project, Ticket.p_id == Project.p_id)\
                    .add_columns(Ticket.t_id.label('id'),Ticket.t_title.label('title'), Ticket.t_desc.label('desc'), \
                        Ticket.assigned_user_id.label('user_id'), Project.p_name.label('p_id')\
                        ,Ticket.t_priority.label('priority'), Ticket.t_status.label('status'),Ticket.t_type.label('type')\
                            ,Ticket.t_create_date.label('create_date'), Ticket.t_close_date.label('close_date')).all()

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
    userinfo = session.get('profile')
    if userinfo['role']!= 'Admin':
        abort(401)
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
    if userinfo['role']!= 'Admin':
        abort(401) 
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


############################################# 2 #################################################
#   PROJECT CREATION   :   Create a new user                                                       #
#################################################################################################
@app.route("/admin/create-project")
def create_project():
    userinfo = session.get('profile')
    if userinfo['role']!= 'Admin':
        abort(401)  

    data = {
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page": "create-project"
    }
    return render_template('projectform.html', data = data)

############################################# 3 #################################################
#   SUBMIT PROJECT :   Submit PROJECT information                                               #
#   Algorithm   :   1.  Read input values from the form                                         #
#                   2.  Update user info in the USER table                                      #
#                   3.  Update project and user role in the User-Project mapping table          #
#   Routing     :   Admin submits form ->   User created    ->  Admin user list page            #
#################################################################################################
@app.route("/admin/project-submit", methods=['POST'])
def submit_project():
    userinfo = session.get('profile')
    if userinfo['role']!= 'Admin':
        abort(401)
    proj_name = request.form.get('proj_name')
    proj_desc = request.form.get('proj_desc')
    today = date.today()
    #p_create_date = today.strftime("%d/%m/%Y")
    p_create_date = constants.CURRENT_DATE
    p_id = db.session.query(func.max(Project.p_id)).all()
    if p_id[0][0] == None:
        proj_entry = Project(1, proj_name, proj_desc, p_create_date, "")
    else:
        proj_entry = Project(p_id[0][0] + 1, proj_name, proj_desc, p_create_date, "")
    try:
        proj_entry.insert()
    except:
        print(sys.exc_info())
        abort(500)


    return redirect("/admin/projects")