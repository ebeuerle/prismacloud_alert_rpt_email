import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailHelper(object):
    def __init__(self):
        self.msg = MIMEMultipart()
        self.from_address = "XXXXX@gmail.com"
        self.to_address = "XXXXX@gmail.com"
        self.email_srv = "smtp.gmail.com"
        self.email_srv_port = "587"
        self.username = "XXXXX@gmail.com"
        self.password = "XXXXXXXX"

    def send_email(self, subject, bodycontent):
        self.msg['From'] = self.from_address
        self.msg['To'] = self.to_address
        self.msg['Subject'] = subject

        self.msg.attach(MIMEText(bodycontent, 'plain'))

        server = smtplib.SMTP(self.email_srv, self.email_srv_port)
        server.starttls()
        server.login(self.username, self.password)
        text = self.msg.as_string()
        server.sendmail(self.from_address, self.to_address.split(','), text)
        server.quit()