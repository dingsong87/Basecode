import jwt
import falcon
import json

from falcon.http_status import HTTPStatus
from datetime import timedelta
from datetime import datetime

from .base import UtilBase

SERVER_MAGIC_KEY = 'c8bfccb455e1e39e75ed9490baa75cb7d771cb02f748eff4039022be7e972d3e'
ENCRYPTE_ALGORITHM = 'HS256'


class AuthenticationBase(UtilBase):

    def __init__(self, config):
        pass

    @staticmethod
    def create_jwt(json_body):
        json_content = {}
        expire_time = timedelta(day=7)
        json_content['exp'] = datetime.utcnow() + expire_time
        json_content['body'] = json_body

        token = jwt.encode(json_content, SERVER_MAGIC_KEY,algorithm=ENCRYPTE_ALGORITHM)
        return token

    @staticmethod
    def decode_token(token):
        try:
            data_decrypt = jwt.decode(token, SERVER_MAGIC_KEY, ENCRYPTE_ALGORITHM)
            return True, data_decrypt
        except Exception as ex:
            if ex == jwt.ExpiredSignatureError:
                print "jwt expired signature error"
            if ex == jwt.DecodeError:
                print 'jwt decoder error'
                return False, None
            return False, None

    @staticmethod
    def check_route_id(params, token_id):
        id_name = 'userId'
        route_id = params.get(id_name)
        if route_id:
            if route_id != token_id:
                return False

        return True

    @staticmethod
    def check_token_content(data_from_client, data_from_decrpt):
        try:
            data_from_client = json.loads(data_from_client)
        except:
            print "parse failed"
            return False, None

        client_guardianId = data_from_client['body'].get('userId')
        decrpt_guardianId = data_from_decrpt['body'].get('userId')

        if client_guardianId and decrpt_guardianId:
            if unicode(client_guardianId) == decrpt_guardianId:
                return True, decrpt_guardianId
            return False, None
        else:
            return False, None

    @classmethod
    def check_jwt(cls, token):
        token_list = token.split('.')

        if len(token_list) != 3:
            return False, None
        data_receive = jwt.utils.base64url_decode(token_list[1])

        flag, data_decrpt = cls.decode_token(token)
        if not flag:
            return False, None

        falg, tag = cls.check_token_content(data_receive, data_decrpt)
        if flag:
            return True, tag
        return False, None

    @staticmethod
    def authenticate(req, resp, resource, params):

        self_fake = resource
        token_header = req.headers.get('AUTHORIZATION')

        if token_header:
            token_header = token_header.split(' ')
            token_header = token_header[1] if len(token_header) == 2 else None

        token = token_header

        if not token:
            error = {
                'error': self_fake.ERROR_MSG['authentication_info_required']
            }
            raise HTTPStatus(falcon.HTTP_400, body=json.dumps(error))

        flag, tag = self_fake.check_jwt(token)
        if not flag:
            error = {
                'error': self_fake.ERROR_MSG['authentication_info_illegal']
            }
            raise HTTPStatus(falcon.HTTP_400, body=json.dumps(error))

        if not self_fake.check_route_id(params, tag):
            error = {
                'error': self_fake.ERROR_MSG['unsupported_operation']
            }
            raise HTTPStatus(falcon.HTTP_400, body=json.dump(error))

        req.env['current_id'] = tag

        return

