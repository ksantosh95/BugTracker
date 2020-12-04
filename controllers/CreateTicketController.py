from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session
from app import app, db
import os, sys
from datetime import date
from sqlalchemy import text

from models.TicketModel import Ticket
from models.ProjectModel import Project


@app.route("/createticket")
def create_ticket():
    userinfo = session.get('profile')
    dev_email= userinfo['name']
    project_name_list = Project.query.all()
    project_name_list_json = [Project.json_format(row) for row in project_name_list]
    return render_template('ticketform.html', project = project_name_list_json)

@app.route("/ticketsubmit", methods=['POST'])
def submit_ticket():
    profile = session.get('profile')
    t_title = request.form.get('t_title')
    t_desc = request.form.get('t_desc')
    emp_id = 0
    submitter_email = profile['name']
    p_id = request.form.get('project')
    t_priority = request.form.get('t_priority')
    t_status = "open"
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