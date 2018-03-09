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
    server = smtplib.SMTP("smtp-mail.outlook.com",587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username,password)
    server.sendmail( senders_email, recievers_email ,msg.as_string())
    server.quit()

def notify(recievers_id):

    #try:
        reporting_manager =  current_user.employee.reporting_manager_id
        #print (reporting_manager)
        manager_user_id = Employees.query.get(int(reporting_manager)).user_id
        #employee_id = .user_id
        reporting_manager_email = User.query.get(manager_user_id).email

        text = "request pending"
        f = codecs.open("app/views/email_templates/leave_request.html", 'r')
        template = Template(f.read())
        html = template.render()
        subject = 'request pending'

        send_email(data_dict['senders_email'], data_dict['senders_email_password'], reporting_manager_email, subject, html , text)
        print('Success sending notify_new')
        
    #except:
    	#print('Faliure sending notifications')



def notify_new(intern_data):
  try:
    text = "Intern added"
    f = codecs.open("app/templates/notifications_email_template/plant-intern-add.html", 'r')
    template = Template(f.read())
    html = template.render(**intern_data)
    subject = 'Alert - New plant intern added'
    send_email(data_dict['senders_email'],data_dict['recievers_email'] , data_dict['senders_email_password'], subject, html , text)
    print('Success sending notify_new')
  except:
    print('Faliure sending notify_new')