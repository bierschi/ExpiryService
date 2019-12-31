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

