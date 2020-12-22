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
from controllers import NotificationController

#################################################################################################
#    FETCH TICKETS SUBMITTED BY THE USER                                                        #
#################################################################################################
@app.route('/user/tickets', methods=['GET'])
def user_get_tickets():
    userinfo = session.get('profile')
    ticket_value = Ticket.query.filter_by(submitter_email= userinfo['email']).all()
    ticket_value = [t.json_format() for t in ticket_value]

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



    



    
