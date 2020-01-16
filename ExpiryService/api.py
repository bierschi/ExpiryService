import json
import logging
from flask import Response, request, send_from_directory
from ExpiryService.dbhandler import DBHandler
from ExpiryService import ROOT_DIR
from ExpiryService.exceptions import DBIntegrityError


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

    def get_providers(self):
        """ get all providers from the database

        :return: Response object
        """

        self.logger.info("GET request to route /providers/")

        sql = "select * from {}".format(self.database_table)
        provider_list = list()
        try:
            data = self.dbfetcher.all(sql=sql)
            for elem in data:
                provider_dict = dict()
                provider_dict['provider'] = elem[0]
                provider_dict['username'] = elem[1]
                provider_dict['password'] = elem[2]
                provider_dict['min_balance'] = elem[3]
                provider_list.append(provider_dict)
        except Exception as e:
            self.logger.error("Exception occured. {}".format(e))
            return Response(status=500, response=json.dumps("Internal Database Error"), mimetype='application/json')

        self.logger.info("send providers to client: {}".format(provider_list))
        return Response(status=200, response=json.dumps(provider_list), mimetype='application/json')

    def add_provider(self):
        """ adds a new provider to the database

        :return: Response object
        """

        self.logger.info("POST request to route /provider/")
        if ('Provider' and 'Username' and 'Password' and 'Minbalance') in request.headers.keys():
            provider = request.headers['Provider']
            username = request.headers['Username']
            password = request.headers['Password']
            min_balance = request.headers['Minbalance']

            sql = "insert into {} (provider, username, password, min_balance) values (%s, %s, %s, %s)".format(
                self.database_table)
            # TODO Validator for provider, username, min balance
            try:
                self.dbinserter.row(sql=sql, data=(provider, username, password, min_balance))
            except DBIntegrityError as e:
                self.logger.error("IntegrityError occured!: {}".format(e))
                return Response(status=409, response=json.dumps("Provider data already available"), mimetype='application/json')
            except Exception as e:
                self.logger.error("Exception: {}".format(e))
                return Response(status=500, response=json.dumps("Internal Database Error"), mimetype='application/json')

            self.logger.info("Added new Provider: {} with Username: ".format(provider, username))
            return Response(status=200, response=json.dumps("Successfully added new Provider: {} with Username: {}".format(provider, username)),
                            mimetype='application/json')
        else:
            self.logger.error("Bad POST Request to /provider/")
            return Response(status=400, response=json.dumps("Bad Request Headers"), mimetype='application/json')

    def delete_provider(self):
        """ deletes a provider from the database

        :return: Response object
        """

        if ('provider' and 'username') in request.args.keys():
            provider = request.args.get('provider')
            username = request.args.get('username')

            # TODO Validator for provider and username

            sql = "select * from {} where provider = %s and username = %s".format(self.database_table)
            try:
                providers = self.dbfetcher.all(sql=sql, data=(provider, username))
                print(providers)
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
