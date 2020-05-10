import logging
import argparse

from ExpiryService.routes import Router
from ExpiryService.api import APIHandler
from ExpiryService.notification import ExpiryServiceTelegram
from ExpiryService.utils import Logger
from ExpiryService import ProviderCheck
from ExpiryService import __version__


class ExpiryService:
    """ class ExpiryService to setup all necessary instances for the application

    USAGE:
            expiryservice = ExpiryService()
            expiryservice.run()

    """
    def __init__(self, name, token, chatid, frontend=True, version=1, **params):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('Create class ExpiryService')

        self.name = name
        self.frontend = frontend
        self.version = 'v' + str(version)
        self.token = token
        self.chatid = chatid

        # handler for specific api calls
        self.api = APIHandler()

        # router instance for mapping endpoints with handler function
        self.router = Router(name=self.name)

        if self.frontend:
            self.router.add_endpoint('/', 'index', method="GET", handler=self.api.index)

        # setup api endpoints
        self.setup_api_endpoints()

        # instance for the providercheck agent
        self.providercheck = ProviderCheck(**params)

        if (self.token and self.chatid) is not None:
            # instance for telegram
            self.telegram = ExpiryServiceTelegram(token=self.token, chatid=self.chatid)

    def setup_api_endpoints(self):
        """ setup the api routes for the application

        """
        # providers
        self.router.add_endpoint(endpoint='/api/' + self.version + '/provider/', endpoint_name='get_provider',
                                 method="GET",    handler=self.api.get_provider)
        self.router.add_endpoint(endpoint='/api/' + self.version + '/provider/',  endpoint_name='update_provider',
                                 method="POST",   handler=self.api.add_provider)
        self.router.add_endpoint(endpoint='/api/' + self.version + '/provider/',  endpoint_name='delete_provider',
                                 method="DELETE", handler=self.api.delete_provider)
        self.router.add_endpoint(endpoint='/api/' + self.version + '/providers/',  endpoint_name='delete_providers',
                                 method="DELETE", handler=self.api.delete_providers)
        # balance
        self.router.add_endpoint(endpoint='/api/' + self.version + '/creditbalance/min/',  endpoint_name='get_creditbalance',
                                 method="GET",   handler=self.api.get_creditbalance)
        self.router.add_endpoint(endpoint='/api/' + self.version + '/creditbalance/min/',  endpoint_name='update_creditbalance',
                                 method="POST",   handler=self.api.update_creditbalance)
        self.router.add_endpoint(endpoint='/api/' + self.version + '/creditbalance/min/',  endpoint_name='delete_creditbalance',
                                 method="DELETE",   handler=self.api.delete_creditbalance)
        # notification
        self.router.add_endpoint(endpoint='/api/' + self.version + '/notification/mail/',  endpoint_name='get_mail_notification',
                                 method="GET",   handler=self.api.get_mail_notification)
        self.router.add_endpoint(endpoint='/api/' + self.version + '/notification/mail/',  endpoint_name='update_mail_notification',
                                 method="POST",   handler=self.api.register_mail_notification)
        self.router.add_endpoint(endpoint='/api/' + self.version + '/notification/mail/',  endpoint_name='delete_mail_notification',
                                 method="DELETE",   handler=self.api.delete_mail_notification)

        # reminder delay
        self.router.add_endpoint(endpoint='/api/' + self.version + '/notification/mail/reminder/', endpoint_name='get_mail_reminder_delay',
                                 method="GET", handler=self.api.get_mail_reminder_delay)
        self.router.add_endpoint(endpoint='/api/' + self.version + '/notification/mail/reminder/', endpoint_name='update_mail_reminder_delay',
                                 method="GET", handler=self.api.update_mail_reminder_delay)

    def run(self, host='0.0.0.0', port=None, debug=None):
        """ runs the ExpiryService application on given port

        :param host: default hostname
        :param port: port for the webserver
        :param debug: debug mode true or false
        """
        self.providercheck.start()
        self.router.run(host=host, port=port, debug=debug)


def main():
    usage1 = "USAGE: \n\t\t ExpiryService --host 127.0.0.1 --port 8091 --Msmtp smtp.web.de --Mport 587 --Msender " \
             "john@web.de --Mpassword jane"

    usage2 = "ExpiryService --host 127.0.0.1 --port 8091 --token a32raf32raf"

    description = "Receive notifications when provider services expires. \n\n {}\n         {}".format(usage1, usage2)

    # parse arguments
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # arguments for the application
    parser.add_argument('-H', '--host',         type=str, help='Hostname for the application', required=True)
    parser.add_argument('-P', '--port',         type=int, help='Port for the application', required=True)

    # arguments for the postgres database
    parser.add_argument('-DBH', '--dbhost',     type=str, help='Hostname for the database connection')
    parser.add_argument('-DBP', '--dbport',     type=int, help='Port for the database connection')
    parser.add_argument('-DBU', '--dbuser',     type=str, help='User for the database connection')
    parser.add_argument('-DBp', '--dbpassword', type=str, help='Password for the database connection')
    parser.add_argument('-DB',  '--dbname',     type=str, help='Database name')

    # arguments for the mail server
    parser.add_argument('-MS', '--msmtp',       type=str, help='SMTP email server')
    parser.add_argument('-MP', '--mport',       type=int, help='SMTP Port')
    parser.add_argument('-MSE', '--msender',    type=str, help='Sender email address')
    parser.add_argument('-MPA', '--mpassword',  type=str, help='Sender email address password')

    # arguments for the telegram notification
    parser.add_argument('-T', '--token',        type=str, help='Provide the telegram token')
    parser.add_argument('-C', '--chatid',        type=int, help='Telegram chat id')

    # argument for the logging folder
    parser.add_argument('-L', '--log-folder',   type=str, help='Log folder for the application')

    # argument for the current version
    parser.add_argument('-v', '--version',      action='version', version=__version__, help='Shows the current version')

    # parse all arguments
    args = parser.parse_args()

    params = dict()

    if args.host is None:
        host = '0.0.0.0'
    else:
        host = args.host

    if args.port is None:
        port = 8100
    else:
        port = args.port

    if args.log_folder is None:
        log_folder = '/var/log/'
    else:
        log_folder = args.log_folder

    # set database params
    params.setdefault('database', {'host': args.dbhost, 'port': args.dbport, 'username': args.dbuser,
                                   'password': args.dbpassword, 'dbname': args.dbname})

    # set mail params
    params.setdefault('mail', {'smtp': args.msmtp, 'port': args.mport, 'sender': args.msender, 'password': args.mpassword})

    # set up logger instance
    logger = Logger(name='ExpiryService', level='info', log_folder=log_folder)
    logger.info("Start Application ExpiryService")

    # create application instance
    expiryservice = ExpiryService(name="ExpiryService", token=args.token, chatid=args.chatid, frontend=False, **params)

    # run the application
    expiryservice.run(host=host, port=port)


if __name__ == '__main__':
    main()
