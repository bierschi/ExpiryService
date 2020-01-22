import ssl
import logging
import smtplib
from email.message import EmailMessage


class Mail:
    """ class Mail to provide sending expiry notification to specific email address

    USAGE:
            mail = Mail(smtp_server="smtp.web.de", port=587, sender=sender@web.de, receiver=receiver@web.de, debug=False)
            mail.login(username='', password='')
            mail.send()
    """
    def __init__(self, smtp_server, port, sender, debug=False):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('create class Mail')

        self.smtp_server = smtp_server
        self.port = port
        self.sender = sender

        self.server = smtplib.SMTP(self.smtp_server, self.port)
        self.context = ssl.create_default_context()
        self.server.starttls(context=self.context)

        if debug:
            self.server.set_debuglevel(True)

        self.msg = EmailMessage()
        self.msg['From'] = self.sender

    def __del__(self):
        """ destructor

        """
        if self.server:
            self.server.close()

    def login(self, username, password):
        """ login to email account with username and password

        """
        self.server.login(user=username, password=password)

    def set_subject(self, subject):
        """ sets the subject for the email

        :param subject: subject in email
        """
        self.msg['Subject'] = subject

    def set_body(self, body):
        """ sets the body for the email

        :param body: body content in email
        """
        self.msg.set_content(body)

    def send(self, receiver):
        """ sends the email

        """
        self.msg['To'] = receiver
        self.server.sendmail(self.sender, receiver, self.msg.as_string())

