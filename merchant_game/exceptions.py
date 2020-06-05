from rest_framework import exceptions


class InvalidRequestException(exceptions.APIException):
    status_code = exceptions.status.HTTP_400_BAD_REQUEST
    default_detail = "The request is missing keys."
    default_code = "missing"
