import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
import os

class EmailManager:
    def __init__(self, log_func=None):
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.email = os.environ["SMTP_EMAIL"]
        self.password = os.environ["APP_PASSWORD"]
        self.log_func = log_func or (lambda msg: print(msg))  # fallback log

    def send(self, to, subject, templateName, context):
        try:
            template = self.env.get_template(template_name)
            html = template.render(context)

            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email
            msg['To'] = to
            msg.attach(MIMEText(html, 'html'))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(self.email, self.password)
                smtp.sendmail(self.email, to, msg.as_string())

            self.log_func(f"✅ Mail sent to {to}")
            return True

        except Exception as e:
            self.log_func(f"❌ Email send failed for {to}\n{e}")
            return False
