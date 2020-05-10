import logging

from ExpiryService.db import DBConnector, DBInserter, DBFetcher
from ExpiryService.db import DBCreator, Schema, Table, Column
from ExpiryService.exceptions import DBConnectorError


class DBHandler:
    """ base class DBHandler to provide database actions for subclasses

    USAGE:
            dbhandler = DBHandler()

    """

    def __init__(self, **dbparams):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('Create class DBHandler')

        self.database_table = "ExpiryService"

        # check db params
        if (('host' and 'port' and 'username' and 'password' and 'dbname') in dbparams.keys()) and \
                (all(value is not None for value in dbparams.values())):
            self.db_host = dbparams['host']
            self.db_port = dbparams['port']
            self.db_username = dbparams['username']
            self.db_password = dbparams['password']
            self.db_name = dbparams['dbname']

            # connect to postgres database
            if DBConnector.connect_psycopg(host=self.db_host, port=self.db_port, username=self.db_username,
                                           password=self.db_password, dbname=self.db_name, minConn=1, maxConn=39):

                self.dbcreator = DBCreator()
                self.dbinserter = DBInserter()
                self.dbfetcher = DBFetcher()

                self.postgres = True
                self.expiryservice_schema = "expiryservice"

                # at start create all necessary tables for ExpiryService
                self._create_local_db_tables()

            else:
                self.logger.error("DBHandler could not connect to the postgres database")
                raise DBConnectorError("DBHandler could not connect to the postgres database")
        else:
            path = '/var/log/ExpiryService/ExpiryService.db'

            if DBConnector.connect_sqlite(path=path):

                self.dbcreator = DBCreator()
                self.dbinserter = DBInserter()
                self.dbfetcher = DBFetcher()

                self.postgres = False
                self.expiryservice_schema = "main"

                # at start create all necessary tables for ExpiryService
                self._create_local_db_tables()
            else:
                self.logger.error("DBHandler could not connect to the sqlite database")
                raise DBConnectorError("DBHandler could not connect to the sqlite database")

    def _create_local_db_tables(self):
        """ creates the local database tables

        """
        # create schema if not exists expiryservice
        if self.postgres:
            self.logger.info("Create Schema {}".format(self.expiryservice_schema))
            self.dbcreator.build(obj=Schema(name=self.expiryservice_schema))

        # create table if not exists
        self.logger.info("create Table {}".format(self.database_table))
        self.dbcreator.build(obj=Table(self.database_table, Column(name="provider", type="text"),
                                                            Column(name="username", type="text"),
                                                            Column(name="password", type="text"),
                                                            Column(name="min_balance", type="real"),
                                                            Column(name="usage", type="text"),
                                                            Column(name="notifyer", type="text"),
                                                            Column(name="last_reminder", type="text"),
                                                            Column(name="reminder_delay", type="text"),
                                       schema=self.expiryservice_schema))
