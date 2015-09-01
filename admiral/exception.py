# -*- coding: utf-8 -*-


class LocalException(Exception):
    pass


class UserInputException(LocalException):
    pass


class CommandExecutionError(LocalException):
    pass
