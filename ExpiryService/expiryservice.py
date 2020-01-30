import logging
import argparse
import configparser
from ExpiryService.routes.router import Router
from ExpiryService.api import APIHandler
from ExpiryService.utils import Logger
from ExpiryService.beagent import BEAgent
from ExpiryService import ROOT_DIR, __version__

config = configparser.ConfigParser()
config.read(ROOT_DIR + '/config/cfg.ini')


class ExpiryService:

    def __init__(self, name, postgres=False, frontend=True, version=1, **params):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('create class ExpiryService')

        self.name = name
        self.frontend = frontend
        self.version = 'v' + str(version)

        # instance for the backend agent
        self.beagent = BEAgent(postgres=postgres, **params)

        # handler for specific api calls
        self.api = APIHandler()

        # router instance for mapping endpoints with handler function
        self.router = Router(name=self.name)

        if self.frontend:
            self.router.add_endpoint('/', 'index', method="GET", handler=self.api.index)

        ## api routes
        # providers
        self.router.add_endpoint(endpoint='/api/' + self.version + '/provider/', endpoint_name='get_provider',
                                 method="GET",    handler=self.api.get_provider)
        self.router.add_endpoint(endpoint='/api/' + self.version + '/provider/',  endpoint_name='update_provider',
                                 method="POST",   handler=self.api.add_provider)
        self.router.add_endpoint(endpoint='/api/' + self.version + '/provider/',  endpoint_name='delete_provider',
                                 method="DELETE", handler=self.api.delete_provider)
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

    def run(self, host='0.0.0.0', port=None, debug=None):
        """ runs the ExpiryService application on given port

        :param host: default hostname
        :param port: port for the webserver
        :param debug: debug mode true or false
        """
        self.beagent.start()
        self.router.run(host=host, port=port, debug=debug)


def main():

    # parse arguments
    parser = argparse.ArgumentParser(description="Command line arguments for the application ExpiryService")
    # arguments for the application
    parser.add_argument('-H', '--host',       type=str, help='Hostname for the application')
    parser.add_argument('-P', '--port',       type=int, help='Port for the application')
    parser.add_argument('-L', '--log-folder', type=str, help='Log folder for the application ExpiryService')

    # arguments for the postgres database
    parser.add_argument('-DBH', '--dbhost',     type=str, help='Hostname for the database connection')
    parser.add_argument('-DBP', '--dbport',     type=int, help='Port for the database connection')
    parser.add_argument('-DBU', '--dbuser',     type=str, help='User for the database connection')
    parser.add_argument('-DBp', '--dbpassword', type=str, help='Password for the database connection')
    parser.add_argument('-DB',  '--dbname',     type=str, help='Database name')

    # arguments for the mail server
    parser.add_argument('-MS', '--Msmtp',      type=str, help='SMTP email server')
    parser.add_argument('-MP', '--Mport',      type=int, help='SMTP Port')
    parser.add_argument('-MSe', '--Msender',   type=str, help='Sender email address')
    parser.add_argument('-MPa', '--Mpassword', type=str, help='Sender email address password')

    # arguments for telegram notification
    # TODO

    parser.add_argument('-v', '--version', action='version', version=__version__, help='show the current version')
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

    if (args.dbhost and args.dbport and args.dbuser and args.dbpassword and args.dbname) is None:
        print("Local sqlite database will be used")
        postgres = False
        params.setdefault('database', {'host': args.dbhost, 'port': args.dbport, 'username': args.dbuser, 'password':
            args.dbpassword, 'dbname': args.dbname})
    else:
        host = args.dbhost
        port = args.dbport
        username = args.dbuser
        password = args.dbpassword
        dbname = args.dbname
        postgres = True
        params.setdefault('database', {'host': host, 'port': port, 'username': username, 'password': password,
                                       'dbname': dbname})

    if (args.Msmtp and args.Mport and args.Msender and args.Mpassword) is None:
        print("No mail server params available")
        params.setdefault('mail', {'smtp': args.Msmtp, 'port': args.Mport, 'sender': args.Msender, 'password': args.Mpassword})
    else:
        nsmtp     = args.Nsmtp
        nport     = args.Nport
        nsender   = args.Nsender
        npassword = args.Npassword

        params.setdefault('mail', {'smtp': nsmtp, 'port': nport, 'sender': nsender, 'password': npassword})

    # set up logger instance
    logger = Logger(name='ExpiryService', level='info', log_folder=log_folder)
    logger.info("start application ExpiryService")

    # create application instance
    expiryservice = ExpiryService(name="ExpiryService", postgres=postgres, frontend=False, **params)

    # run the application
    expiryservice.run(host=host, port=port)


if __name__ == '__main__':
    main()
