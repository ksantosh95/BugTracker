from flask import Flask, jsonify, request, abort
from app import app, db
import os, sys
from datetime import date


from models.TicketModel import Ticket



@app.route('/ticketsubmit', methods=['POST'])
def ticketsubmit():
    #request.form = request.get_json()
    t_title = request.form.get('t_title')
    t_desc = request.form.get('t_desc')
    #emp_id = request.form.get('emp_id')
    emp_id = 0
    #t_submitter = request.form.get('t_submitter')
    t_submitter =""
    p_id = request.form.get('p_id')
    t_priority = request.form.get('t_priority')
    t_status = "open"
    t_type = request.form.get('t_type')
    today = date.today()
    
    t_create_date = today.strftime("%d/%m/%Y")
    t_close_date = ""

    ticket_entry = Ticket(t_title,t_desc,emp_id,t_submitter,p_id,t_priority,t_status,t_type,t_create_date,t_close_date)
    try:
        ticket_entry.insert()
    except:
        print(sys.exc_info())
        abort(500)

    return jsonify(
        {
            "success":True
        }
    ),201
    


@app.route('/ticketview')
def ticketview():
    ticket_value = Ticket.query.all()
    ticket_value = [t.json_format() for t in ticket_value]
    return jsonify(ticket_value)

    
