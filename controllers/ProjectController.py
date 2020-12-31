#################################################################################################
#                                                                                               #
#   Module          :   Project Controller                                                      #
#   Operations      :                                                                           #
#   1.  Redirect project queries           /projects                            All end users   #
#   2.  Project details                    /projectdetails/<int:project_id>     All end users   #
#   Last Update     :    Initial function definition                                            #
#   Last Update date:   19 Dec 2020                                                             #
#                                                                                               #
#################################################################################################

from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session
from app import app, db
import os, sys
from datetime import date
from sqlalchemy import text

from models.ProjectModel import Project
from models.UserProjMapModel import Map_user_proj
from models.UsersModel import Users
from models.TicketModel import Ticket

from controllers import NotificationController
from controllers import AdminController

def project_user_list_to_json(self):
    return {
            "p_id" : self.p_id,
            "user_id":self.user_id,
            "role":self.user_role,
            "name":self.user_name,
            "email":self.user_email        
        }

#################################################################################################
#   REDIRECT PROJECTS REQUESTS                                                                  #
#################################################################################################
@app.route("/projects")
def redirect_projects():
    userinfo = session.get('profile')
    if userinfo['role'] == 'Developer':
        return redirect('/dev/projects')
    elif userinfo['role'] == 'Admin':
        return redirect('/admin/projects')
    elif userinfo['role'] == 'Project Manager':
        return redirect('/manager/projects')
    return ""


#################################################################################################
#   FETCH PROJECT DETAILS                                                                       #
#   Algorithm   :   1.  Fetch project information from project table                            #
#                   2.  Get user list for the project (project_users)                           #
#                   3.  Get tickets for project (project_tickets)                               #
#################################################################################################
@app.route("/projectdetails/<int:project_id>")
def get_project_details(project_id):
    userinfo = session.get('profile')
    #Check if the request is valid
    authorized_personnel = Map_user_proj.query.with_entities(Map_user_proj.user_id).filter(Map_user_proj.p_id == project_id)\
                            .filter(Map_user_proj.user_id ==userinfo['user_id']).all()
    if len(authorized_personnel) == 0 and userinfo['role'] != 'Admin':
        abort(401)

    project_list = Project.query.get(project_id)
    project = Project.json_format(project_list)

    project_users_list = Map_user_proj.query.join(Users, Map_user_proj.user_id == Users.user_id)\
                    .add_columns(Map_user_proj.p_id, Map_user_proj.user_id, Map_user_proj.user_role, Users.user_name, Users.user_email)\
                    .filter(Map_user_proj.p_id == project_id).all()
    project_users =  [project_user_list_to_json(row) for row in project_users_list]

    for u in project_users:
        valid_delete = AdminController.is_valid_remove(u['user_id'])    
        u['valid_delete'] = valid_delete


    project_tickets_list = Ticket.query.join(Users, Ticket.assigned_user_id == Users.user_id, isouter=True )\
                        .add_columns(Ticket.t_id,Ticket.t_title,Ticket.t_desc, Users.user_name.label('assigned_user_id'), \
                            Ticket.submitter_email, Ticket.p_id, Ticket.t_priority, Ticket.t_status, Ticket.t_type,\
                                Ticket.t_create_date, Ticket.t_close_date)\
                        .filter(Ticket.p_id == project_id).all()
    project_tickets =  [Ticket.json_format(row) for row in project_tickets_list]

    #user_list = Users.query.filter(Users.user_role != "Admin").all()
    sql = text("""select user_id, user_name,user_email
                    ,user_pwd,user_role,update_date from users 
                    where user_role!='Admin' and user_id not in (select user_id from map_user_proj where p_id ="""+str(project_id)+""")""")
    result = db.session.execute(sql)
    users = [row for row in result]
    user_list_json = [Users.json_format(u) for u in users]  


    #Get notifications
    notification_list = NotificationController.get_notifications(userinfo['user_id'])
    notification_count = len(notification_list)

    

    data = {
        "project" :project,
        "project_users" : project_users,
        "ticket" : project_tickets,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "project_detail",
        "userlist" : user_list_json,
        "notification" : notification_list,
        "notification_count" : notification_count
    }
    return render_template('project_details.html', data = data )


