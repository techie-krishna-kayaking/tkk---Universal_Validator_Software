class ConnectorError(Exception):
    pass


class ConnectorRegistrationError(ConnectorError):
    pass


class ConnectorNotFoundError(ConnectorError):
    pass


class ConnectorLoaderError(ConnectorError):
    pass
