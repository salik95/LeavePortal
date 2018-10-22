import smtplib
from email.mime.multipart import MIMEMultipart 
from email.mime.application import MIMEApplication
from email import encoders

from email.mime.text import MIMEText
from jinja2 import Template
import codecs
import json
import time
from flask import request, jsonify, url_for
from app.models import *
from flask_login import login_required, current_user
from app import db , app
import logging 
from threading import Thread




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



def notify(receiver_id = None, send_hr = None, send_gm=None , subject=None , body=None  
    ,send_director=None ) :



    messages = {
        'Encashment request':'Encashment request is pending',
        'Encashment Approved': 'Your encashment request has been approved ',
        'Encashment Form':' ',
        'Encashment Unapproved':'Your encashment request has not been approved',
        'Leave Approved':'Your leave request has been approved ',  
        'Leave Unapproved':'Your leave request has not been approved',
        'Leave Request':'There is a pending leave request',
        'Welcome To HOH Leave Portal': ' '
    }
    try:

        text = subject
        f = codecs.open("app/views/email_templates/general.html", 'r')
        template = Template(f.read())
        subject = subject
        email = Configuration.query.filter_by(key='email_address').first().value
        password = Configuration.query.filter_by(key='password').first().value


        if receiver_id!= None:
            receiver_id = int(receiver_id)
            recievers_email = User.query.get(receiver_id).email
            if subject == 'Welcome To HOH Leave Portal':
                messages['Welcome To HOH Leave Portal'] = 'Your email is '+ recievers_email + ' and your password is ' + body
            html = template.render(main_body = messages[subject] , link_for_app=url_for('dashboard' , _external=True) , subject=subject)
            send_email(email , password , recievers_email , subject, html , text)
            print('Success sending ' , recievers_email ) 
        
            
        if send_hr!= None:
            recievers_email = User.query.filter_by(role='HR Manager').first().email
            html = template.render(main_body = messages[subject] , link_for_app=url_for('dashboard' , _external=True) , subject=subject)
            send_email(email , password , recievers_email , subject, html , text)
            print('Success sending ' , recievers_email ) 

        if send_gm!= None:
            recievers_email = User.query.filter_by(role='General Manager').first().email
            html = template.render(main_body = messages[subject] , link_for_app=url_for('dashboard' , _external=True) , subject=subject)
            send_email(email , password , recievers_email , subject, html , text)
            print('Success sending ' , recievers_email ) 
        if send_director!= None:
            recievers_email = User.query.filter_by(role='Director').first().email            
            html = template.render(main_body = messages[subject] , link_for_app=url_for('dashboard' , _external=True) , subject=subject)
            send_email(email , password , recievers_email , subject, html , text)
            print('Success sending ' , recievers_email ) 
        


    except:
        logging.exception('Faliure sending notifications')





