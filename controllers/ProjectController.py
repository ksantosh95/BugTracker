from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session
from app import app, db
import os, sys
from datetime import date
from sqlalchemy import text

from models.ProjectModel import Project
from models.UserProjMapModel import Map_user_proj
from models.UsersModel import Users
from models.TicketModel import Ticket

def project_user_list_to_json(self):
    return {
            "p_id" : self.p_id,
            "user_id":self.user_id,
            "role":self.user_role,
            "name":self.user_name,
            "email":self.user_email        
        }

@app.route("/projects")
def redirect_projects():
    userinfo = session.get('profile')
    if userinfo['role'][0] == 'Developer':
        return redirect('/dev/projects')
    return ""

@app.route("/projectdetails/<int:project_id>")
def get_project_details(project_id):
    userinfo = session.get('profile')

    project_list = Project.query.get(project_id)
    project = Project.json_format(project_list)

    project_users_list = Map_user_proj.query.join(Users, Map_user_proj.user_id == Users.user_id)\
                    .add_columns(Map_user_proj.p_id, Map_user_proj.user_id, Map_user_proj.user_role, Users.user_name, Users.user_email)\
                    .filter(Map_user_proj.p_id == project_id).all()
    project_users =  [project_user_list_to_json(row) for row in project_users_list]

    project_tickets_list = Ticket.query.join(Users, Ticket.assigned_user_id == Users.user_id)\
                        .add_columns(Ticket.t_id,Ticket.t_title,Ticket.t_desc, Users.user_name.label('assigned_user_id'), \
                            Ticket.submitter_email, Ticket.p_id, Ticket.t_priority, Ticket.t_status, Ticket.t_type,\
                                Ticket.t_create_date, Ticket.t_close_date)\
                        .filter(Ticket.p_id == project_id).all()
    project_tickets =  [Ticket.json_format(row) for row in project_tickets_list]

    data = {
        "project" :project,
        "project_users" : project_users,
        "ticket" : project_tickets,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "project_detail"
    }
    return render_template('project_details.html', data = data )