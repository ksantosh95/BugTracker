from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session
from app import app, db
import os, sys
from datetime import date


from models.TicketModel import Ticket


@app.route('/tickets', methods=['GET'])
def get_tickets():
    userinfo = session.get('profile')
    ticket_value = Ticket.query.filter_by(submitter_email= userinfo['name']).all()
    ticket_value = [t.json_format() for t in ticket_value]
    return render_template('tickets.html', ticket = ticket_value, userinfo = userinfo)


@app.route("/createticket")
def create_ticket():
    return render_template('ticketform.html')


@app.route('/ticketsubmit', methods=['POST'])
def submit_ticket():
    profile = session.get('profile')
    t_title = request.form.get('t_title')
    t_desc = request.form.get('t_desc')
    emp_id = 0
    submitter_email = profile['name']
    #p_id = request.form.get('p_id')
    p_id = 1000
    t_priority = request.form.get('t_priority')
    t_status = "open"
    t_type = request.form.get('t_type')
    today = date.today()
    t_create_date = today.strftime("%d/%m/%Y")
    t_close_date = ""
   
    ticket_entry = Ticket(t_title,t_desc,emp_id,submitter_email,p_id,t_priority,t_status,t_type,t_create_date,t_close_date)
    try:
        ticket_entry.insert()
    except:
        print(sys.exc_info())
        abort(500)

    return redirect(url_for('get_tickets'))
    



    
