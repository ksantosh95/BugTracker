from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session
from app import app, db
import os, sys
from datetime import date
from sqlalchemy import text

from models.TicketModel import Ticket
from models.ProjectModel import Project



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
    data = {
        "ticket" : ticket_value,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "tickets"
    }
    return render_template('tickets.html', data = data)



    
