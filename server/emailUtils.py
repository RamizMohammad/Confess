import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
import os
from .Databaseconfig import ConfessServer

env = Environment(loader=FileSystemLoader('templates'))
server = ConfessServer()

EMAIL = os.environ["SMTP_EMAIL"]
PASSWORD = os.environ["APP_PASSWORD"]

def sendEmailTemplate(to, subject, templateName, context):
    template = env.get_template(templateName)
    html = template.render(context)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['To'] = to
    msg.attach(MIMEText(html, 'html'))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, to, msg.as_string())
            return true
        server.send_telegram_log(message=f"Mail has been sent")
    except Exception as e:
        server.send_telegram_log(message=f"Error in sending email\n{e}")
        return false
