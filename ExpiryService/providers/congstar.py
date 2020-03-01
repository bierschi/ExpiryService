import logging
from ExpiryService.providers import Provider


class Congstar(Provider):
    """ class Congstar to parse consumption data from Congstar web page

    USAGE:
            congstar = Congstar()
            congstar.login(username, password)

    """
    def __init__(self):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('create class Congstar')

        # init base class
        super().__init__()

        self.congstar_login = "https://www.congstar.de/api/auth/login"
        self.congstar_home = "https://www.congstar.de/meincongstar/"
        self.session.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Host": "www.congstar.de",
            "Origin": "https://www.congstar.de/",
            #"Referer": "https://www.congstar.de/login/",
            #"Content-Type": "application/json, text/plain, */*",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "XMLHttpRequest"
        })

        self.congstar_data = dict()

    def login(self, username, password):
        """ login to congstar web page

        :param username: username
        :param password: password
        :return: True if login was successful else False
        """

        self.logger.info("Login to Congstar web page")

        login_form = {
            'username': username,
            'password': password,
            'defaultRedirectUrl': "/meincongstar",
            'targetPageUrlOrId': ""
        }

        login_resp = self.session.post(url=self.congstar_login, data=login_form, allow_redirects=True)
        print(login_resp.status_code)
        #print(login_resp.text)

        if login_resp.status_code == 200:
            self.logger.info("Login to Congstar was successful")
            return True
        else:
            self.logger.error("Login to Congstar failed!")
            return False

    def current_consumption(self):
        """

        :return:
        """
        resp = self.session.get(url="https://www.congstar.de/meincongstar/meine-produkte/tarife/mein-vertrag/?contractId=BvWF_IP1DdTcQg%3D%3D")
        #print(self.session.cookies)
        print(resp.text)

if __name__ == '__main__':
    congstar = Congstar()
    if congstar.login(username="", password=""):
        congstar.current_consumption()
