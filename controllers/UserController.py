#################################################################################################
#                                                                                               #
#   Module          :   User Controller                                                         #
#   Operations      :                                                                           #
#   1.  Fetch tickets submitted by user           /user/tickets                      Users      #
#   Last Update     :    Initial function definition                                            #
#   Last Update date:   19 Dec 2020                                                             #
#                                                                                               #
#################################################################################################
from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session
from flask_cors import cross_origin
from app import app, db
import os, sys
from datetime import date


from models.TicketModel import Ticket
from models.ProjectModel import Project
from controllers import NotificationController


#################################################################################################
#    FETCH TICKETS SUBMITTED BY THE USER                                                        #
#################################################################################################
@app.route('/user/tickets', methods=['GET'])
def user_get_tickets():
    userinfo = session.get('profile')
    if userinfo['role']!= 'User':
        abort(401)

    ticket_value = Ticket.query.join(Project, Ticket.p_id == Project.p_id)\
                    .add_columns(Ticket.t_id.label('id'),Ticket.t_title.label('title'), Ticket.t_desc.label('desc'), \
                        Ticket.assigned_user_id.label('user_id'), Project.p_name.label('p_id')\
                        ,Ticket.t_priority.label('priority'), Ticket.t_status.label('status'),Ticket.t_type.label('type')\
                            ,Ticket.t_create_date.label('create_date'), Ticket.t_close_date.label('close_date'))\
                                .filter(Ticket.submitter_email == userinfo['email']).all()
    notification_list = NotificationController.get_notifications(userinfo['user_id'])
    data = {
        "ticket" : ticket_value,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "tickets",
        "notification" : notification_list
    }
    return render_template('mainpage.html', data = data)



    



    
