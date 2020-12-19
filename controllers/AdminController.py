from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session
from app import app, db
import os, sys
from datetime import date
from sqlalchemy import text
from datetime import datetime

from models.TicketModel import Ticket
from models.ProjectModel import Project
from models.UserProjMapModel import Map_user_proj
from models.UsersModel import Users

from controllers import NotificationController

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

#CREATE A NEW USER

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


#UPDATE INFORMATION FOR THE USER
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

#DELETE USER
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


#ASSIGN PROJECT TO THE USER
@app.route("/admin/assign-user-project", methods=['POST'])
def assign_user_to_project():
    userinfo = session.get('profile')
    user_id = request.form.get('user_id')
    project_id = request.form.get('project')
    role = request.form.get('role')
    page = request.form.get('page')
    today = date.today()
    update_date = today.strftime("%d/%m/%Y")
    map_entry = Map_user_proj (user_id, project_id, role,update_date, "" )
    try:
        map_entry.insert()
    except:
        print(sys.exc_info())
        abort(500)
    if page == 'project-details':
        return redirect("/projectdetails/" + project_id)
    else:
        return redirect("/admin/userdetails/" + user_id)

##DELETE USER FROM USER DETAILS PAGE
@app.route("/admin/delete-project-user/")
def delete_project_user():
    user_id = request.args.get('user_id')
    project_id = request.args.get('project_id')
    map= Map_user_proj.query.filter(Map_user_proj.user_id == user_id).filter(Map_user_proj.p_id == project_id).one()
    map.delete()
    return redirect("/admin/userdetails/" + user_id)

##DELETE USER FROM PROJECT DETAILS PAGE
@app.route("/admin/delete-project-user-project-details/")
def delete_project_user_projectdetails():
    user_id = request.args.get('user_id')
    project_id = request.args.get('project_id')
    map= Map_user_proj.query.filter(Map_user_proj.user_id == user_id).filter(Map_user_proj.p_id == project_id).one()
    map.delete()
    return redirect("/projectdetails/" + project_id)

#ADMIN PROJECT LIST
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


