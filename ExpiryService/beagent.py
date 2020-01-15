import logging
import threading
from ExpiryService.dbhandler import DBHandler
from time import sleep


class BEAgent(DBHandler):

    def __init__(self, **dbparams):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('create class BEAgent')

        # init base class
        super().__init__(postgres=False, **dbparams)

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

    def __run(self):
        """

        :return:
        """

        while self.__running:
            #print("test")
            sleep(1)


