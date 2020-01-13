import logging
import configparser
from ExpiryService.db.connector import DBConnector
from ExpiryService.db.creator import DBCreator, Table, Column
from ExpiryService.db.fetcher import DBFetcher
from ExpiryService.db.inserter import DBInserter
from ExpiryService import ROOT_DIR


class DBHandler:
    """ base class DBHandler to provide database actions for subclasses

    USAGE:
            dbhandler = DBHandler()

    """
    def __init__(self, postgres=False, **dbparams):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('create class DBHandler')

        # load config file
        self.config = configparser.ConfigParser()
        self.config.read(ROOT_DIR + '/config/cfg.ini')

        self.postgres = postgres

        # load config file
        self.config = configparser.ConfigParser()
        self.config.read(ROOT_DIR + '/config/cfg.ini')

        # get schema from cfg.ini
        self.database_table  = self.config.get('sqlite', 'table')

        if self.postgres is False:
            self.logger.info("create local sqlite database")
            self.db_name = self.config.get('sqlite', 'name')
            # instance for db connector
            DBConnector.connect_sqlite(path='/var/log/ExpiryService' + '/' + self.db_name + '.db')

        else:
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

    def _create_local_db_tables(self):
        """ creates the local database tables

        """

        # create table if not exists
        self.logger.info("create Table {}".format(self.database_table))
        self.dbcreator.build(obj=Table(self.database_table,   Column(name="provider", type="text"),
                                                              Column(name="username", type="text"),
                                                              Column(name="password", type="text"),
                                                              Column(name="min_balance", type="real"),
                                                              Column(name="url", type="text"),
                                                              Column(name="repetition_number", type="integer")))
