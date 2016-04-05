import redis
import json


class RedisEngine(object):
    _redis_db = None

    def __init__(self, config):
        try:
            super(RedisEngine, self).__init__(config)
        except Exception as ex:
            print "not right class: %s" % ex
        config = config['redis']
        redis_host = config['host']
        redis_port = config['port']
        RedisEngine.init_redis(redis_host, redis_port)

    @classmethod
    def init_redis(cls, host, port):
        if not cls._redis_db:
            print "create redis connection"
            cls._redis_db = redis.Redis(host, port)

    @classmethod
    def set_dict_value(cls, db, data):
        if db == "redis":
            try:
                data['value'] = json.dumps(data['value'])
                if data.get('timeout'):
                    cls._redis_db.expire(data['name'], data['timeout'])
                    cls._redis_db.hset(data['name'], data['key'], data['value'])
                else:
                    cls._redis_db.hset(data['name'], data['key'], data['value'])

            except Exception as ex:
                print "hset redis: %s" % ex
                return False

            return True

        return False

    @classmethod
    def get_dict_value(cls, db, data):
        if db == "redis":
            try:
                result = cls._redis_db.hget(data['name'], data['key'])
                result = json.loads(result)
                return result if result else None
            except Exception as ex:
                print "hget redis: %s" % ex
                return None

        return None

    @classmethod
    def set_value(cls, db, data):
        if db == "redis":
            try:
                if data.get('timeout'):
                    cls._redis_db.setex(data['key'], data['value'], data['timeout'])
                else:
                    cls._redis_db.set(data['key'], data['value'])
            except Exception as ex:
                print "set redis: %s" % ex
                return False

            return False

        return False

    @classmethod
    def get_value(cls, db, data):
        if db == "redis":
            try:
                result = cls._redis_db.get(data['key'])
                return result if result else '0'
            except Exception as ex:
                print "get redis: %s" % ex
                return '-1'

        return '-1'
