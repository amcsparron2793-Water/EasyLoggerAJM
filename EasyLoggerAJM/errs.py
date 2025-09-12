class InvalidEmailMsgType(Exception):
    DEFAULT_MSG = "email_msg must be one of {valid_msg_types} not {given_value}."
    _MISSING_ATTR_ERR_MSG = 'if msg is not given, valid_msg_types and given_value must be given'

    def __init__(self, msg=None, **kwargs):
        valid_msg_types = kwargs.get('valid_msg_types', None)
        given_value = kwargs.get('given_value', None)
        if msg:
            self.message = msg
        if not msg and valid_msg_types and given_value:
            self.message = self.__class__.DEFAULT_MSG.format(valid_msg_types=valid_msg_types,
                                                             given_value=given_value)
        else:
            raise AttributeError(self.__class__._MISSING_ATTR_ERR_MSG)

