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
        self.log = log_func or (lambda msg: print("[EmailLog]", msg))

    def send(self, to, subject, templateName, context):
        try:
            template = self.env.get_template(templateName)
            html = template.render(context)

            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = formataddr(("TEAM CONFESS", self.email))
            msg['To'] = to
            msg.attach(MIMEText(html, 'html'))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(self.email, self.password)
                smtp.sendmail(self.email, to, msg.as_string())
            self.log(f"✅ Email sent to {to}")
            return True

        except Exception as e:
            self.log(f"❌ Email send failed to {to}: {e}")
            return False
