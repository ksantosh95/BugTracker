from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session
from flask_cors import cross_origin
from app import app, db
import os, sys
from datetime import date


from models.TicketModel import Ticket


@app.route('/user/tickets', methods=['GET'])
def user_get_tickets():
    userinfo = session.get('profile')
    ticket_value = Ticket.query.filter_by(submitter_email= userinfo['name']).all()
    ticket_value = [t.json_format() for t in ticket_value]
    return render_template('tickets.html', ticket = ticket_value, userinfo = userinfo)


    



    
