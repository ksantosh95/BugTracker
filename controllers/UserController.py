from flask import Flask, jsonify, request, abort, render_template, redirect, url_for
from app import app, db
import os, sys
from datetime import date


from models.TicketModel import Ticket


@app.route('/tickets', methods=['GET'])
def ticketview():
    ticket_value = Ticket.query.filter_by(submitter_id = "10").all()
    ticket_value = [t.json_format() for t in ticket_value]
    return render_template('tickets.html', ticket = ticket_value)



@app.route('/ticketsubmit', methods=['POST'])
def ticketsubmit():
    t_title = request.form.get('t_title')
    t_desc = request.form.get('t_desc')
    emp_id = 0
    submitter_id =10
    #p_id = request.form.get('p_id')
    p_id = 1000
    t_priority = request.form.get('t_priority')
    t_status = "open"
    t_type = request.form.get('t_type')
    today = date.today()
    t_create_date = today.strftime("%d/%m/%Y")
    t_close_date = ""
   
    ticket_entry = Ticket(t_title,t_desc,emp_id,submitter_id,p_id,t_priority,t_status,t_type,t_create_date,t_close_date)
    try:
        ticket_entry.insert()
    except:
        print(sys.exc_info())
        abort(500)

    return redirect(url_for('tickets'))
    



    
