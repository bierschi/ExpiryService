import logging
from threading import Thread
from time import sleep, time

from ExpiryService.dbhandler import DBHandler
from ExpiryService.notification import Mail
from ExpiryService.providers import Provider, AldiTalk, Netzclub
from ExpiryService.exceptions import ProviderInstanceError, ProviderLoginError
from ExpiryService.scheduler import Scheduler


class ProviderCheck(DBHandler, Thread):
    """ class ProviderCheck to check data from registered providers

    USAGE:
            providercheck = ProviderCheck(**params)
            providercheck.start()

    """
    def __init__(self, **params):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('Create class ProviderCheck')

        # get params
        self.dbparams = dict()
        self.dbparams.update(params['database'])
        self.mailparams = dict()
        self.mailparams.update(params['mail'])

        # init base classes
        DBHandler.__init__(self, **self.dbparams)
        Thread.__init__(self)

        self._running = True

        if ('smtp' and 'port' and 'sender' and 'password') in self.mailparams.keys():
            if (self.mailparams['smtp'] and self.mailparams['port'] and self.mailparams['sender'] and self.mailparams['password']) is not None:
                self.logger.info("Create mail server")
                self.smtp = self.mailparams['smtp']
                self.port = self.mailparams['port']
                self.sender = self.mailparams['sender']
                self.password = self.mailparams['password']
                self.mail = Mail(smtp_server=self.smtp, port=self.port)
            else:
                self.logger.error("Mail params are None")
        else:
            self.logger.error("No mail params provided")

        # create scheduler instance
        self.scheduler = Scheduler()

        # providers weekly check
        self.scheduler.periodic(3600, self.check_data_from_providers, False)

        # provider data check interval, 10min default
        self.provider_check_interval = 600

    def run(self) -> None:
        """ run thread for beagent

        """

        while self._running:

            sleep(self.provider_check_interval)
            self.check_data_from_providers(notify=False)

    def __get_registered_providers(self):
        """ get all registered providers in database table

        :return: list of registered providers
        """

        sql = "select * from {}".format(self.database_table)

        try:
            providers = self.dbfetcher.all(sql=sql)
        except Exception as e:
            self.logger.error("Internal Database Error. {}".format(e))
            return []

        return providers

    def __create_provider_instance(self, provider):
        """ creates provider instance

        :return: instance of type provider
        """
        if provider == 'netzclub':
            return Netzclub()
        elif provider == 'alditalk':
            return AldiTalk()
        else:
            raise ProviderInstanceError("Could not create the provider instance")

    def __login_provider(self, provider, username, password):
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

    def get_last_reminder_ts(self, provider, username):
        """ get last reminder timestamp from database

        :return: last reminder timestamp
        """

        reminder_sql = "select last_reminder from {} where provider = %s and username = %s".format(self.database_table)

        try:
            last_reminder = self.dbfetcher.all(sql=reminder_sql, data=(provider, username))
            last_reminder = last_reminder[0][0]

            if last_reminder is not None:
                return last_reminder
            else:
                return last_reminder
        except Exception as e:
            self.logger.error("Internal Database Error. {}".format(e))
            return None

    def set_last_reminder_ts(self, provider, username):
        """ sets the last reminder timestamp in database table

        :param provider: provider name
        :param username: username
        """
        update_reminder_sql = "update {} set last_reminder = %s where provider = %s and username = %s".format(self.database_table)

        now_ts = time()
        try:
            self.dbinserter.row(sql=update_reminder_sql, data=(now_ts, provider, username))
        except Exception as ex:
            self.logger.error(ex)

    def get_reminder_delay(self, provider, username):
        """

        :return:
        """
        reminder_delay_sql = "select reminder_delay from {} where provider = %s and username = %s".format(self.database_table)

        try:
            reminder_delay = self.dbfetcher.all(sql=reminder_delay_sql, data=(provider, username))
            reminder_delay = reminder_delay[0][0]

            if reminder_delay is not None:
                print(reminder_delay)
                print(type(reminder_delay))
                pass
            else:
                pass
        except Exception as e:
            self.logger.error("Internal Database Error. {}".format(e))

    def get_consumption_data(self, provider):
        """ get the consumption data dict from given provider

        :return: consumption data dict
        """
        return provider.current_consumption()

    def get_data_usage_overview(self, provider):
        """ get the data usage overview from given provider

        :return: list of data usage
        """
        return provider.data_usage_overview()

    def is_creditbalance_under_min(self, provider, username, consumption):
        """ checks if the creditbalance has reached the database minimum balance

        :return: True if minimum was reached, else False
        """

        min_balance_sql = "Select min_balance from {} where provider = %s and username = %s".format(self.database_table)

        try:
            min_balance = self.dbfetcher.all(sql=min_balance_sql, data=(provider, username))
            min_balance = min_balance[0][0]
        except Exception as ex:
            self.logger.error("Internal Database Error. {}".format(ex))
            return False

        current_creditbalance = consumption['creditbalance']
        if "€" in current_creditbalance:
            current_creditbalance = current_creditbalance.replace("€", "")
        if "," in current_creditbalance:
            current_creditbalance = current_creditbalance.replace(",", ".")

        if float(current_creditbalance) <= min_balance:
            return True
        else:
            return False

    def prepare_creditbalance_min_mail(self, consumption):
        """ prepares the creditbalance minimum mail with consumption data

        :return: creditbalance minimum string
        """
        self.logger.info("Prepare the creditbalance minimum mail")

        consumption_str = "Name: {} \nNumber: {}\ncreditbalance: {}\nData Volume: {} {}\nEnd Date: {}".format(
            consumption['name'], consumption['number'], consumption['creditbalance'], consumption['remaining_volume'],
            consumption['total_volume'], consumption['end_date'])

        return consumption_str

    def prepare_notification_mail(self, consumption, data_usage):
        """ prepares the notification mail with consumption and data usage data

        :return: notification string
        """
        self.logger.info("Prepare weekly notification mail")

        consumption_str = "Name: {} \nNumber: {}\ncreditbalance: {}\nData Volume: {} {}\nEnd Date: {}".format(
            consumption['name'], consumption['number'], consumption['creditbalance'], consumption['remaining_volume'],
            consumption['total_volume'], consumption['end_date'])
        data_usage_str = "\n\n"
        for data_usage_month in data_usage['table_body']:
            data_usage_month_str = "{}: {}\n{}: {}\n{}: {}\n{}: {}\n{}: {}\n\n".format(
                data_usage['table_head'][0], data_usage_month[0],
                data_usage['table_head'][1], data_usage_month[1],
                data_usage['table_head'][2], data_usage_month[2],
                data_usage['table_head'][3], data_usage_month[3],
                data_usage['table_head'][4], data_usage_month[4])
            data_usage_str += data_usage_month_str

        return consumption_str + data_usage_str

    def send_notification_mail(self, receivers, subject_str, notification_str):
        """ sends the notification mail to given receivers

        :param receivers: receiver string from database
        :param subject_str: subject header string
        :param notification_str: notification str for email
        """
        receiver_list = receivers.split(';')
        for receiver in receiver_list:
            self.logger.info("Send Mail to {}".format(receiver))
            self.mail.new_message()
            self.mail.set_subject(subject_str)
            self.mail.set_body(str(notification_str))
            self.mail.send(username=self.sender, password=self.password, receiver=receiver)

    def check_data_from_providers(self, notify=False):
        """ checks data from registered database providers

        """
        # get all registered providers from database
        registered_provider_list = self.__get_registered_providers()

        if len(registered_provider_list) > 0:
            for registered_provider in registered_provider_list:
                try:
                    provider_instance = self.__create_provider_instance(provider=registered_provider[0])
                    logged_in_provider = self.__login_provider(provider=provider_instance,
                                                               username=registered_provider[1],
                                                               password=registered_provider[2])
                    # get data from providers
                    consumption = self.get_consumption_data(provider=logged_in_provider)
                    data_usage = self.get_data_usage_overview(provider=logged_in_provider)

                    # send mail if creditbalance minimum reached
                    if self.is_creditbalance_under_min(provider=registered_provider[0], username=registered_provider[1],
                                                       consumption=consumption):
                        self.logger.info("Creditbalance under minimum for provider {} and username {} with usage: {}"
                                         .format(registered_provider[0], registered_provider[1], registered_provider[4]))

                        # TODO check reminder delay for sending email
                        last_ts = self.get_last_reminder_ts(provider=registered_provider[0], username=registered_provider[1])

                        creditbalance_str = self.prepare_creditbalance_min_mail(consumption=consumption)

                        # set last reminder timestamp
                        self.set_last_reminder_ts(provider=registered_provider[0], username=registered_provider[1])

                        self.send_notification_mail(receivers=registered_provider[5],
                                                    subject_str="Creditbalance minimum reached for {}".format(registered_provider[4]),
                                                    notification_str=creditbalance_str)
                    # send weekly reminder mails to receivers
                    if notify:
                        self.logger.info("Weekly reminder for {} with usage: {}".format(registered_provider[1],
                                                                                      registered_provider[4]))
                        notification_str = self.prepare_notification_mail(consumption=consumption, data_usage=data_usage)
                        self.send_notification_mail(receivers=registered_provider[5],
                                                    subject_str="Consumption Overview for {}".format(registered_provider[4]),
                                                    notification_str=notification_str)

                except ProviderInstanceError as ex:
                    self.logger.error("ProviderInstanceError: {}".format(ex))
                except ProviderLoginError as ex:
                    self.logger.error("ProviderLoginError: {}".format(ex))
        else:
            self.logger.error("Registered provider list from database is empty!")


