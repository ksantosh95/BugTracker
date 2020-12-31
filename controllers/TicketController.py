#################################################################################################
#                                                                                               #
#   Module          :   Ticket Controller                                                       #
#   Operations      :                                                                           #
#   1.  Create Ticket               /createticket                       All end users           #
#   2.  Submit Ticket               /ticketsubmit                       All end users           #
#   3.  Ticket Details              /ticketdetails/<int:ticket_id>      All end users           #
#   4.  Redirect Ticket calls       /tickets                            All end users           #
#   5.  Assign Dev to Ticket        /assigndev                          Dev , Manager           #
#   6.  Update Ticket               /ticketupdate                       Admin                   #
#   7.  Update Ticket Status        /update-ticket-status               Dev , Manager           #
#   Last Update     :    Added function for updating tickets                                    #
#   Last Update date:   21 Dec 2020                                                             #
#                                                                                               #
#################################################################################################


from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session
from app import app, db
import os, sys
from datetime import date
from sqlalchemy import text, func
import constants
from models.TicketModel import Ticket
from models.ProjectModel import Project
from models.Ticket_HistoryModel import Ticket_history
from models.CommentModel import Comment
from models.UsersModel import Users
from models.UserProjMapModel import Map_user_proj
from models.NotificationModel import Notification

from controllers import NotificationController
from controllers import ManagerController



########################################### 1  ##################################################
#   Create Ticket       :   Used to create and submit a ticket                                  #
#   Incoming call       :   Create Ticket button on landing page                                #
#   Output              :   Ticket submitted to ticket, ticket history and notification table   #
#   Algorithm           :   Function (Create Ticket)                                            #
#                       :   1.  Fetch All projects to show case                                 #
#                           Function (Ticket Submit)                                            #
#                           1.  Read inputs. Set userid =0, open date=today, status= Open       #
#                           2.  Enter into ticket, ticket history and notification              #
#   Last Modification   :   Added notification creation                                         #
#################################################################################################

@app.route("/createticket")
def create_ticket():
    userinfo = session.get('profile')
    project_name_list = Project.query.join(Map_user_proj, Project.p_id == Map_user_proj.p_id)\
                        .add_columns(Project.p_id.label('id'), Project.p_name.label('name'))\
                        .filter(Map_user_proj.user_id == userinfo['user_id'])
    
    data = {
        "project" : project_name_list,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname']
    }
    return render_template('ticketform.html', data = data)

########################################### 2  ##################################################
@app.route("/ticketsubmit", methods=['POST'])
def submit_ticket():
    profile = session.get('profile')
    t_title = request.form.get('t_title')
    t_desc = request.form.get('t_desc')
    user_id = 0
    submitter_email = profile['name']
    p_id = request.form.get('project')
    t_priority = request.form.get('t_priority')
    t_status = "Open"
    t_type = request.form.get('t_type')
    today = date.today()
    #t_create_date = today.strftime("%d/%m/%Y")
    t_create_date = constants.CURRENT_DATE
    t_close_date = ""
    
    t_id = db.session.query(func.max(Ticket.t_id)).all()
    if t_id[0][0] == None:
        ticket_entry = Ticket(1,t_title,t_desc,user_id,submitter_email,p_id,t_priority,t_status,t_type,t_create_date,t_close_date)
    else:
        ticket_entry = Ticket(t_id[0][0] + 1, t_title,t_desc,user_id,submitter_email,p_id,t_priority,t_status,t_type,t_create_date,t_close_date)
    
    try:
        ticket_entry.insert()
    except:
        print(sys.exc_info())
        abort(500)
    
    #ENTER IN TICKET HISTORY
    ticket_id = ticket_entry.t_id
    t_history_id = db.session.query(func.max(Ticket_history.t_history_id)).all()
    if t_history_id[0][0] == None:
        ticket_history_entry = Ticket_history(1,ticket_id,user_id,t_status,t_create_date,t_priority)
    else:
        ticket_history_entry = Ticket_history(t_history_id[0][0]+1,ticket_id,user_id,t_status,t_create_date,t_priority)
        
    
    try:
        ticket_history_entry.insert()
    except:
        print(sys.exc_info())
        abort(500)

    #ENTER IN NOTIFICATIONS
    user_list = Map_user_proj.query.with_entities(Map_user_proj.user_id).filter(Map_user_proj.p_id == p_id).all()
    print(user_list)
    for user in user_list:
        notification = Notification(ticket_id, user, 'New')
        try:
            notification.insert()
        except:
            print(sys.exc_info())
            abort(500)
    if profile['role'] == 'Developer':
        return redirect(url_for('dev_get_tickets'))
    elif profile['role'] == 'User':
        return redirect(url_for('user_get_tickets'))
    elif profile['role'] == 'Admin':
        return redirect(url_for('admin_get_tickets'))
    elif profile['role'] == 'Project Manager':
        return redirect(url_for('manager_get_tickets'))
    return ""


