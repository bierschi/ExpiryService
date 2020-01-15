import json
import logging
from flask import Response, request, send_from_directory
from ExpiryService.dbhandler import DBHandler
from ExpiryService import ROOT_DIR


class APIHandler(DBHandler):
    """ class APIHandler to define api handler functions

    USAGE:
            api = APIHandler()

    """
    def __init__(self):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('create class APIHandler')

        # init base class
        super().__init__()


    def index(self):
        """ renders the frontend page

        """
        return send_from_directory(ROOT_DIR + '/frontend/', 'index.html')

    def static_proxy(self, path):
        """ sets a static proxy to the frontend directory

        :param path: path to the dist folder from frontend directory
        """
        return send_from_directory(ROOT_DIR + '/frontend/', path)

    def test(self):
        """

        :return:
        """

        return Response(status=200, response=json.dumps("API test successful"), mimetype='application/json')


    def get_providers(self):
        """

        :return:
        """
        return Response(status=200, response=json.dumps("Send all saved Providers"), mimetype='application/json')

    def add_provider(self):
        """

        :return:
        """
        print(request.headers)
        if ('Provider' and 'Username' and 'Password' and 'Minbalance') in request.headers.keys():
            provider = request.headers['Provider']
            username = request.headers['Username']
            password = request.headers['Password']
            min_balance = request.headers['Minbalance']

            sql = "insert into {} ".format(self.database_table)
            data = "s"
            self.dbinserter.row(sql=sql, data=data)
            return Response(status=200, response=json.dumps("Successfully inserted Provider"),
                            mimetype='application/json')
        else:
            return Response(status=400, response=json.dumps("Bad Request Headers"), mimetype='application/json')


    def delete_provider(self):
        """

        :return:
        """
        pass
