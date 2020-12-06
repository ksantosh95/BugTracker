from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session
from app import app, db
import os, sys
from datetime import date
from sqlalchemy import text

from models.TicketModel import Ticket
from models.ProjectModel import Project
from models.Ticket_HistoryModel import Ticket_history
from models.CommentModel import Comment
from models.UsersModel import Users


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
    user_id = 0
    submitter_email = profile['name']
    p_id = request.form.get('project')
    t_priority = request.form.get('t_priority')
    t_status = "Open"
    t_type = request.form.get('t_type')
    today = date.today()
    t_create_date = today.strftime("%d/%m/%Y")
    t_close_date = "N/A"
   
    ticket_entry = Ticket(t_title,t_desc,user_id,submitter_email,p_id,t_priority,t_status,t_type,t_create_date,t_close_date)
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
def get_ticket_history(ticket_id):
    sql = text("""SELECT tick_history.t_id, 
                        filter.user_name as user_id, 
                        tick_history.t_status, 
                        tick_history.t_update_date, 
                        tick_history.t_priority 
                    FROM   ticket_history tick_history 
                        INNER JOIN (SELECT u.user_name, 
                                            tick.t_id 
                                    FROM   users u 
                                            INNER JOIN (SELECT assigned_user_id, 
                                                                t_id 
                                                        FROM   ticket 
                                                        WHERE  t_id = """ + str(ticket_id)+""") tick 
                                                    ON u.user_id = tick.assigned_user_id) filter 
                                ON tick_history.t_id = filter.t_id   """)
    result = db.session.execute(sql)
    ticket_history_list = [row for row in result]
    ticket_history = [Ticket_history.json_format(row) for row in ticket_history_list]

    userinfo = session.get('profile')

    sql_ticket = text(""" SELECT tick.t_id, 
                            tick.t_title, 
                            tick.t_desc, 
                            u.user_name AS assigned_user_id, 
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
                            LEFT OUTER JOIN users u 
                                    ON u.user_id = tick.assigned_user_id 
                        WHERE  tick.t_id = """+ str(ticket_id)+ """  """)
    result_ticket = db.session.execute(sql_ticket)
    ticket_list = [row for row in result_ticket]
    ticket = [Ticket.json_format(row) for row in ticket_list]

    comment_list = Comment.query.join(Users, Comment.user_id==Users.user_id)\
                .add_columns(Comment.t_id, Comment.comment, Comment.date, Users.user_name.label('user_id'))\
                .filter(Comment.t_id==ticket_id).all()
    comment = [Comment.json_format(row) for row in comment_list]

    data = {
        "ticket" : ticket,
        "ticket_history" : ticket_history,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "ticket_detail",
        "comment" : comment
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