########################################### 3 ###################################################
#   Fetch Ticket Details    :   Get ticket data, ticket history and developers in the project   #
#   Incoming Call           :   Called by details link in the ticket table                      #
#   Input parameter         :   ticket_id                                                       #
#   Functioning             :   Fetch columns from ticket, ticket history and notifications     #
#   Last modification       :   Added notification functionality                                #
#################################################################################################

@app.route("/ticketdetails/<int:ticket_id>")
def get_ticket_details(ticket_id):
    userinfo = session.get('profile')
    #Check whether the request is valid
    authorized_personnel = Map_user_proj.query.join(Ticket, Map_user_proj.p_id == Ticket.p_id)\
                            .add_columns(Map_user_proj.user_id).filter(Map_user_proj.user_id== userinfo['user_id'])\
                                .filter(Ticket.t_id == ticket_id).all()

    if len(authorized_personnel) == 0 and userinfo['role'] != 'Admin':
        abort(401)



    result = Ticket_history.query.join(Users, Ticket_history.user_id == Users.user_id, isouter=True)\
            .add_columns(Ticket_history.t_id, Users.user_name.label('user_id'), Ticket_history.t_status, Ticket_history.t_update_date\
                ,Ticket_history.t_priority)\
                    .filter(Ticket_history.t_id == ticket_id)
    ticket_history_list = [row for row in result]
    ticket_history = [Ticket_history.json_format(row) for row in ticket_history_list]

    

    #SELECT TICKET INFORMATION FOR TICKET_ID. SELECT PROJECT NAME AS 'P_ID'
    sql_ticket = text(""" SELECT tick.t_id, 
                            tick.t_title, 
                            tick.t_desc, 
                            u.user_name AS assigned_user_id, 
                            tick.submitter_email, 
                            proj.p_name  AS p_id, 
                            tick.t_priority, 
                            tick.t_status, 
                            tick.t_type, 
                            tick.t_create_date, 
                            tick.t_close_date 
                        FROM   ticket tick 
                            INNER JOIN project proj 
                                    ON tick.p_id = proj.p_id 
                            LEFT OUTER JOIN users u 
                                    ON u.user_id = tick.assigned_user_id 
                        WHERE  tick.t_id = """+ str(ticket_id)+ """  """)
    result_ticket = db.session.execute(sql_ticket)
    ticket_list = [row for row in result_ticket]
    ticket = [Ticket.json_format(row) for row in ticket_list]

    comment_list = Comment.query.join(Users, Comment.user_id==Users.user_id)\
                .add_columns(Comment.t_id, Comment.comment, Comment.date, Users.user_name.label('user_id'))\
                .filter(Comment.t_id==ticket_id)\
                .order_by(Comment.c_id.desc()).all()
    comment = [Comment.json_format(row) for row in comment_list]

    #Get list of developers in the project for assigning
    dev_list = Ticket.query.join(Map_user_proj, Ticket.p_id == Map_user_proj.p_id)\
                .join(Users, Map_user_proj.user_id == Users.user_id)\
                .add_columns(Users.user_name, Users.user_id)\
                .filter(Ticket.t_id == ticket_id).filter(Map_user_proj.user_role == 'Developer').all()

    assigned_dev_id = Ticket.query.with_entities(Ticket.assigned_user_id).filter(Ticket.t_id == ticket_id).all()

    #Get notifications
    notification_list = NotificationController.get_notifications(userinfo['user_id'])
    notification_count = len(notification_list)


    data = {
        "ticket" : ticket,
        "ticket_history" : ticket_history,
        "userinfo" : userinfo,
        "user_id": userinfo['user_id'],
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "ticket_detail",
        "comment" : comment,
        "dev_list" : dev_list,
        "notification" : notification_list,
        "notification_count" : notification_count,
        "assigned_dev":assigned_dev_id[0][0]
    }
    return render_template('ticket_details.html', data = data )


############################################ 4 ##################################################
#   Redirect Tickets    :   Redirects function call to appropriate user page                    #
#################################################################################################

