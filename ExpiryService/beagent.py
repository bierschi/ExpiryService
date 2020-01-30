import logging
import threading
from ExpiryService.dbhandler import DBHandler
from ExpiryService.notification import Mail
from ExpiryService.providers import Provider, AldiTalk, Netzclub
from ExpiryService.exceptions import ProviderInstanceError, ProviderLoginError
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
                self.mail = Mail(smtp_server=self.smtp, port=self.port)
                self.mail.login(self.sender, self.password)
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

    def __get_registered_providers(self):
        """ get all registered providers in database table

        :return: list of registered providers
        """

        sql = "select * from {}".format(self.database_table)

        try:
            providers = self.dbfetcher.all(sql=sql)
        except Exception as e:
            self.logger.error("Exception! {}".format(e))
            return []

        return providers

    def create_provider_instance(self, provider):
        """ creates provider instance

        :return: instance of type provider
        """
        if provider == 'netzclub':
            return Netzclub()
        elif provider == 'alditalk':
            return AldiTalk()
        else:
            raise ProviderInstanceError("Could not create the provider instance")

    def login_provider(self, provider, username, password):
        """ login to the provider web page with username and password

        :return: logged in provider instance
        """

        if isinstance(provider, Provider):
            if provider.login(username=username, password=password):
                return provider
            else:
                raise ProviderLoginError("Failed to login to provider {}".format(provider))
        else:
            raise ProviderInstanceError("Could not return logged in provider instance")

    def get_consumption_data(self, provider):
        """

        :return:
        """
        return provider.current_consumption()

    def send_notification_mail(self, receivers, consumption_data):
        """

        :param receivers:
        :param consumption_data:
        :return:
        """
        pass

    def __run(self):
        """

        :return:
        """

        while self.__running:

            registered_provider_list = self.__get_registered_providers()
            if len(registered_provider_list) > 0:
                for registered_provider in registered_provider_list:
                    try:
                        provider_instance = self.create_provider_instance(provider=registered_provider[0])
                        logged_in_provider = self.login_provider(provider=provider_instance, username=registered_provider[1], password=registered_provider[2])
                        print(self.get_consumption_data(provider=logged_in_provider))

                    except ProviderInstanceError:
                        pass
                    except ProviderLoginError:
                        pass
            else:
                self.logger.error("registered provider list is empty!")
            sleep(100)
