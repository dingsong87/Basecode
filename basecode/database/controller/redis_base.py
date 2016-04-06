from ..engine import RedisEngine
from ...utils import UtilBase

from datetime import datetime
from datetime import timedelta

ONE_MINUTE_IN_SECONDS = 60
ONE_DAY_IN_SECONDS = 86400


class RedisBase(RedisEngine, UtilBase):

    _redis_string = {
        'cpv': 'change_password_verify',
        'mbv': 'mobile_binding_verify',
        'mrv': 'mobile_releasing_verify',
        'pnmfs': 'pending_notification_msg_for_store:',
        'pspd': 'phone_send_per_day:',
        'rat': 'request_attempt_times:',
        'rba': 'release_block_address:',
        'siv': 'sign_in_verify:',
        'suv': 'sign_up_verify:',
        'si': 'send_interval:',
        'wit': 'websocket_initial_token:',
    }

    def __init__(self, config):
        super(RedisBase, self).__init__(config)

    @property
    def REDIS_STRING(self):
        return RedisBase._redis_string

    def set_websocket_token(self, retailerId, token):
        self.set_value("redis", {'key': self.REDIS_STRING['wit'] + retailerId,
                                 'value': token, 'timeout': 2 * ONE_MINUTE_IN_SECONDS})

    def check_websocket_token(self, retailerId, token):
        token_from_redis = self.get_value("redis", {'key': self.REDIS_STRING['wit'] + retailerId})
        if not token_from_redis:
            return False, self.ERROR_MSG['token_timeout']

        if unicode(token) != unicode(token_from_redis):
            return False, self.ERROR_MSG['token_verification_failed']

        return True, None

    def set_notification_in_current_day(self, msg_type, msg_id, msg_content):
        current_time = datetime.utcnow()
        scheduled_time = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
        if current_time > scheduled_time:
            total_seconds = (scheduled_time + timedelta(days=1) - current_time).total_seconds()
        else:
            total_seconds = (scheduled_time - current_time).total_seconds()

        self.set_dict_value("redis", {'name': self.REDIS_STRING['pnmfs'] + msg_type, 'key': msg_id,
                                      'value': msg_content, 'timeout': int(total_seconds)})

    def get_notification_in_current_day(self, msg_type, msg_id):
        dict_from_redis = self.get_dict_value("redis", {'name': self.REDIS_STRING['pnmfs'] + msg_type,
                                                        'key': msg_id})
        return dict_from_redis

    def delete_notification_in_current_day(self, msg_type, msg_id):
        self.delete_dict_value("redis", {'name': self.REDIS_STRING['pnmfs'] + msg_type, 'key': msg_id})
        return

    def get_all_notification_in_current_day(self, msg_type):
        dict_from_redis = self.get_all_dict_value("redis", {'name': self.REDIS_STRING['pnmfs'] + msg_type})
        return dict_from_redis

    def check_sms_code(self, phone, code_type, code):
        code_from_redis = self.get_value("value", {'key': code_type + phone})
        if not code_from_redis:
            return False, self.ERROR_MSG['sms_timeout']

        if unicode(code) != unicode(code_from_redis):
            return False, self.ERROR_MSG['sms_verification_failed']

        return True, None

    def check_image_code(self, key, code):
        code = code.lower()
        code_from_redis = redis.get_value("redis", {'key': key})
        if not code_from_redis:
            return False, self.ERROR_MSG['img_code_timeout']

        if unicode(code) != code_from_redis:
            return False, self.ERROR_MSG['img_code_verification_failed']

        return True, None

    def sms_set_cache(self, phone, code, code_type):
        self.set_value("redis", {'key': self.REDIS_STRING['si'] + phone, 'value': 1,
                                 'timeout': ONE_MINUTE_IN_SECONDS})
        self.set_value("redis", {'key': code_type + phone, 'value': code, 'timeout': ONE_MINUTE_IN_SECONDS})
        count_per_day = int(self.get_value("redis", {'key': self.REDIS_STRING['pspd'] + phone}))
        self.set_value("redis",
                       {'key': self.REDIS_STRING['pspd'] + phone, 'value': count_per_day + 1,
                        'timeout': ONE_DAY_IN_SECONDS})

    def image_code_set_cache(self, image_code_type, code):
        self.set_value("redis", {'key': image_code_type, 'value': code, 'timeout': ONE_MINUTE_IN_SECONDS})

    def ip_block_set_cache(self, remote_ip):
        failed_times = int(self.get_value("redis", {'key': self.REDIS_STRING['rat'] + remote_ip}))
        self.set_value("redis", {'key': self.REDIS_STRING['rat'] + remote_ip, 'value': failed_times + 1,
                                 'timeout': ONE_DAY_IN_SECONDS})
        return

    def reset_ip_block(self, remote_ip):
        self.set_value("redis", {'key': self.REDIS_STRING['rat'] + remote_ip, 'value': 0,
                                 'timeout': ONE_DAY_IN_SECONDS})
        return

    def check_if_block(self, remote_ip):
        if int(self.get_value("redis", {'key': self.REDIS_STRING['rat'] + remote_ip})) > 5:
            return True

        return False

    def check_if_can_send(self, phone):
        if self.get_value("redis", {'key': self.REDIS_STRING['si'] + phone}) in (1, '1'):
            return False, self.ERROR_MSG['sms_can_not_send_in_60']

        if int(self.get_value("redis", {'key': self.REDIS_STRING['si'] + phone})) > 10:
            return False, self.ERROR_MSG['sms_max_limit_per_day']

        return True, None


