import logging
import requests
from abc import ABC, abstractmethod


class Provider(ABC):
    """ Base class Provider to define methods for specific Mobile Phone Providers

    """
    def __init__(self):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('create class Provider')

        self.session = requests.Session()
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                      "Chrome/73.0.3683.75 Safari/537.36"}
        self.session.headers.update(self.headers)

    @abstractmethod
    def login(self, username, password):
        """ login method for the provider web page

        :return: True if login was successful
        """
        pass

    @abstractmethod
    def current_consumption(self):
        """ get current consumption from provider web page

        :return: consumption data dict
        """
        pass

    @abstractmethod
    def data_usage_overview(self):
        """ get data usage overview from provider web page

        :return: data usage dict
        """
        pass