@app.route("/tickets")
def redirect_tickets():
    userinfo = session.get('profile')
    if userinfo['role']== 'Developer':
          return redirect('/dev/assignedtickets')
    elif userinfo['role'] == 'User':
        return redirect(url_for('user_get_tickets'))
    elif userinfo['role']== 'Admin': 
        return redirect("/admin/tickets")
    elif userinfo['role'] == 'Project Manager':
        return redirect(url_for('manager_get_tickets'))
    return ""


############################################ 5 ##################################################
#   Assign Developer to Ticket  :   Called by Developers/Managers to assign a dev to a ticket   #
#   Incoming Call               :   Assign Personnel button on Ticket Details page              #
#   Functioning                 :   1.  Assigned developer is added to ticket table             #
#                                   2.  Comment is added to comment table                       #
#                                   3.  'Assigned'  type Notification is added                  #
#   Last Modification           :   Added notification functionality                            #
#################################################################################################

@app.route("/assigndev", methods=['POST'])
def assign_dev():
    ticket_id= request.form.get('ticket_id')
    ticket = Ticket.query.get(ticket_id)
    ticket.assigned_user_id = request.form.get('dev_name')
    ticket.update()

    #Insert record in ticket history
    user_id = request.form.get('dev_name')
    today = date.today()
    #t_update_date = today.strftime("%d/%m/%Y")
    t_update_date =constants.CURRENT_DATE
    t_history_id = db.session.query(func.max(Ticket_history.t_history_id)).all()
    if t_history_id[0][0] == None:
        ticket_history = Ticket_history(1, ticket_id, user_id, ticket.t_status, t_update_date, ticket.t_priority )
    else:
        ticket_history = Ticket_history(t_history_id[0][0]+1,ticket_id, user_id, ticket.t_status, t_update_date, ticket.t_priority )
    
    try:
        ticket_history.insert()
    except:
        print(sys.exc_info())
        abort(500)

    #Insert record in comments
    userinfo = session.get('profile')
    assigned_user_name = Users.query.with_entities(Users.user_name).filter(Users.user_id == user_id).one()
    c_id = db.session.query(func.max(Comment.c_id)).all()
    if c_id[0][0] == None:
        comment = Comment(1,ticket_id, userinfo['user_id'],t_update_date, " assigned developer " + assigned_user_name[0] )
    else:
        comment = Comment(c_id[0][0]+1,ticket_id, userinfo['user_id'],t_update_date, " assigned developer " + assigned_user_name[0] )
    try:
        comment.insert()
    except:
        print(sys.exc_info())
        abort(500)

    #Record a notification
    notification = Notification(ticket_id, user_id, 'Assigned')
    try:
        notification.insert()
    except:
        print(sys.exc_info())
        abort(500)
    return redirect('/ticketdetails/'+ ticket_id) 


############################################### 6 ###############################################
#   Update ticket   :   Update Ticket information                                               #
#   Incoming Call   :   Ticket Edit button on Ticket Details page                               #
#   Algorithm       :   1.  Ticket table is updated                                             #
#                       2.  If status or priority is updated, update ticket history             #
#                       3.  Add 'Update' type notification                                      #
#################################################################################################
@app.route("/ticketupdate", methods=['POST'])
def update_ticket():
    profile = session.get('profile')
    to_update_ticket_history = False
    ticket_id = request.form.get('ticket_id')
    t_title = request.form.get('t_title')
    t_desc = request.form.get('t_desc')
    p_id = request.form.get('project')
    t_priority = request.form.get('t_priority')
    t_status = request.form.get('t_status')
    t_type = request.form.get('t_type')
    today = date.today()
    #t_update_date = today.strftime("%d/%m/%Y")
    t_update_date = constants.CURRENT_DATE

    ticket_entry = Ticket.query.get(ticket_id)
    #CHECK IF TICKET HISTORY NEEDS TO BE UPDATED
    if t_status != ticket_entry.t_status or t_priority != ticket_entry.t_priority:
        to_update_ticket_history = True
    
    ticket_entry.t_title = t_title
    ticket_entry.t_desc = t_desc
    ticket_entry.p_id = p_id
    ticket_entry.t_priority = t_priority
    ticket_entry.t_status = t_status
    ticket_entry.t_type = t_type

    if t_status == "Closed":
        ticket_entry.t_close_date = constants.CURRENT_DATE

    try:
        ticket_entry.update()
    except:
        print(sys.exc_info())
        abort(500)
    
    #ENTER IN TICKET HISTORY
    if to_update_ticket_history:
        ticket_id = ticket_entry.t_id
        t_history_id = db.session.query(func.max(Ticket_history.t_history_id)).all()
        if t_history_id[0][0] == None:
            ticket_history_entry = Ticket_history(1,ticket_id,ticket_entry.assigned_user_id,t_status,t_update_date,t_priority)
        else:
            ticket_history_entry = Ticket_history(t_history_id[0][0]+1,ticket_id,ticket_entry.assigned_user_id,t_status,t_update_date,t_priority)
        
        try:
            ticket_history_entry.insert()
        except:
            print(sys.exc_info())   
            abort(500)

    #ENTER IN NOTIFICATIONS
    user_list = Map_user_proj.query.with_entities(Map_user_proj.user_id).filter(Map_user_proj.p_id == p_id).all()
    for user in user_list:
        notification = Notification(ticket_id, user, 'Update')
        try:
            notification.insert()
        except:
            print(sys.exc_info())
            abort(500)
    if profile['role'] == 'Developer':
        return redirect(url_for('dev_get_tickets'))
    elif profile['role'] == 'User':
        return redirect(url_for('user_get_tickets'))
    elif profile['role'] == 'Admin':
        return redirect(url_for('admin_get_tickets'))
    return ""


