import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
import os
from .Databaseconfig import ConfessServer

env = Environment(loader=FileSystemLoader('templates'))
confess_server = ConfessServer()

EMAIL = os.environ["SMTP_EMAIL"]
PASSWORD = os.environ["APP_PASSWORD"]

def sendEmailTemplate(to, subject, templateName, context):
    try:
        # Render email template
        template = env.get_template(templateName)
        html = template.render(context)

        # Build email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL
        msg['To'] = to
        msg.attach(MIMEText(html, 'html'))

        # Send email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL, PASSWORD)
            smtp.sendmail(EMAIL, to, msg.as_string())

        # Log success
        confess_server.send_telegram_log(message=f"✅ Mail has been sent to {to}")
        return True

    except Exception as e:
        # Log error
        confess_server.send_telegram_log(message=f"❌ Error in sending email to {to}\n{e}")
        return False
