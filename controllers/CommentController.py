#################################################################################################
#                                                                                               #
#   Module          :   Comment Controller                                                      #
#   Operations      :                                                                           #
#   1.  Submit Comment                     /submitcomment                   Users, Dev, Manager #
#   Last Update     :    Initial function definition                                            #
#   Last Update date:   19 Dec 2020                                                             #
#                                                                                               #
#################################################################################################

from flask import Flask, jsonify, request, abort, render_template, redirect, url_for,  session
from app import app, db
import os, sys
from datetime import date
from sqlalchemy import text, func
import constants
from models.TicketModel import Ticket
from models.UsersModel import Users
from models.CommentModel import Comment


#################################################################################################
#   Add Comment                                                                                 #
#   Incoming Call : Ticket Details page                                                         #
#################################################################################################
@app.route('/submitcomment', methods=['POST'])
def submit_comment():
    comment_text = request.form.get('comment')
    ticket_id = request.form.get('ticket_id')
    today = date.today()
    #update_date = today.strftime("%d/%m/%Y")
    update_date = constants.CURRENT_DATE
    userinfo = session.get('profile')
    user_id = Users.query.with_entities(Users.user_id).filter_by(user_email= userinfo['email'])
    c_id = db.session.query(func.max(Comment.c_id)).all()
    if c_id[0][0] == None:
        comment_entry = Comment(1, ticket_id, user_id, update_date, comment_text)
    else:
        comment_entry = Comment(c_id[0][0] + 1, ticket_id, user_id, update_date, comment_text)
    try:
        comment_entry.insert()
    except:
        print(sys.exc_info())
        abort(500)

    return redirect('/ticketdetails/'+ticket_id)



    

