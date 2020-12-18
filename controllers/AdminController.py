from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session
from app import app, db
import os, sys
from datetime import date
from sqlalchemy import text
from datetime import datetime

from models.TicketModel import Ticket
from models.ProjectModel import Project
from models.UserProjMapModel import Map_user_proj
from models.UsersModel import Users

from controllers import NotificationController

@app.route('/admin/user-list', methods=['GET'])
def admin_get_users():
    userinfo = session.get('profile')
    user_list = Users.query.filter(Users.user_role != "Admin").all()
    user = [Users.json_format(u) for u in user_list]  
    data = {
        "user" : user,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "admin-user",
        "userinfo" : userinfo
    }
    return render_template('admin-mainpage.html', data = data)

#CREATE A NEW USER

@app.route("/create-user")
def create_user():
    userinfo = session.get('profile')  
    data = {
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname']
    }
    return render_template('userform.html', data = data)





@app.route("/user-submit", methods=['POST'])
def submit_user():
    user_name = request.form.get('user_name')
    user_email = request.form.get('user_email')
    user_role = request.form.get('user_role')
    user_pwd = "bugTracker123"
    today = date.today()
    update_date = today.strftime("%d/%m/%Y")
   
    user_entry = Users(user_name, user_email,user_pwd, user_role, update_date)
    try:
        user_entry.insert()
    except:
        print(sys.exc_info())
        abort(500)

    return redirect("/admin/user-list")