import ssl
import logging
import smtplib
from email.message import EmailMessage
from ExpiryService.exceptions import MailMessageError


class Mail:
    """ class Mail to provide sending expiry notification to specific email address

    USAGE:
            mail = Mail(smtp_server="smtp.web.de", port=587, debug=False)
            mail.login(username='', password='')
            mail.send()
    """
    def __init__(self, smtp_server, port, debug=False):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('create class Mail')

        self.smtp_server = smtp_server
        self.port = port
        self.sender = None
        self.server = smtplib.SMTP(self.smtp_server, self.port)
        self.context = ssl.create_default_context()
        self.server.starttls(context=self.context)

        if debug:
            self.server.set_debuglevel(True)

        self.msg = None

    def __del__(self):
        """ destructor

        """
        if self.server:
            self.server.close()

    def login(self, username, password):
        """ login to email account with username and password

        """
        self.sender = username
        self.server.login(user=self.sender, password=password)

    def new_message(self):
        """ creates a new EmailMessage object

        """
        self.msg = EmailMessage()
        if self.sender is not None:
            self.msg['From'] = self.sender
        else:
            pass

    def set_subject(self, subject):
        """ sets the subject for the email

        :param subject: subject in email
        """
        if self.msg is not None:
            self.msg['Subject'] = subject
        else:
            raise MailMessageError("No Mail Message was set!")

    def set_body(self, body):
        """ sets the body for the email

        :param body: body content in email
        """
        if self.msg is not None:
            self.msg.set_content(body)
        else:
            raise MailMessageError("No Mail Message was set!")

    def send(self, receiver):
        """ sends the email to the receiver

        """
        if self.msg is not None:
            self.msg['To'] = receiver
            self.server.sendmail(self.sender, receiver, self.msg.as_string())
            self.msg.clear()
        else:
            raise MailMessageError("No Mail Message was set!")
