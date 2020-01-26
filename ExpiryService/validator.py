import logging


class Validator:
    """ class Validator to validate data from the API

    USAGE:
            validator = Validator()

    """
    def __init__(self):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('create class Validator')

    def provider(self, provider):
        """ checks if ExpiryService supports given provider

        :param provider: provider string
        :return: True or False
        """
        if provider in ("alditalk", "netzclub", "congstar"):
            return True
        else:
            return False

    def username(self, provider, username):
        """ checks if username of given provider is valid

        :param provider: provider string
        :param username: username string
        :return: True or False
        """

        if provider == 'alditalk':
            if username.isdigit():  # only mobile number
                return True
            else:
                return False
        elif provider == 'netzclub':  # mobile number and email
            if ((username.isdigit()) or ("@" in username)):
                return True
            else:
                return False
        elif provider == 'congstar':
            return True

    def balance(self, balance):
        """ checks if balance is positive

        :param balance: string of minimum credit balance
        :return: True or False
        """

        if float(balance) >= 0.0:
            return True
        else:
            return False

    def notifyer(self, notifyer):
        """ checks if notifyer includes the char '@'

        :param notifyer: notifyer string
        :return: return True or False
        """

        if '@' in notifyer:
            return True
        else:
            return False

