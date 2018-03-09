import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
import codecs
import json
import time

from flask_login import login_required, current_user
from app import db , app



def send_email(senders_email,recievers_email, senders_email_password, subject, html, email_text):
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

    try:
        print (current_user.employee.reporting_manager_id)
        text = "Request Pending"
        f = codecs.open("app/index.html", 'r')
        template = Template(f.read())
        html = template.render()
        subject = 'Alert - New plant intern added'
        send_email('arsalanjaved2010@outlook.com',recievers_email , 'arsalanA1', 'Check portal', html , text)
        print('Success sending notifications')
    except:
    	print('Faliure sending notifications')
