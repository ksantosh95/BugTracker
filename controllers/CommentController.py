from flask import Flask, jsonify, request, abort, render_template, redirect, url_for,  session
from app import app, db
import os, sys
from datetime import date
from sqlalchemy import text

from models.TicketModel import Ticket
from models.UsersModel import Users
from models.CommentModel import Comment



@app.route('/submitcomment', methods=['POST'])
def submit_comment():
    comment_text = request.form.get('comment')
    ticket_id = request.form.get('ticket_id')
    today = date.today()
    update_date = today.strftime("%d/%m/%Y")
    userinfo = session.get('profile')
    user_id = Users.query.with_entities(Users.user_id).filter_by(user_email= userinfo['email'])
    comment_entry = Comment(ticket_id, user_id, update_date, comment_text)
    try:
        comment_entry.insert()
    except:
        print(sys.exc_info())
        abort(500)

    return redirect('/ticketdetails/'+ticket_id)



    

