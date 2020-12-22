#################################################################################################
#                                                                                               #
#   Module          :   Notification Controller                                                 #
#   Operations      :                                                                           #
#   1.  Delete notifications           /deletenotification                 Users, Dev, Manager  #
#   Last Update     :   Initial function definition                                             #
#   Last Update date:   19 Dec 2020                                                             #
#                                                                                               #
#################################################################################################
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
from models.UserProjMapModel import Map_user_proj
from models.NotificationModel import Notification

#################################################################################################
#   FUNCTION TO FETCH ALL NOTIFICATIONS FOR USER ID                                             #
#################################################################################################
def get_notifications(user_id):
    notification_list = Notification.query.filter(Notification.user_id == user_id).all()
    return notification_list


#################################################################################################
#   DELETE NOTIFICATIONS FOR USER                                                               #
#################################################################################################
@app.route("/deletenotification")
def delete_notification():
    ticket_id = request.args.get('ticket_id')
    n_id = request.args.get('n_id')
    print(ticket_id)
    n = Notification.query.get(n_id)
    n.delete()
    return redirect('/ticketdetails/'+ ticket_id) 