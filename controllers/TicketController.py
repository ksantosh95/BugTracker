from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session
from app import app, db
import os, sys
from datetime import date
from sqlalchemy import text

from models.TicketModel import Ticket
from models.ProjectModel import Project
from models.Ticket_DetailModel import Ticket_detail


@app.route("/createticket")
def create_ticket():
    userinfo = session.get('profile')
    dev_email= userinfo['name']
    project_name_list = Project.query.all()
    project_name_list_json = [Project.json_format(row) for row in project_name_list]
    
    data = {
        "project" : project_name_list_json,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname']
    }
    return render_template('ticketform.html', data = data)

@app.route("/ticketsubmit", methods=['POST'])
def submit_ticket():
    profile = session.get('profile')
    t_title = request.form.get('t_title')
    t_desc = request.form.get('t_desc')
    emp_id = 0
    submitter_email = profile['name']
    p_id = request.form.get('project')
    t_priority = request.form.get('t_priority')
    t_status = "Open"
    t_type = request.form.get('t_type')
    today = date.today()
    t_create_date = today.strftime("%d/%m/%Y")
    t_close_date = "N/A"
   
    ticket_entry = Ticket(t_title,t_desc,emp_id,submitter_email,p_id,t_priority,t_status,t_type,t_create_date,t_close_date)
    try:
        ticket_entry.insert()
    except:
        print(sys.exc_info())
        abort(500)
    
    
    if profile['role'][0] == 'Developer':
        return redirect(url_for('dev_get_tickets'))
    elif profile['role'][0] == 'User':
        return redirect(url_for('user_get_tickets'))
    return ""



@app.route("/ticketdetails/<int:ticket_id>")
def get_ticket_details(ticket_id):
    sql = text("""SELECT tick_detail.t_id, 
                        filter.emp_name as emp_id, 
                        tick_detail.t_status, 
                        tick_detail.t_update_date, 
                        tick_detail.t_comment 
                    FROM   ticket_detail tick_detail 
                        INNER JOIN (SELECT emp.emp_name, 
                                            tick.t_id 
                                    FROM   employee emp 
                                            INNER JOIN (SELECT emp_id, 
                                                                t_id 
                                                        FROM   ticket 
                                                        WHERE  t_id = """ + str(ticket_id)+""") tick 
                                                    ON emp.emp_id = tick.emp_id) filter 
                                ON tick_detail.t_id = filter.t_id   """)
    result = db.session.execute(sql)
    ticket_detail_list = [row for row in result]
    ticket_detail = [Ticket_detail.json_format(row) for row in ticket_detail_list]

    userinfo = session.get('profile')

    sql_ticket = text(""" SELECT tick.t_id, 
                            tick.t_title, 
                            tick.t_desc, 
                            emp.emp_name AS emp_id, 
                            tick.submitter_email, 
                            proj.p_name  AS p_id, 
                            tick.t_priority, 
                            tick.t_status, 
                            tick.t_type, 
                            tick.t_create_date, 
                            tick.t_close_date 
                        FROM   ticket tick 
                            INNER JOIN project proj 
                                    ON tick.p_id = proj.p_id 
                            INNER JOIN employee emp 
                                    ON emp.emp_id = tick.emp_id 
                        WHERE  tick.t_id = """+ str(ticket_id)+ """  """)
    result_ticket = db.session.execute(sql_ticket)
    ticket_list = [row for row in result_ticket]
    ticket = [Ticket.json_format(row) for row in ticket_list]


    data = {
        "ticket" : ticket,
        "ticket_detail" : ticket_detail,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "ticket_detail"
    }
    return render_template('ticket_details.html', data = data )

@app.route("/tickets")
def redirect_tickets():
    userinfo = session.get('profile')
    if userinfo['role'][0] == 'Developer':
          return redirect(url_for('dev_get_tickets'))
    elif userinfo['role'][0] == 'User':
        return redirect(url_for('user_get_tickets'))
    return ""
