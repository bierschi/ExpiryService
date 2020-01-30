

class DBConnectorError(ConnectionError):
    """DBConnectorException"""
    pass


class DBCreatorError(Exception):
    """DBCreatorException"""
    pass


class DBInserterError(Exception):
    """DBInserterException"""
    pass


class DBIntegrityError(Exception):
    """DBIntegrityError"""
    pass


class ProviderInstanceError(Exception):
    """ProviderInstanceError"""
    pass


class ProviderLoginError(Exception):
    """ProviderLoginError"""
    pass


class MailMessageError(Exception):
    """MailMessageError"""
    pass
