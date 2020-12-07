import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailHelper(object):
    def __init__(self):
        self.msg = MIMEMultipart()
        self.from_address = "eddie.beuerlein@gmail.com"
        self.to_address = "eddie.beuerlein@gmail.com"
        self.email_srv = "smtp.gmail.com"
        self.email_srv_port = "587"
        self.username = "eddie.beuerlein@gmail.com"
        self.password = "XXXXXXXX"

    def send_email(self, subject, bodycontent):
        self.msg['From'] = self.from_address
        self.msg['To'] = self.to_address
        self.msg['Subject'] = subject

        self.msg.attach(MIMEText(bodycontent, 'plain'))
        if self.email_srv_port == "465":
            server = smtplib.SMTP_SSL(self.email_srv, self.email_srv_port)
        elif self.email_srv_port == "587":
            server = smtplib.SMTP(self.email_srv, self.email_srv_port)
            server.starttls()
        else:
            server = smtplib.SMTP(self.email_srv, self.email_srv_port)
        server.login(self.username, self.password)
        text = self.msg.as_string()
        server.sendmail(self.from_address, self.to_address.split(','), text)
        server.quit()