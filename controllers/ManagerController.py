#################################################################################################
#                                                                                               #
#   Module          :    Manager Controller                                                     #
#   Operations      :                                                                           #
#   1.  Fetch all tickets               /manager/tickets                        Manager         #   
#   2.  Fetch tickets subtmitted        /manager/submittedtickets               Manager         #
#       by manager                                                                              #
#   3.  Projects under the manager      /manager/projects                       Manager         #
#   Last Update     :    Added function for updating tickets                                    #
#   Last Update date:    21 Dec 2020                                                            #
#                                                                                               #
#################################################################################################

from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session
from decimal import *
from app import app, db
import os, sys
from datetime import date, datetime
from sqlalchemy import text, func
from datetime import datetime

from models.TicketModel import Ticket
from models.ProjectModel import Project
from models.UserProjMapModel import Map_user_proj
from models.UsersModel import Users
from models.MonthConfigModel import Month_config

from controllers import NotificationController
from controllers import TicketController


@app.route('/manager-dashboard')
def get_manager_mainpage():
    userinfo = session.get('profile')

    if userinfo['role']!= 'Project Manager':
        abort(401)
    manager_email = userinfo['email']
    user_id = userinfo['user_id']
    #Get notifications
    notification_list = NotificationController.get_notifications(userinfo['user_id'])
    notification_count = len(notification_list)


    project_list = Project.query.join(Map_user_proj, Project.p_id == Map_user_proj.p_id)\
				.join(Users, Users.user_id == Map_user_proj.user_id)\
				.add_columns(Project.p_id,Project.p_name,Project.p_desc,Project.p_start_date,Project.p_end_date)\
				.filter(Users.user_email == manager_email).all()
    project = [Project.json_format(proj) for proj in project_list] 

    data = {
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "manager_mainpage",
        "notification" : notification_list,
        "notification_count" : notification_count,
        "project" : project
    }
    return render_template('manager-mainpage.html', data=data)

