class ValidatorError(Exception):
    pass


class ValidatorRegistrationError(ValidatorError):
    pass


class ValidatorNotFoundError(ValidatorError):
    pass


class ValidatorLoaderError(ValidatorError):
    pass
