import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
import codecs
import json
import time
from flask import request, jsonify
from app.models import *
from flask_login import login_required, current_user
from app import db , app

import logging 


def send_email(senders_email, senders_email_password, recievers_email, subject, html, email_text):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = senders_email
    msg['To'] = recievers_email
    part1 = MIMEText(email_text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    username = str(senders_email) 
    password = str( senders_email_password)  
    server = smtplib.SMTP("smtp.office365.com",587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username,password)
    server.sendmail( senders_email, recievers_email ,msg.as_string())
    server.quit()

def notify(recievers_id = None, hr_email = None) :

    try:
        text = "request pending"
        f = codecs.open("app/views/email_templates/leave_request.html", 'r')
        template = Template(f.read())
        html = template.render()
        subject = 'request pending'

        email = Configuration.query.filter_by(key='email_address').first().value
        password = Configuration.query.filter_by(key='password').first().value
        
        if recievers_id!= None:
            reporting_manager =  Employees.query.get(int(recievers_id)).reporting_manager_id
            manager_user_id = Employees.query.get(int(reporting_manager)).user_id
            reporting_manager_email = User.query.get(manager_user_id).email
            send_email(email , password , reporting_manager_email, subject, html , text)
            print('Success sending ' , reporting_manager_email )

        elif hr_email!= None:
            send_email(email , password , hr_email , subject, html , text)
            print('Success sending ' , hr_email ) 
    except:
        logging.exception('Faliure sending notifications')

