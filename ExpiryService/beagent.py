import logging
import threading
from ExpiryService.dbhandler import DBHandler
from ExpiryService.notification import Mail
from time import sleep


class BEAgent(DBHandler):

    def __init__(self, postgres=False, **params):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('create class BEAgent')

        # get params
        self.dbparams = dict()
        self.dbparams.update(params['database'])
        self.mailparams = dict()
        self.mailparams.update(params['mail'])

        # init base class
        super().__init__(postgres=postgres, **self.dbparams)

        if ('smtp' and 'port' and 'sender' and 'password') in self.mailparams.keys():
            if (self.mailparams['smtp'] and self.mailparams['port'] and self.mailparams['sender'] and self.mailparams['password']) is not None:
                self.logger.info("Create mail server")
                self.smtp = self.mailparams['smtp']
                self.port = self.mailparams['port']
                self.sender = self.mailparams['sender']
                self.password = self.mailparams['password']
                self.mail = Mail(smtp_server=self.smtp, port=self.port, sender=self.sender)
            else:
                self.logger.error("Mail params are none")
        else:
            self.logger.error("No mail params provided")

        # create run thread
        self.__thread = threading.Thread(target=self.__run, daemon=False)
        self.__running = False

        # check if local database tables exists
        self._create_local_db_tables()

    def __del__(self):
        """ destructor

        """
        if self.__running:
            self.stop()

    def start(self, daemon=False):
        """ starts the beagent run thread

        """
        if self.__thread:

            if isinstance(daemon, bool):
                self.__thread.daemon = daemon
                self.__running = True
                self.__thread.start()

            else:
                raise TypeError("'daemon' must be type of boolean")

    def stop(self):
        """ stops the beagent run thread

        """
        if self.__thread:
            self.__running = False

    def __get_all_providers(self):
        """

        :return:
        """

        sql = "select * from {}".format(self.database_table)

        try:
            providers = self.dbfetcher.all(sql=sql)
        except Exception as e:
            self.logger.error("Exception! {}".format(e))
            return []

        return providers

    def __run(self):
        """

        :return:
        """

        while self.__running:
            #print("test")
            sleep(1)
            self.__get_all_providers()

