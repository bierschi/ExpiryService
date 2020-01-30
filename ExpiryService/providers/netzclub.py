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
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.netzclub.net/login/",
            "Connection": "keep-alive",
            "Origin": "https://www.netzclub.net/",
            "Content-Type": "application/x-www-form-urlencoded",
        })

        self.netzclub_data = dict()

    def __str__(self):
        """ string representation

        :return: str
        """
        return "Netzclub"

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
        """ get current consumption from Netzclub web page

        :return: consumption dict
        """
        netzclub_home = self.session.get(url="https://www.netzclub.net/selfcare/")

        soup = BeautifulSoup(netzclub_home.text, 'html.parser')

        credit_balance = soup.find("span", {"class": "c-button__balance"}).text

        name = soup.find("div", {"class": "c-user-info c-user-info--with-border"}).text
        name_number_list = name.strip().replace('\n', '').split('           ')
        if len(name_number_list) > 2:
            name   = name_number_list[0]
            number = name_number_list[2].strip()
        else:
            name = ''
            number = ''

        remaining_data = soup.find("div", {"class": "c-value-box__amount"}).text

        total_data = soup.find("div", {"class": "c-value-box__text"}).text

        end_date = soup.find("small", {"class": "c-value-box__footnote"}).text
        end_date = end_date.strip().replace('\n', '')

        self.netzclub_data.update({
            'name': name,
            'number': number,
            'creditbalance': credit_balance,
            'remaining_volume': remaining_data,
            'total_volume': total_data,
            'end_date': end_date
        })
        return self.netzclub_data

    def data_usage_overview(self):
        """ parses the data usage overview from the netzclub webpage

        :return: table dict
        """
        netzclub_home = self.session.get(url="https://www.netzclub.net/meine-abrechnung/")

        soup = BeautifulSoup(netzclub_home.text, 'html.parser')

        data_usage = soup.find("div", {"id": "datenverbrauchsuebersicht"})

        table_head = data_usage.find('thead')
        table_head_rows = table_head.find_all('th')

        table_dict = dict()
        table_head_list = list()
        for row in table_head_rows:
            table_head_list.append(row.text)

        table_dict['table_head'] = table_head_list

        table_body = data_usage.find('tbody')
        table_body_rows = table_body.find_all('tr')

        table_body_list = list()
        for row in table_body_rows:
            table_body_list.append(row.text.strip().split('\n'))

        table_dict['table_body'] = table_body_list

        return table_dict

if __name__ == '__main__':
    netzclub = Netzclub()
    if netzclub.login(username="", password=""):
        print(netzclub.data_usage_overview())
