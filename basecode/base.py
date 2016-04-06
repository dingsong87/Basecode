from .utils import RouteHandler
from .utils import UtilBase

from .database import MongoDBBase
from .database import RedisBase


class BaseCode(RouteHandler, UtilBase):

    def __init__(self, config):
        super(BaseCode, self).__init__(config)


class RedisBaseCode(RedisBase, RouteHandler, UtilBase):

    def __init__(self, config):
        super(RedisBaseCode, self).__init__(config)


class MongoBaseCode(RouteHandler, UtilBase):

    def __init__(self, config):
        super(MongoBaseCode, self).__init__(config)
        self.storage = MongoDBBase(config)