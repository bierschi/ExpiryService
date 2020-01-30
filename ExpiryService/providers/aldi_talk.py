import logging
from bs4 import BeautifulSoup
from ExpiryService.providers import Provider


class AldiTalk(Provider):
    """ class AldiTalk to parse consumption data from AldiTalk web page

    USAGE:
            alditalk = AldiTalk()
            alditalk.login(username, password)

    """
    def __init__(self):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('create class AldiTalk')

        # init base class
        super().__init__()

        self.aldi_url = "https://www.alditalk-kundenbetreuung.de/de/"
        self.csrf_token = self.__get_csrf_token()

        self.aldi_data = dict()

    def __str__(self):
        """ string representation

        :return: str
        """
        return "AldiTalk"

    def __get_csrf_token(self):
        """ get the csrf token from the web page

        :return: csrf token
        """
        self.logger.info("Get csrf token from AldiTalk web page")

        token_resp = self.session.get(self.aldi_url)
        bs = BeautifulSoup(token_resp.text, 'html.parser')
        token = bs.find('input', type="hidden", attrs={'name': '_csrf_token'}).get('value')

        return token

    def login(self, username, password):
        """ login to alditalk web page

        :param username: username
        :param password: password

        :return: True if login was successful else False
        """

        login_form = {
            '_csrf_token': self.csrf_token,
            'form[username]': username,
            'form[password]': password,
        }
        login_resp = self.session.post(url=self.aldi_url + 'login_check', data=login_form, allow_redirects=True)

        if login_resp.status_code == 200:
            self.logger.info("Login to AldiTalk was successful")
            return True
        else:
            self.logger.error("Login to AldiTalk failed!")
            return False

    def current_consumption(self):
        """ get current consumption from AldiTalk web page

        :return: consumption dict
        """
        resp = self.session.get(url=self.aldi_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        #print(soup)
        credit_balance_box = soup.find("div", {"id": "ajaxReplaceQuickInfoBoxBalanceId"})

        credit_balance = ''
        for p in credit_balance_box.find_all(["p"]):
            credit_balance = p.text.replace('\xa0', ' ')

        table_data = soup.find("div", {"class": "table"})

        remaining_data, total_data, end_date = self.__parse_table_data(table=table_data)

        name_number_data = soup.find("div", {"id": "ajaxReplaceAreaId-32956"})

        name = name_number_data.find('p').text
        number = name_number_data.find('h3').text

        self.aldi_data.update({
            'name': name,
            'number': number,
            'credit_balance': credit_balance,
            'remaining_volume': remaining_data,
            'total_volume': total_data,
            'end_date': end_date
        })
        return self.aldi_data

    def __parse_table_data(self, table):
        """ parses the table data which contains the current consumption

        :param table: bs table element
        :return: remaining_data, total_data, end_date
        """
        end_date_data = table.find("tr", {"class": "t-row pack__panel pack__panel--end-date"})
        end_date_text = end_date_data.find("td", {"colspan": "2"}).text
        end_date = end_date_text.strip().replace('\n', '')

        pack_usage = table.find("td", {"class": "pack__usage"})

        data = pack_usage.find_all("span")

        if len(data) > 4:
            usage_remaining = data[0].text
            usage_remaining_unit = data[2].text
            usage_total = data[3].text
            usage_total_unit = data[4].text

            remaining_data = usage_remaining + ' ' + usage_remaining_unit
            total_data = usage_total + ' ' + usage_total_unit
            return remaining_data, total_data, end_date
        else:
            self.logger.error("length of table data is less than 5! Can not parse remaining data")

    def data_usage_overview(self):
        """ parses the data usage overview from the alditalk webpage

        :return: table dict
        """
        resp = self.session.get(url=self.aldi_url + 'konto/kontoubersicht')
        soup = BeautifulSoup(resp.text, 'html.parser')

        data_usage = soup.find("div", {"id": "ajaxReplaceAreaId-20701"})

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
            data = row.text.strip().replace('  ', '').splitlines()
            data = [s for s in data if s]  # remove empty str
            table_body_list.append(data)

        table_dict['table_body'] = table_body_list

        return table_dict


if __name__ == '__main__':
    aldi = AldiTalk()
    if aldi.login(username='01575-5021329', password=''):
        print(aldi.data_usage_overview())


