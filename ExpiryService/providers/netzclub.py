import logging
from bs4 import BeautifulSoup
from ExpiryService.providers import Provider


class Netzclub(Provider):
    """ class Netzclub to parse consumption data from Netzclub web page

    USAGE:
            netzclub = Netzclub()
            netzclub.login(username, password)

    """
    def __init__(self):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('create class Netzclub')

        # init base class
        super().__init__()

        self.netzclub_login = "https://www.netzclub.net/login/"
        self.netzclub_home = "https://www.netzclub.net/selfcare/"
        self.csrf_token, self.sid, self.reload_token = self.__get_login_tokens()

        self.session.headers.update({
            #"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.netzclub.net/login/",
            "Connection": "keep-alive",
            "Origin": "https://www.netzclub.net/",
            "Content-Type": "application/x-www-form-urlencoded",
        })

        self.netzclub_data = dict()

    def __get_login_tokens(self):
        """ get the csrf token from the web page

        :return: csrf token
        """
        self.logger.info("Get csrf token from Netzclub web page")

        token_resp = self.session.get(self.netzclub_login)
        bs = BeautifulSoup(token_resp.text, 'html.parser')
        csrf_token = bs.find('input', type="hidden", attrs={'name': 'csrfToken'}).get('value')
        sid = bs.find('input', type="hidden", attrs={'name': 'sid'}).get('value')
        reload_token = bs.find('input', type="hidden", attrs={'name': '__reload_token_loginForm__'}).get('value')

        return csrf_token, sid, reload_token

    def login(self, username, password):
        """ login to netzclub web page

        :param username: username
        :param password: password
        :return: True if login was successful else False
        """
        self.logger.info("Login to Netzclub web page")

        login_form = {
            '__hidden_loginForm': 'exists',
            'sid': self.sid,
            '__reload_token_loginForm__': self.reload_token,
            'csrfToken': self.csrf_token,
            'txtMobile': username,
            'txtPassword': password,
            'btnLogin': '',
            'hidAnchor': ''
        }

        login_resp = self.session.post(url=self.netzclub_login, data=login_form, allow_redirects=True)

        if login_resp.status_code == 200:
            self.logger.info("Login to Netzclub was successful")
            return True
        else:
            self.logger.error("Login to Netzclub failed!")
            return False

    def current_consumption(self):
        """

        :return:
        """
        netzclub_home = self.session.get(url="https://www.netzclub.net/selfcare/")

        soup = BeautifulSoup(netzclub_home.text, 'html.parser')

        remaining_data = soup.find("div", {"class": "c-value-box__amount"}).text
        print(remaining_data)
        total_data = soup.find("div", {"class": "c-value-box__text"}).text
        print(total_data)
        end_date = soup.find("small", {"class": "c-value-box__footnote"}).text
        end_date = end_date.strip().replace('\n', '')
        print(end_date)
        self.netzclub_data.update({
            'remaining_volume': remaining_data,
            'total_volume': total_data,
            'end_date': end_date
        })
        return self.netzclub_data


if __name__ == '__main__':
    netzclub = Netzclub()
    if netzclub.login(username="", password=""):
        netzclub.current_consumption()
