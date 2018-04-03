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



#notify(subject='Leave Request', receiver_id=current_user.employee.manager.id)

def notify(receiver_id = None, send_hr = None, send_gm=None , subject=None) :


    messages = {
        'Encashment request':'Encashment request',
        'Encashment Approved':'',
        'Encashment Form': '',
        'Encashment Unapproved': '',
        'Leave Approved':'',  
        'Leave Unapproved':'',
        'Leave Request':''
    }
    try:
        text = "request pending"
        f = codecs.open("app/views/email_templates/leave_request.html", 'r')
        template = Template(f.read())
        html = template.render(main_body = messages[subject] , link_for_app='google.com')
        subject = subject
        email = Configuration.query.filter_by(key='email_address').first().value
        password = Configuration.query.filter_by(key='password').first().value
        
        if receiver_id!= None:
            receiver_id = int(receiver_id)
            manager_user_id = Employees.query.get(int(receiver_id)).user_id
            reporting_manager_email = User.query.get(manager_user_id).email
            send_email(email , password , reporting_manager_email, subject, html , text)
            print('Success sending ' , reporting_manager_email )

        if send_hr!= None:
            hr_email = User.query.filter_by(role='HR Manager').first().email
            send_email(email , password , hr_email , subject, html , text)
            print('Success sending ' , hr_email ) 

        if send_gm!= None:
            gm_email = User.query.filter_by(role='General Manager').first().email
            send_email(email , password , gm_email , subject, html , text)
            print('Success sending ' , gm_email ) 


    except:
        logging.exception('Faliure sending notifications')