#################################################################################################
#   GET ALL TICKETS FOR PROJECTS UNDER MANAGER                                                  #
#   SERVES  :   mainpage.html (Manager View)                                                    #
#################################################################################################
@app.route('/manager/tickets', methods=['GET'])
def manager_get_tickets():
    userinfo = session.get('profile')
    if userinfo['role']!= 'Project Manager':
        abort(401)
    manager_email= userinfo['name']
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
                                                    WHERE  user_email = '""" + manager_email+ """') 
                                                    u 
                                                ON map.user_id = u.user_id) filter 
                            ON tick.p_id = filter.p_id 
                    INNER JOIN project proj 
                            ON tick.p_id = proj.p_id """)
    result = db.session.execute(sql)
    names = [row for row in result]
    ticket_value = [Ticket.array_to_json_format(row) for row in names]

    today = date.today()
    t_create_date = today.strftime("%d/%m/%Y")
    d1 = datetime.strptime(t_create_date, '%d/%m/%Y')
    for t in ticket_value:
        d2 = datetime.strptime(t['create_date'], '%d/%m/%Y')
        t['datediff'] = abs((d2 - d1).days)

    #Get notifications
    notification_list = NotificationController.get_notifications(userinfo['user_id'])
    notification_count = len(notification_list)
    data = {
        "ticket" : ticket_value,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "manager_tickets",
        "notification" : notification_list,
        "notification_count" : notification_count
    }

    return render_template('mainpage.html', data = data)


#################################################################################################
#   FETCH MANAGER'S SUBMITTED TICKETS                                                           #
#   SERVES  :   mainpage.html                                                                   #
#################################################################################################
@app.route('/manager/submittedtickets', methods=['GET'])
def get_manager_submitted_tickets():
    ticket = TicketController.get_submitted_tickets()
    userinfo = session.get('profile')
    if userinfo['role']!= 'Project Manager':
        abort(401)
    #Get notifications
    notification_list = NotificationController.get_notifications(userinfo['user_id'])
    notification_count = len(notification_list)

    data = {
        "ticket" : ticket,
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "submittedtickets",
        "notification" : notification_list,
        "notification_count" : notification_count
    }
    return render_template('mainpage.html', data = data)

#################################################################################################
#   GET MANAGER PROJECTS                                                                        #
#################################################################################################
@app.route('/manager/projects', methods=['GET'])
def manager_get_projects():
    userinfo = session.get('profile')
    if userinfo['role']!= 'Project Manager':
        abort(401)
    manager_email= userinfo['email']
    project_list = Project.query.join(Map_user_proj, Project.p_id == Map_user_proj.p_id)\
				.join(Users, Users.user_id == Map_user_proj.user_id)\
				.add_columns(Project.p_id,Project.p_name,Project.p_desc,Project.p_start_date,Project.p_end_date)\
				.filter(Users.user_email == manager_email).all()
    project = [Project.json_format(proj) for proj in project_list]   

    #Get notifications
    notification_list = NotificationController.get_notifications(userinfo['user_id'])
    notification_count = len(notification_list)
    data = {
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "projects",
        "project" : project,
        "notification" : notification_list,
        "notification_count" : notification_count
    }
    return render_template('mainpage.html', data = data)

#################################################################################################
#   GET DATAPOINTS FOR DASHBOARD LINE GRAPH                                                     #
#################################################################################################
@app.route("/manager-dashboard/project/<int:project_id>")
def get_project_chart(project_id):
    userinfo = session.get('profile')
    if userinfo['role']!= 'Project Manager':
        abort(401)
    user_id = userinfo['user_id']
    mth_id = datetime.now().month
    yr = datetime.now().year

    if project_id==0:
        query = text(""" SELECT mapid.mth_name          AS mth_name, 
                                mapid.p_id              AS p_id, 
                                COALESCE(filter.cnt, 0) AS cnt 
                            FROM   (SELECT config.mth_name, 
                                        config.mth_id, 
										config.year,
                                        proj.p_id 
                                    FROM   (select * from month_config where id <= (select id from month_config where mth_id = """+str(mth_id)+ """ and year= """ +str(yr)+""") and id >= (select id - 11 from month_config where mth_id = """+str(mth_id)+ """ and year= """ +str(yr)+""")) config 
                                        CROSS JOIN (SELECT p_id 
                                                    FROM   map_user_proj 
                                                    WHERE  user_id = """ +str(user_id)+"""
                                                            AND user_role = 'Project Manager') proj) mapid 
                                LEFT OUTER JOIN (SELECT Count(filter.t_id)              AS cnt, 
                                                        filter.p_id, 
                                                        Date_part('month', filter.date) AS month ,
														Date_part('year', filter.date) AS yr
                                                    FROM   (SELECT tick.t_id, 
                                                                tick.p_id, 
                                                                To_date(tick.t_create_date, 'DD/MM/YYYY') 
                                                                AS 
                                                                date 
                                                            FROM   ticket tick 
                                                            WHERE  p_id IN (SELECT p_id 
                                                                            FROM   map_user_proj 
                                                                            WHERE 
                                                                user_id = """ +str(user_id)+"""
                                                                AND user_role = 
                                                                    'Project Manager')) filter 
                                                    GROUP  BY filter.p_id, 
                                                            Date_part('month', filter.date),
															Date_part('year', filter.date)) filter 
                                                ON mapid.mth_id = filter.month 
												AND mapid.year = filter.yr
                                                AND mapid.p_id = filter.p_id """)
        result = db.session.execute(query)
        chart_data = [Month_config.json_format(row) for row in result]

        project_list_query = text("""SELECT proj.p_id   AS p_id, 
                                            proj.p_name AS p_name 
                                        FROM   project proj 
                                            INNER JOIN map_user_proj map 
                                                    ON proj.p_id = map.p_id 
                                        WHERE  map.user_id ="""+str(user_id)+"""
                                            AND map.user_role = 'Project Manager' """)
        result = db.session.execute(project_list_query)
        project_list = [Project.project_list_json_format(row) for row in result]


    else:
        query = text(""" SELECT mapid.mth_name          AS mth_name, 
                                mapid.p_id              AS p_id, 
                                COALESCE(filter.cnt, 0) AS cnt 
                            FROM   (SELECT config.mth_name, 
                                        config.mth_id, 
										config.year,
                                        proj.p_id 
                                    FROM   (select * from month_config where id <= (select id from month_config where mth_id = """+str(mth_id)+ """ and year= """ +str(yr)+""") and id >= (select id - 11 from month_config where mth_id = """+str(mth_id)+ """ and year= """ +str(yr)+""")) config 
                                        CROSS JOIN (SELECT """ +str(project_id)+""" as p_id) proj) mapid 
                                LEFT OUTER JOIN (SELECT Count(filter.t_id)              AS cnt, 
                                                        filter.p_id, 
                                                        Date_part('month', filter.date) AS month ,
														Date_part('year', filter.date) AS yr
                                                    FROM   (SELECT tick.t_id, 
                                                                tick.p_id, 
                                                                To_date(tick.t_create_date, 'DD/MM/YYYY') 
                                                                AS 
                                                                date 
                                                            FROM   ticket tick 
                                                            WHERE  p_id ="""+str(project_id)+ """) filter 
                                                    GROUP  BY filter.p_id, 
                                                            Date_part('month', filter.date),
															Date_part('year', filter.date)) filter 
                                                ON mapid.mth_id = filter.month 
												AND mapid.year = filter.yr
                                                AND mapid.p_id = filter.p_id """)
        result = db.session.execute(query)
        chart_data = [Month_config.json_format(row) for row in result]

        project_list_query = text("""SELECT proj.p_id   AS p_id, 
                                            proj.p_name AS p_name 
                                        FROM   project proj 
                                            INNER JOIN map_user_proj map 
                                                    ON proj.p_id = map.p_id 
                                        WHERE  map.user_id ="""+str(user_id)+"""
                                            AND map.p_id = """+str(project_id)+ """
                                            AND map.user_role = 'Project Manager' """)
        result = db.session.execute(project_list_query)
        project_list = [Project.project_list_json_format(row) for row in result]


    data = {
            "chart_data": chart_data,
            "project_list": project_list
        }
    return data


#################################################################################################
#   GET DATAPOINTS FOR DASHBOARD CARDS                                                          #
#################################################################################################
@app.route('/manager-dashboard-cards/<int:project_id>')
def get_manager_mainpage_cards(project_id): 
    userinfo = session.get('profile')
    if userinfo['role']!= 'Project Manager':
        abort(401)
    manager_email = userinfo['email']
    user_id = userinfo['user_id']
    if project_id == 0:
        #GET TOTAL OPEN TICKETS
        total_open_tickets = Ticket.query.join(Map_user_proj, Ticket.p_id == Map_user_proj.p_id)\
                                        .with_entities(func.count(Ticket.t_id).label('cnt'))\
                                                .filter(Map_user_proj.user_id == user_id)\
                                                    .filter(Map_user_proj.user_role=='Project Manager')\
                                                        .filter(Ticket.t_status == 'Open')\
                                                        .all()



        #UNASSINGED TICKETS
        unassigned_tickets = Ticket.query.join(Map_user_proj, Ticket.p_id == Map_user_proj.p_id)\
                                        .with_entities(func.count(Ticket.t_id).label('cnt'))\
                                                .filter(Map_user_proj.user_id == user_id)\
                                                    .filter(Map_user_proj.user_role=='Project Manager')\
                                                        .filter(Ticket.assigned_user_id == 0)\
                                                        .all()
        
        #IN PROGRESS TICKETS
        in_progress_tickets = Ticket.query.join(Map_user_proj, Ticket.p_id == Map_user_proj.p_id)\
                                        .with_entities(func.count(Ticket.t_id).label('cnt'))\
                                                .filter(Map_user_proj.user_id == user_id)\
                                                    .filter(Map_user_proj.user_role=='Project Manager')\
                                                        .filter(Ticket.t_status == 'Progress')\
                                                        .all()

        #AVERAGE TIME TAKEN TO RESOLVE PER TICKET
        query = text("""select CAST(avg_ticket_time as INTEGER) from 
                        ( select avg(diff) as avg_ticket_time from 
                            (select (to_date(t_close_date,'DD/MM/YYYY') - to_date(t_create_date,'DD/MM/YYYY')) as diff 
                                from ticket where t_status='Closed')x)y;""")
        result = db.session.execute(query)
        avg_time = [row for row in result]

    else:
        #GET TOTAL OPEN TICKETS
        total_open_tickets = Ticket.query.join(Map_user_proj, Ticket.p_id == Map_user_proj.p_id)\
                                        .with_entities(func.count(Ticket.t_id).label('cnt'))\
                                                .filter(Map_user_proj.user_id == user_id)\
                                                    .filter(Map_user_proj.user_role=='Project Manager')\
                                                        .filter(Map_user_proj.p_id == project_id)\
                                                        .filter(Ticket.t_status == 'Open')\
                                                        .all()



        #UNASSINGED TICKETS
        unassigned_tickets = Ticket.query.join(Map_user_proj, Ticket.p_id == Map_user_proj.p_id)\
                                        .with_entities(func.count(Ticket.t_id).label('cnt'))\
                                                .filter(Map_user_proj.user_id == user_id)\
                                                    .filter(Map_user_proj.user_role=='Project Manager')\
                                                        .filter(Map_user_proj.p_id == project_id)\
                                                        .filter(Ticket.assigned_user_id == 0)\
                                                        .all()
        
        #IN PROGRESS TICKETS
        in_progress_tickets = Ticket.query.join(Map_user_proj, Ticket.p_id == Map_user_proj.p_id)\
                                        .with_entities(func.count(Ticket.t_id).label('cnt'))\
                                                .filter(Map_user_proj.user_id == user_id)\
                                                    .filter(Map_user_proj.user_role=='Project Manager')\
                                                        .filter(Map_user_proj.p_id == project_id)\
                                                        .filter(Ticket.t_status == 'Progress')\
                                                        .all()

        #AVERAGE TIME TAKEN TO RESOLVE PER TICKET
        query = text("""select CAST(avg_ticket_time as INTEGER) from 
                        ( select avg(diff) as avg_ticket_time from 
                            (select (to_date(t_close_date,'DD/MM/YYYY') - to_date(t_create_date,'DD/MM/YYYY')) as diff 
                                from ticket where t_status='Closed' and p_id = """ +str(project_id)+""")x)y;""")
        result = db.session.execute(query)
        avg_time = [row for row in result]

    data = {
        "userinfo" : userinfo,
        "role" : userinfo['role'],
        "username" : userinfo['nickname'],
        "page" : "manager_mainpage_cards",
        "total_open_tickets" : total_open_tickets[0][0],
        "unassigned_tickets": unassigned_tickets[0][0],
        "in_progress_tickets":in_progress_tickets[0][0],
        "avg_time":avg_time[0][0]
    }
    return data


#################################################################################################
#   GET DATAPOINTS FOR DASHBOARD PIE CHART                                                      #
#################################################################################################
@app.route('/manager-dashboard-piechart/<int:project_id>')
def get_manager_mainpage_piechart(project_id): 
    userinfo = session.get('profile')
    if userinfo['role']!= 'Project Manager':
        abort(401)
    manager_email = userinfo['email']
    user_id = userinfo['user_id']
    mth_id = str(datetime.now().month)
    yr = str(datetime.now().year)
    if project_id == 0:
        query = text(""" SELECT index.left_pri   AS priority,
                            COALESCE(cnt, 0) AS cnt 
                        FROM   (SELECT 'Low' AS left_pri 
                                UNION 
                                SELECT 'Medium' 
                                UNION 
                                SELECT 'High')index 
                            LEFT OUTER JOIN (SELECT filter.t_priority AS priority, 
                                                    Count(*)          AS cnt 
                                                FROM   (SELECT tick.t_id, 
                                                            tick.p_id, 
                                                            tick.t_priority, 
                                                            To_date(tick.t_create_date, 'DD/MM/YYYY') 
                                                            AS 
                                                            date 
                                                        FROM   ticket tick 
                                                        WHERE  p_id IN (SELECT p_id 
                                                                        FROM   map_user_proj 
                                                                        WHERE  user_id = """+str(user_id)+""" 
                                                                            AND user_role = 
                                                                                'Project Manager')) 
                                                    filter 
                                                    INNER JOIN (SELECT * 
                                                                FROM   month_config 
                                                                WHERE  id <= (SELECT id 
                                                                                FROM   month_config 
                                                                                WHERE  mth_id = """+mth_id+""" 
                                                                                        AND year = """+yr+""") 
                                                                        AND id >= (SELECT id - 11 
                                                                                    FROM   month_config 
                                                                                    WHERE 
                                                                            mth_id = """+mth_id+""" 
                                                                            AND year = """+yr+""")) 
                                                                config 
                                                            ON Date_part('month', filter.date) = 
                                                                config.mth_id 
                                                                AND Date_part('year', filter.date) = 
                                                                    config.year 
                                                GROUP  BY filter.t_priority)tab 
                                            ON index.left_pri = tab.priority  """)
        result = db.session.execute(query)
        piechart_data = [Month_config.piechart_json(row) for row in result]

    else:
        query = text(""" SELECT index.left_pri   AS priority,
                            COALESCE(cnt, 0) AS cnt 
                        FROM   (SELECT 'Low' AS left_pri 
                                UNION 
                                SELECT 'Medium' 
                                UNION 
                                SELECT 'High')index 
                            LEFT OUTER JOIN (SELECT filter.t_priority AS priority, 
                                                    Count(*)          AS cnt 
                                                FROM   (SELECT tick.t_id, 
                                                            tick.p_id, 
                                                            tick.t_priority, 
                                                            To_date(tick.t_create_date, 'DD/MM/YYYY') 
                                                            AS 
                                                            date 
                                                        FROM   ticket tick 
                                                        WHERE  p_id ="""+str(project_id)+ """) 
                                                    filter 
                                                    INNER JOIN (SELECT * 
                                                                FROM   month_config 
                                                                WHERE  id <= (SELECT id 
                                                                                FROM   month_config 
                                                                                WHERE  mth_id = """+mth_id+""" 
                                                                                        AND year = """+yr+""") 
                                                                        AND id >= (SELECT id - 11 
                                                                                    FROM   month_config 
                                                                                    WHERE 
                                                                            mth_id = """+mth_id+""" 
                                                                            AND year = """+yr+""")) 
                                                                config 
                                                            ON Date_part('month', filter.date) = 
                                                                config.mth_id 
                                                                AND Date_part('year', filter.date) = 
                                                                    config.year 
                                                GROUP  BY filter.t_priority)tab 
                                            ON index.left_pri = tab.priority  """)
        result = db.session.execute(query)
        piechart_data = [Month_config.piechart_json(row) for row in result]
    data = {
            "piechart_data": piechart_data
        }
    return data