############################################## 7 ################################################
#   Update Ticket Status    :   Called by Developer to update the ticket status                 #
#   Incoming Call           :   Ticket status button on Ticket Details page                     #
#   Algorithm               :   1.  Update Ticket table                                         #
#                               2.  Update Ticket history table                                 #
#                               3.  Add 'Update' type notification to notification table        #
#   Last Update             :   Added notification                                              #
#################################################################################################
@app.route("/update-ticket-status", methods=['POST'])
def update_project_status():
    userinfo = session.get('profile')
    ticket_id = request.form.get('ticket_id')
    ticket_entry = Ticket.query.get(ticket_id)
    #today = date.today()
    #t_update_date = today.strftime("%d/%m/%Y")
    t_update_date = constants.CURRENT_DATE
    t_status = request.form.get('input')
    p_name = request.form.get('p_name')
    
    ticket_entry.t_status = t_status
    try:
        ticket_entry.update()
    except:
        print(sys.exc_info())
        abort(500)

    if t_status == "Closed":
        ticket_entry.t_close_date = t_update_date

    #ENTER IN TICKET HISTORY
    ticket_id = ticket_entry.t_id
    t_history_id = db.session.query(func.max(Ticket_history.t_history_id)).all()
    if t_history_id[0][0] == None:
        ticket_history_entry = Ticket_history(1,ticket_id,ticket_entry.assigned_user_id,t_status,t_update_date,ticket_entry.t_priority)
    else:
        ticket_history_entry = Ticket_history(t_history_id[0][0]+1,ticket_id,ticket_entry.assigned_user_id,t_status,t_update_date,ticket_entry.t_priority)
        
    
    try:
        ticket_history_entry.insert()
    except:
        print(sys.exc_info())   
        abort(500)

    #ENTER IN NOTIFICATIONS
    p_id = Project.query.with_entities(Project.p_id).filter(Project.p_name == p_name).one()
    user_list = Map_user_proj.query.with_entities(Map_user_proj.user_id).filter(Map_user_proj.p_id == p_id).all()
    for user in user_list:
        notification = Notification(ticket_id, user, 'Update')
        try:
            notification.insert()
        except:
            print(sys.exc_info())
            abort(500)

    #Insert record in comments
    c_id = db.session.query(func.max(Comment.c_id)).all()
    if c_id[0][0] == None:
        comment = Comment(1,ticket_id, userinfo['user_id'],t_update_date, " Updated ticket status to  " + t_status )
    else:
        comment = Comment(c_id[0][0]+1,ticket_id, userinfo['user_id'],t_update_date, " Updated ticket status to  " + t_status )
    
    try:
        comment.insert()
    except:
        print(sys.exc_info())
        abort(500)
    return redirect('/ticketdetails/'+ str(ticket_id)) 

def get_submitted_tickets():
    userinfo = session.get('profile')
    ticket = Ticket.query.join(Project, Ticket.p_id == Project.p_id)\
                    .add_columns(Ticket.t_id.label('id'),Ticket.t_title.label('title'), Ticket.t_desc.label('desc'), \
                        Ticket.assigned_user_id.label('user_id'), Project.p_name.label('p_id')\
                        ,Ticket.t_priority.label('priority'), Ticket.t_status.label('status'),Ticket.t_type.label('type')\
                            ,Ticket.t_create_date.label('create_date'), Ticket.t_close_date.label('close_date'))\
                                .filter(Ticket.submitter_email == userinfo['email']).all()
    return ticket