import logging
import argparse
import configparser
from ExpiryService.routes.router import Router
from ExpiryService.api import APIHandler
from ExpiryService.utils import Logger
from ExpiryService.beagent import BEAgent
from ExpiryService import ROOT_DIR

config = configparser.ConfigParser()
config.read(ROOT_DIR + '/config/cfg.ini')


class ExpiryService:

    def __init__(self, name, frontend=True, version=1, **dbparams):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('create class ExpiryService')

        self.name = name
        self.frontend = frontend
        self.version = 'v' + str(version)

        # instance for the backend agent
        self.beagent = BEAgent(**dbparams)

        # handler for specific api calls
        self.api = APIHandler()

        # router instance for mapping endpoints with handler function
        self.router = Router(name=self.name)

        if self.frontend:
            self.router.add_endpoint('/', 'index', method="GET", handler=self.api.index)

        # api routes
        self.router.add_endpoint(endpoint='/api/' + self.version + '/providers/', endpoint_name='get_providers', method="GET", handler=self.api.get_providers)
        self.router.add_endpoint(endpoint='/api/' + self.version + '/provider/', endpoint_name='add_provider', method="POST", handler=self.api.add_provider)
        self.router.add_endpoint(endpoint='/api/' + self.version + '/provider/', endpoint_name='delete_provider', method="DELETE", handler=self.api.delete_provider)

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
    parser = argparse.ArgumentParser(description="Arguments for application ExpiryService")
    # arguments for the application
    parser.add_argument('--host',       type=str, help='hostname for the application')
    parser.add_argument('--port',       type=int, help='port for the application')
    parser.add_argument('--log-folder', type=str, help='log folder for application ExpiryService')
    # arguments for the postgres database
    parser.add_argument('--dbhost',     type=str, help='hostname to connect to the database')
    parser.add_argument('--dbport',     type=str, help='port to connect to the database')
    parser.add_argument('--dbuser',     type=str, help='user of the database')
    parser.add_argument('--dbpassword', type=str, help='password from the user')
    parser.add_argument('--dbname',     type=str, help='database name')

    args = parser.parse_args()

    if args.host is None:
        host = '0.0.0.0'
    else:
        host = args.host

    if args.port is None:
        port = 8090
    else:
        port = args.port

    if args.log_folder is None:
        log_folder = '/var/log/'
    else:
        log_folder = args.log_folder

    dbparams = {}
    if (args.dbhost and args.dbport and args.dbuser and args.dbpassword and args.dbname) is None:
        print("load database settings from config file")
    else:
        host = args.dbhost
        port = args.dbport
        username = args.dbuser
        password = args.dbpassword
        dbname = args.dbname
        dbparams = {'host': host, 'port': port, 'username': username, 'password': password, 'dbname': dbname}

    # set up logger instance
    logger = Logger(name='ExpiryService', level='info', log_folder=log_folder)
    logger.info("start application ExpiryService")

    # create application instance
    expiryservice = ExpiryService(name="ExpiryService", frontend=True, **dbparams)

    # run the application
    expiryservice.run(host=host, port=port)


if __name__ == '__main__':
    main()
