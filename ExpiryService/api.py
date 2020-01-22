import json
import logging
from flask import Response, request, send_from_directory
from ExpiryService.validator import Validator
from ExpiryService.dbhandler import DBHandler
from ExpiryService.exceptions import DBIntegrityError
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

        # validator instance
        self.validator = Validator()

    def index(self):
        """ renders the frontend page

        """
        return send_from_directory(ROOT_DIR + '/frontend/', 'index.html')

    def static_proxy(self, path):
        """ sets a static proxy to the frontend directory

        :param path: path to the dist folder from frontend directory
        """
        return send_from_directory(ROOT_DIR + '/frontend/', path)

    def get_providers(self):
        """ get all providers from the database

        :return: Response object
        """

        self.logger.info("GET request to route /providers/")

        sql = "select * from {}".format(self.database_table)
        provider_list = list()
        try:
            data = self.dbfetcher.all(sql=sql)
        except Exception as e:
            self.logger.error("Exception occured. {}".format(e))
            return Response(status=500, response=json.dumps("Internal Database Error"), mimetype='application/json')

        for elem in data:
            provider_dict = dict()
            provider_dict['provider']    = elem[0]
            provider_dict['username']    = elem[1]
            provider_dict['password']    = elem[2]
            provider_dict['min_balance'] = elem[3]
            provider_dict['name']        = elem[4]
            provider_list.append(provider_dict)

        self.logger.info("send providers to client: {}".format(provider_list))
        return Response(status=200, response=json.dumps(provider_list), mimetype='application/json')

    def add_provider(self):
        """ adds a new provider to the database

        :return: Response object
        """

        self.logger.info("POST request to route /provider/")
        if ('Provider' and 'Username' and 'Password' and 'Minbalance' and 'Name') in request.headers.keys():
            provider    = request.headers['Provider']
            username    = request.headers['Username']
            password    = request.headers['Password']
            min_balance = request.headers['Minbalance']
            name        = request.headers['Name']

            if ',' in min_balance:
                min_balance = min_balance.replace(',', '.')

            # validate given attributes
            if not self.validator.provider(provider=provider):
                self.logger.error("Provider {} is not supported".format(provider))
                return Response(status=400, response=json.dumps("Provider {} is not supported".format(provider)), mimetype='application/json')
            elif not self.validator.username(provider=provider, username=username):
                self.logger.error("Username {} for given Provider {} is not valid".format(username, provider))
                return Response(status=400, response=json.dumps("Username {} for given Provider {} is not valid".format(username, provider)), mimetype='application/json')
            elif not self.validator.balance(balance=min_balance):
                self.logger.error("Minimum Balance must be positive")
                return Response(status=400, response=json.dumps("Minimum Balance must be positive"), mimetype='application/json')

            # check if provider combination already available
            sql_provider_combo = "select * from {} where provider = %s and username = %s and password = %s".format(self.database_table)

            try:
                providers = self.dbfetcher.all(sql=sql_provider_combo, data=(provider, username, password))
            except Exception as e:
                self.logger.error("Exception!: {}".format(e))
                return Response(status=500, response=json.dumps("Internal Database Error"), mimetype='application/json')

            if len(providers) > 0:
                self.logger.error("Provider {}, Username {} was already added".format(provider, username))
                return Response(status=409, response=json.dumps("Provider was already added"),
                                mimetype='application/json')

            sql = "insert into {} (provider, username, password, min_balance, name) values (%s, %s, %s, %s, %s)".format(
                self.database_table)

            try:
                self.dbinserter.row(sql=sql, data=(provider, username, password, min_balance, name))
            except DBIntegrityError as e:
                self.logger.error("IntegrityError occured!: {}".format(e))
                return Response(status=409, response=json.dumps("Provider data already available"), mimetype='application/json')
            except Exception as e:
                self.logger.error("Exception: {}".format(e))
                return Response(status=500, response=json.dumps("Internal Database Error"), mimetype='application/json')

            self.logger.info("Added new Provider: {} with Username: {}".format(provider, username))
            return Response(status=200, response=json.dumps("Successfully added new Provider: {} with Username: {}".format(provider, username)),
                            mimetype='application/json')
        else:
            self.logger.error("Bad POST Request to /provider/")
            return Response(status=400, response=json.dumps("Bad Request Headers"), mimetype='application/json')

    def delete_provider(self):
        """ deletes a provider from the database

        :return: Response object
        """

        self.logger.info("DELETE request to route /provider/")
        if ('provider' and 'username') in request.args.keys():
            provider = request.args.get('provider')
            username = request.args.get('username')

            # validate given attributes
            if not self.validator.provider(provider=provider):
                return Response(status=400, response=json.dumps("Provider {} is not supported".format(provider)), mimetype='application/json')
            elif not self.validator.username(provider=provider, username=username):
                return Response(status=400, response=json.dumps("Username {} for given Provider {} is not valid".format(username, provider)), mimetype='application/json')

            sql = "select * from {} where provider = %s and username = %s".format(self.database_table)
            try:
                providers = self.dbfetcher.all(sql=sql, data=(provider, username))
            except Exception as e:
                self.logger.error("Exception: {}".format(e))
                return Response(status=500, response=json.dumps("Internal Database Error"), mimetype='application/json')

            if len(providers) > 0:
                sql = "delete from {} where provider = %s and username = %s".format(self.database_table)
                try:
                    self.dbinserter.row(sql=sql, data=(provider, username))
                except Exception as e:
                    self.logger.error("Exception: {}".format(e))
                    return Response(status=500, response=json.dumps("Internal Database Error"), mimetype='application/json')

                self.logger.info("Successfully deleted Provider: {} with Username: {} from database".format(provider, username))
                return Response(status=200, response=json.dumps("Successfully deleted Provider: {} with Username: {} "
                                                                "from database".format(provider, username)), mimetype='application/json')
            else:
                self.logger.error("Requested Provider and Username combination was not found")
                return Response(status=404, response=json.dumps("Requested Provider and Username combination not found"),
                                mimetype='application/json')
        else:
            self.logger.error("Bad DELETE Request to /provider/")
            return Response(status=400, response=json.dumps("Bad Request Parameters"), mimetype='application/json')

    def update_balance(self):
        """

        :return:
        """
        self.logger.info("POST request to route /provider/")
        pass

    def get_mail_notification(self):
        """

        :return:
        """

        self.logger.info("GET request to route /notification/mail/")

        if ('Provider' and 'Username' and 'Password') in request.headers.keys():

            provider    = request.headers['Provider']
            username    = request.headers['Username']
            password    = request.headers['Password']

            sql = "select notifyer from {} where provider = %s and username = %s".format(self.database_table)

        else:
            self.logger.error("Bad GET Request to route /notification/mail/")
            return Response(status=400, response=json.dumps("Bad Request Headers"), mimetype='application/json')

    def register_mail_notification(self):
        """

        :return:
        """
        self.logger.info("POST request to route /notification/mail/")

        if ('Provider' and 'Username' and 'Password') in request.headers.keys():

            provider    = request.headers['Provider']
            username    = request.headers['Username']
            password    = request.headers['Password']

            if ('receiver') in request.args.keys():
                receiver = request.args.getlist('receiver')



                self.logger.info("Successfully ".format())
                return Response(status=200, response=json.dumps("Successfully ".format(provider, username)), mimetype='application/json')
            else:
                return Response(status=400, response=json.dumps("Bad Request Params"), mimetype='application/json')

        else:
            self.logger.error("Bad POST Request to route /notification/mail/")
            return Response(status=400, response=json.dumps("Bad Request Headers"), mimetype='application/json')

    def delete_mail_notification(self):
        """

        :return:
        """
        pass
