import requests
import falcon
import json

from .json_validate import DefaultValidatingDraft4Validator


class UtilBase():

    _error_msg = {
        'authentication_info_required': 'AUTHENTICATION_INFO_REQUIRED',
        'authentication_info_illegal': 'AUTHENTICATION_INFO_ILLEGAL',
        'attempt_too_many_times': 'ATTEMPT_TOO_MANY_TIMES',
        'balance_insufficient': 'BALANCE_INSUFFICIENT',
        'conflict_info_exist': 'CONFLICT_INFO_EXIST',
        'conflict_mobile_exist': 'CONFLICT_MOBILE_EXIST',
        'forbidden': 'FORBIDDEN',
        'img_code_timeout': 'IMG_CODE_TIMEOUT',
        'img_code_verification_failed': 'IMG_CODE_VERIFICATION_FAILED',
        'invalid_body_content': 'INVALID_BODY_CONTENT',
        'invalid_mobile_number': 'INVALID_MOBILE_NUMBER',
        'invalid_query_params': 'INVALID_QUERY_PARAMS',
        'need_credential': 'NEED_CREDENTIAL',
        'not_found': 'NOT_FOUND',
        'no_mobile_info': 'NO_MOBILE_INFO',
        'password_verification_failed': 'PASSWORD_VERIFICATION_FAILED',
        'sms_can_not_send_in_60': 'SMS_CAN_NOT_SEND_IN_60',
        'sms_max_limit_per_day': 'SMS_MAX_LIMIT_PER_DAY',
        'sms_timeout': 'SMS_TIMEOUT',
        'sms_verification_failed': 'SMS_VERIFICATION_FAILED',
        'token_timeout': 'TOKEN_TIMEOUT',
        'token_verification_failed': 'TOKEN_VERIFICATION_FAILED',
        'user_not_exist': 'USER_NOT_EXIST',
        'user_exist_more_information_needed': 'USER_EXIST_MORE_INFORMATION_NEEDED',
        'unsupported_operation': 'UNSUPPORTED_OPERATION',
        'unsupported_transaction_category': 'UNSUPPORTED_TRANSACTION_CATEGORY',
    }

    _headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    _methods = {
        "GET": requests.get,
        "POST": requests.post,
        "PUT": requests.put,
        "DELETE": requests.delete
    }

    @property
    def ERROR_MSG(self):
        return UtilBase._error_msg

    @property
    def HEADERS(self):
        return UtilBase._headers

    @property
    def METHODS(self):
        return UtilBase._methods

    @staticmethod
    def result_error(msg, detail=None):
        msg = {'error': msg}
        if detail:
            msg['detail'] = detail

        return falcon.HTTP_400, json.dumps(msg)

    @staticmethod
    def transform_status_code(status_code):

        if status_code == 200:
            return falcon.HTTP_200

        if status_code == 201:
            return falcon.HTTP_201

        if status_code == 202:
            return falcon.HTTP_202

        if status_code == 403:
            return falcon.HTTP_403

        if status_code == 404:
            return falcon.HTTP_404

        if status_code == 409:
            return falcon.HTTP_409

        if status_code == 415:
            return falcon.HTTP_415

        if status_code == 500:
            return falcon.HTTP_500

    @staticmethod
    def transform_to_int(param_dict, if_raise_value_error=False):
        if not isinstance(param_dict, dict):
            return False, "<%s> is not <dict> type" % type(param_dict)

        for key, value in param_dict.items():
            try:
                param_dict[key] = int(value)
            except ValueError:
                if if_raise_value_error:
                    return False, "'%s' type <%s> can not be converted to <int>" % (value, type(value))
                else:
                    pass
        return True, None

    def request(self, method, url, **params):
        response = self.METHODS[method](url, headers=self.HEADERS, **params)
        return response

    @staticmethod
    def parse_pagination_params(params_dict):
        condition = dict(params_dict)
        pageNum = condition.get('pageNum')
        pageSize = condition.get('pageSize')

        if pageNum:
            del condition['pageNum']
        else:
            pageNum = 0

        if pageSize:
            del condition['pageSize']
        else:
            pageSize = 10

        return condition, pageNum, pageSize

    @staticmethod
    def validate_dict_with_schema(data, schema):
        try:
            DefaultValidatingDraft4Validator(schema).validate(data)
            return 200, None
        except Exception as ex:
            return 415, "parse body exception: %s" % ex

    @classmethod
    def get_params_from_body(cls, body_stream, schema=None, return_dict=False):
        data = {}
        body = body_stream.read()

        try:
            data = json.loads(body)
        except:
            return 415, "parse json failed"

        if schema:
            code, tag = cls.validate_dict_with_schema(data, schema)
            if code != 200:
                return code, tag

        return 200, data if return_dict else json.dumps(data)