

import os, sys
from datetime import date


AUTH0_DOMAIN = 'bugtrac.us.auth0.com'
AUTH0_CLIENT_ID = 'r6I9WfxRdcE3m6XeST6tlHtwiCEKncJB'
#AUTH0_CALLBACK_URL= 'http://127.0.0.1:5000/callback'
#HEROKU DEPLOYMENT
AUTH0_CALLBACK_URL= 'https://bugtracker-stage.herokuapp.com/callback'
AUTH0_CLIENT_SECRET = 'KRIcQ3mcZ8YYAoAKObkRkV4QQrvKahUoe5VfnTWMKKHXFsN5SXmEIiOPS2ZrNtU-'
AUTH0_AUDIENCE = 'bugTrac'
STATUS = ['Open','Progress','Closed']
PRIORITY = ['High','Medium','Low']

today = date.today()
CURRENT_DATE = today.strftime("%d/%m/%Y")


DEMO_ADMIN_ID = 19