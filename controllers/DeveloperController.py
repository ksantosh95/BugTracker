#################################################################################################
#                                                                                               #
#   Module          :   Developer Controller                                                    #
#   Operations      :                                                                           #
#   1.  List of all tickets                     /dev/tickets                      Developer     #
#   2.  List of all projects for the dev        /dev/projects                     Developer     #
#   3.  List of tickets assigned to dev         /dev/assignedtickets              Developer     #
#   4.  List of tickets submitted by dev        /dev/submittedtickets             Developer     #
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

from models.TicketModel import Ticket
from models.ProjectModel import Project
from models.UserProjMapModel import Map_user_proj
from models.UsersModel import Users

from controllers import NotificationController
from controllers import TicketController

########################################### 1  ##################################################

@app.route('/dev/tickets', methods=['GET'])
def dev_get_tickets():
    userinfo = session.get('profile')
    if userinfo['role']!= 'Developer':
        abort(401)
    dev_email= userinfo['name']
    sql = text("""SELECT tick.t_id, 
                    tick.t_title, 
                    tick.t_desc, 
                    tick.assigned_user_id, 
                    tick.submitter_email, 
                    proj.p_name AS p_id, 
                    tick.t_priority, 
                    tick.t_status, 
                    tick.t_type, 
                    tick.t_create_date, 
                    tick.t_close_date 
                FROM   ticket tick 
                    INNER JOIN (SELECT map.p_id 
                                FROM   map_user_proj map 
                                        INNER JOIN (SELECT * 
                                                    FROM   users 
                                                    WHERE  user_email = '""" + dev_email+ """') 
                                                    u 
                                                ON map.user_id = u.user_id) filter 
                            ON tick.p_id = filter.p_id 
                    INNER JOIN project proj 
                            ON tick.p_id = proj.p_id """)
    result = db.session.execute(sql)
    names = [row for row in result]
    ticket_value = [Ticket.array_to_json_format(row) for row in names]

    today = date.today()
    t_create_date = today.strftime("%d/%m/%Y")
    d1 = datetime.strptime(t_create_date, '%d/%m/%Y')
    for t in ticket_value:
        d2 = datetime.strptime(t['create_date'], '%d/%m/%Y')
        t['datediff'] = abs((d2 - d1).days)

    #Get notifications
    notification_list = NotificationController.get_notifications(userinfo['user_id'])
    notification_count = len(notification_list)
    data = {
        "ticket" : ticket_value,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "tickets",
        "notification" : notification_list,
        "notification_count" : notification_count
    }
    


    return render_template('mainpage.html', data = data)


@app.route('/dev/projects', methods=['GET'])
def dev_get_projects():
    userinfo = session.get('profile')
    if userinfo['role']!= 'Developer':
        abort(401)
    dev_email= userinfo['email']
    project_list = Project.query.join(Map_user_proj, Project.p_id == Map_user_proj.p_id)\
				.join(Users, Users.user_id == Map_user_proj.user_id)\
				.add_columns(Project.p_id,Project.p_name,Project.p_desc,Project.p_start_date,Project.p_end_date)\
				.filter(Users.user_email == dev_email).all()
    project = [Project.json_format(proj) for proj in project_list]   

    #Get notifications
    notification_list = NotificationController.get_notifications(userinfo['user_id'])
    notification_count = len(notification_list)
    data = {
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "projects",
        "project" : project,
        "notification" : notification_list,
        "notification_count" : notification_count
    }
    return render_template('mainpage.html', data = data)


@app.route('/dev/assignedtickets', methods=['GET'])
def get_dev_assigned_tickets():
    userinfo = session.get('profile')
    if userinfo['role']!= 'Developer':
        abort(401)
    dev_email= userinfo['email']
    ticket_list = Ticket.query.join(Users, Ticket.assigned_user_id == Users.user_id)\
                    .join(Project, Ticket.p_id == Project.p_id)\
                    .add_columns(Ticket.t_id, Ticket.t_title, Ticket.t_desc, Ticket.assigned_user_id, Ticket.submitter_email,\
                        Project.p_name.label('p_id'), Ticket.t_priority, Ticket.t_status, Ticket.t_type, Ticket.t_create_date, Ticket.t_close_date)\
                            .filter(Users.user_email == dev_email)\
                                .filter(Users.user_role== 'Developer').all()
    ticket = [Ticket.json_format(tick) for tick in ticket_list]  
    
    today = date.today()
    t_create_date = today.strftime("%d/%m/%Y")
    d1 = datetime.strptime(t_create_date, '%d/%m/%Y')
    for t in ticket:
        d2 = datetime.strptime(t['create_date'], '%d/%m/%Y')
        t['datediff'] = abs((d2 - d1).days)


    notification_list = NotificationController.get_notifications(userinfo['user_id'])
    notification_count = len(notification_list)
    data = {
        "ticket" : ticket,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "assignedtickets",
        "notification" : notification_list,
        "notification_count" : notification_count
    }
    return render_template('mainpage.html', data = data)


@app.route('/dev/submittedtickets', methods=['GET'])
def get_dev_submitted_tickets():
    ticket = TicketController.get_submitted_tickets()
    userinfo = session.get('profile')
    if userinfo['role']!= 'Developer':
        abort(401)
    #Get notifications
    notification_list = NotificationController.get_notifications(userinfo['user_id'])
    notification_count = len(notification_list)

    data = {
        "ticket" : ticket,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "submittedtickets",
        "notification" : notification_list,
        "notification_count" : notification_count
    }
    return render_template('mainpage.html', data = data)