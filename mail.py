import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Mailer:
    def __init__(self, sender_email, receiver_email):
        self.sender_email = sender_email
        self.receiver_email = receiver_email
        self.smtp_server = "localhost"
        self.smtp_port = 25

    def test(self, body):
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = self.receiver_email
        message["Subject"] = "test email"
        body = "This is a test email sent using Python and TLS."
        message.attach(MIMEText(body, "plain"))

        self.sender(message)


    def send_mail(self, subject, body):
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = self.receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        self.sender(message)


    def sender(self, message):
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.sendmail(self.sender_email, self.receiver_email, message.as_string())
            server.quit()
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")

