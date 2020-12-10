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


@app.route('/dev/tickets', methods=['GET'])
def dev_get_tickets():
    userinfo = session.get('profile')
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

    data = {
        "ticket" : ticket_value,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "tickets"
    }
    
    return render_template('mainpage.html', data = data)


@app.route('/dev/projects', methods=['GET'])
def dev_get_projects():
    userinfo = session.get('profile')
    dev_email= userinfo['email']
    project_list = Project.query.join(Map_user_proj, Project.p_id == Map_user_proj.p_id)\
				.join(Users, Users.user_id == Map_user_proj.user_id)\
				.add_columns(Project.p_id,Project.p_name,Project.p_desc,Project.p_start_date,Project.p_end_date)\
				.filter(Users.user_email == dev_email).all()
    project = [Project.json_format(proj) for proj in project_list]   
    data = {
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "projects",
        "project" : project
    }
    return render_template('mainpage.html', data = data)


@app.route('/dev/assignedtickets', methods=['GET'])
def get_dev_assigned_tickets():
    userinfo = session.get('profile')
    dev_email= userinfo['email']
    ticket_list = Ticket.query.join(Users, Ticket.assigned_user_id == Users.user_id)\
                    .add_columns(Ticket.t_id, Ticket.t_title, Ticket.t_desc, Ticket.assigned_user_id, Ticket.submitter_email,\
                        Ticket.p_id, Ticket.t_priority, Ticket.t_status, Ticket.t_type, Ticket.t_create_date, Ticket.t_close_date)\
                            .filter(Users.user_email == dev_email)\
                                .filter(Users.user_role== 'Developer').all()
    ticket = [Ticket.json_format(tick) for tick in ticket_list]  
    
    today = date.today()
    t_create_date = today.strftime("%d/%m/%Y")
    d1 = datetime.strptime(t_create_date, '%d/%m/%Y')
    for t in ticket:
        d2 = datetime.strptime(t['create_date'], '%d/%m/%Y')
        t['datediff'] = abs((d2 - d1).days)

    data = {
        "ticket" : ticket,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "assignedtickets"
    }
    return render_template('mainpage.html', data = data)


@app.route('/dev/submittedtickets', methods=['GET'])
def get_dev_submitted_tickets():
    userinfo = session.get('profile')
    dev_email= userinfo['email']
    ticket_list = Ticket.query.filter_by(submitter_email= userinfo['email']).all()
    ticket = [Ticket.json_format(t) for t in ticket_list]  
    
    today = date.today()
    t_create_date = today.strftime("%d/%m/%Y")
    d1 = datetime.strptime(t_create_date, '%d/%m/%Y')
    for t in ticket:
        d2 = datetime.strptime(t['create_date'], '%d/%m/%Y')
        t['datediff'] = abs((d2 - d1).days)

    data = {
        "ticket" : ticket,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "submittedtickets"
    }
    return render_template('mainpage.html', data = data)