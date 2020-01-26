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

    def get_provider(self):
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
            if elem[5] is not None:
                provider_dict['notifyer']    = elem[5].split(';')
            else:
                provider_dict['notifyer'] = list()
            provider_list.append(provider_dict)

        self.logger.info("send providers to client: {}".format(provider_list))
        return Response(status=200, response=json.dumps(provider_list), mimetype='application/json')

    def add_provider(self):
        """ adds a new provider to the database

        :return: Response object
        """

        self.logger.info("POST request to route /provider/")
        if ('Provider' and 'Username' and 'Password' and 'Minbalance' and 'Name' and 'Notifyer') in request.headers.keys():
            provider    = request.headers['Provider']
            username    = request.headers['Username']
            password    = request.headers['Password']
            min_balance = request.headers['Minbalance']
            name        = request.headers['Name']
            notifyer    = request.headers['Notifyer']

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
            elif not self.validator.notifyer(notifyer=notifyer):
                self.logger.error("Notifyer is not a valid mail address")
                return Response(status=400, response=json.dumps("Notifyer is not a valid mail address"), mimetype='application/json')

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

            sql = "insert into {} (provider, username, password, min_balance, name, notifyer) values (%s, %s, %s, %s, %s, %s)".format(
                self.database_table)

            try:
                self.dbinserter.row(sql=sql, data=(provider, username, password, min_balance, name, notifyer))
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
        if ('Provider' and 'Username') in request.headers.keys():
            provider    = request.headers['Provider']
            username    = request.headers['Username']

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
            sql_delete_all = "delete from {}".format(self.database_table)
            try:
                self.dbinserter.sql(sql=sql_delete_all)
            except Exception as e:
                self.logger.error("Exception: {}".format(e))
                return Response(status=500, response=json.dumps("Internal Database Error"), mimetype='application/json')
            self.logger.error("Successfully deleted all providers from database")
            return Response(status=200, response=json.dumps("Successfully deleted all providers from database"), mimetype='application/json')

    def get_creditbalance(self):
        """

        :return:
        """
        pass

    def update_creditbalance(self):
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

        if ('Provider' and 'Username') in request.headers.keys():

            provider    = request.headers['Provider']
            username    = request.headers['Username']

            sql_notifyer = "select notifyer from {} where provider = %s and username = %s".format(self.database_table)

            notifyers = self.dbfetcher.all(sql=sql_notifyer, data=(provider, username))

            if len(notifyers) > 0:
                notifyer_list = list()
                for notifyer in notifyers:
                    if notifyer[0] is not None:
                        notifyer_list.extend(notifyer[0].split(';'))
                    else:
                        self.logger.error("Saved notifyer list is NULL!")
                self.logger.info("Send notifyer list to client: {}".format(notifyer_list))
                return Response(status=200, response=json.dumps(notifyer_list), mimetype='application/json')

            else:
                return Response(status=404, response=json.dumps("No mail notification was set!"), mimetype='application/json')

        else:
            self.logger.error("Bad GET Request to route /notification/mail/")
            return Response(status=400, response=json.dumps("Bad Request Headers"), mimetype='application/json')

    def register_mail_notification(self):
        """

        :return:
        """
        self.logger.info("POST request to route /notification/mail/")

        if ('Provider' and 'Username') in request.headers.keys():

            provider    = request.headers['Provider']
            username    = request.headers['Username']

            # validate given attributes
            if not self.validator.provider(provider=provider):
                return Response(status=400, response=json.dumps("Provider {} is not supported".format(provider)), mimetype='application/json')
            elif not self.validator.username(provider=provider, username=username):
                return Response(status=400, response=json.dumps("Username {} for given Provider {} is not valid".format(username, provider)), mimetype='application/json')

            if 'notifyer' in request.args.keys():
                given_notifyers = request.args.getlist('notifyer')

                sql_notifyer = "select notifyer from {} where provider = %s and username = %s".format(self.database_table)

                saved_notifyers = self.dbfetcher.all(sql=sql_notifyer, data=(provider, username))

                if len(saved_notifyers) > 0:

                    # check if notifyer already in db
                    for el in saved_notifyers:
                        if el[0] is not None:
                            saved_notifyers_list = el[0].split(';')
                        else:
                            saved_notifyers_list = list()

                    for notifyer in given_notifyers:
                        if not (notifyer in saved_notifyers_list):
                            saved_notifyers_list.append(notifyer)
                        else:
                            self.logger.error("notifyer: {} already in the database table".format(notifyer))

                    # concat notifyers
                    all_notifyers = ';'.join(saved_notifyers_list)

                    sql_set_notifyer = "update {} set notifyer = %s where provider = %s and username = %s".format(self.database_table)
                    try:
                        self.dbinserter.row(sql=sql_set_notifyer, data=(all_notifyers, provider, username))
                    except Exception as e:
                        self.logger.error("Exception: {}".format(e))
                        return Response(status=500, response=json.dumps("Internal Database Error"), mimetype='application/json')

                    self.logger.info("Successfully updated the notifyers from Provider: {} and Username: {}".format(provider, username))
                    return Response(status=200, response=json.dumps("Successfully updated the notifyers from Provider: {} and Username: {}".format(provider, username)),
                                    mimetype='application/json')
                else:

                    return Response(status=500, response=json.dumps("Internal Error".format(provider, username)), mimetype='application/json')
            else:
                return Response(status=400, response=json.dumps("Bad Request Params"), mimetype='application/json')

        else:
            self.logger.error("Bad POST Request to route /notification/mail/")
            return Response(status=400, response=json.dumps("Bad Request Headers"), mimetype='application/json')

    def delete_mail_notification(self):
        """ deletes mail notification for given provider and username

        :return: Response object
        """
        self.logger.info("DELETE request to route /notification/mail/")

        if ('Provider' and 'Username') in request.headers.keys():
            provider = request.headers['Provider']
            username = request.headers['Username']

            # validate given attributes
            if not self.validator.provider(provider=provider):
                return Response(status=400, response=json.dumps("Provider {} is not supported".format(provider)), mimetype='application/json')
            elif not self.validator.username(provider=provider, username=username):
                return Response(status=400, response=json.dumps("Username {} for given Provider {} is not valid".format(username, provider)), mimetype='application/json')

            if 'notifyer' in request.args.keys():
                given_notifyers = request.args.getlist('notifyer')

                sql_notifyer = "select notifyer from {} where provider = %s and username = %s".format(self.database_table)

                saved_notifyers = self.dbfetcher.all(sql=sql_notifyer, data=(provider, username))

                if len(saved_notifyers) > 0:

                    # check if given notifyer in saved notifyers
                    for el in saved_notifyers:
                        if el[0] is not None:
                            saved_notifyers_list = el[0].split(';')
                        else:
                            saved_notifyers_list = list()

                    for g_notifyer in given_notifyers:
                        if g_notifyer in saved_notifyers_list:
                            saved_notifyers_list.remove(g_notifyer)
                        else:
                            self.logger.error("given notifyer: {} can not be deleted from the database table".format(g_notifyer))

                    # concat notifyers
                    all_notifyers = ';'.join(saved_notifyers_list)
                    sql_notifyer_delete = "update {} set notifyer = %s where provider = %s and username = %s".format(
                        self.database_table)
                    try:
                        self.dbinserter.row(sql=sql_notifyer_delete, data=(all_notifyers, provider, username))
                    except Exception as e:
                        self.logger.error("Exception: {}".format(e))
                        return Response(status=500, response=json.dumps("Internal Database Error"), mimetype='application/json')

                    self.logger.info("Successfully deleted notifyers from Provider: {} and Username: {}".format(provider, username))
                    return Response(status=200, response=json.dumps("Successfully deleted notifyers from Provider: {} and Username: {}".format(provider, username)),
                                    mimetype='application/json')
                else:
                    self.logger.error("Length of saved notifyers is 0!")
                    return Response(status=500, response=json.dumps("Internal Server Error"), mimetype='application/json')
            else:
                sql_set_notifyer = "update {} set notifyer = NULL where provider = %s and username = %s".format(self.database_table)
                try:
                    self.dbinserter.row(sql=sql_set_notifyer, data=(provider, username))
                except Exception as e:
                    self.logger.error("Exception: {}".format(e))
                    return Response(status=500, response=json.dumps("Internal Database Error"),
                                    mimetype='application/json')
                self.logger.info(
                    "Successfully deleted notifyers from Provider: {} and Username: {}".format(provider, username))
                return Response(status=200, response=json.dumps("Successfully deleted notifyers from Provider: {} and Username: {}".format(provider, username)), mimetype='application/json')
        else:
            self.logger.error("Bad DELETE Request to route /notification/mail/")
            return Response(status=400, response=json.dumps("Bad Request Headers"), mimetype='application/json')
