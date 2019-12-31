import logging
import configparser
from ExpiryService.db.connector import DBConnector
from ExpiryService.db.creator import DBCreator
from ExpiryService.db.fetcher import DBFetcher
from ExpiryService.db.inserter import DBInserter
from ExpiryService import ROOT_DIR


class DBHandler:
    """ base class DBHandler to provide database actions for subclasses

    USAGE:
            dbhandler = DBHandler()

    """
    def __init__(self, **dbparams):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('create class DBHandler')

        # load config file
        self.config = configparser.ConfigParser()
        self.config.read(ROOT_DIR + '/config/cfg.ini')

        if ('host' and 'port' and 'username' and 'password' and 'dbname') in dbparams.keys():
            self.db_host     = dbparams['host']
            self.db_port     = dbparams['port']
            self.db_username = dbparams['username']
            self.db_password = dbparams['password']
            self.db_name     = dbparams['dbname']
        else:
            # get database configs from cfg.ini
            self.db_host     = self.config.get('database', 'host')
            self.db_port     = self.config.getint('database', 'port')
            self.db_username = self.config.get('database', 'username')
            self.db_password = self.config.get('database', 'password')
            self.db_name     = self.config.get('database', 'dbname')

        DBConnector.connect_psycopg(host=self.db_host, port=self.db_port, username=self.db_username,
                                    password=self.db_password, dbname=self.db_name, minConn=1, maxConn=20)

        # instances for db actions
        self.dbcreator = DBCreator()
        self.dbfetcher = DBFetcher()
        self.dbinserter = DBInserter()

