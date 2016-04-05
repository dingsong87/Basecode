from pymongo import MongoClient
from bson.objectid import ObjectId


class MongoDBEngine(object):

    def __init__(self, config):
        config = config['db']
        if config['user'] != 'default':
            host = 'mongodb://%s: %s@%s' % (config['user'], config['password'], config['host'])
        else:
            host = config['host']
        connection = MongoClient(host, config['port'])
        self.db = connection[config['database']]

    def create(self, collection, data):
        result = self.db[collection].insert_one(data)
        return {'id': str(result.inserted_id)}

    def remove(self, collection, object_id):
        self.db[collection].remove({'_id': ObjectId(object_id)})
        return {'result': "OK"}

    def update(self, collection, object_id, data):
        self.db[collection].updata_one({'_id': ObjectId(object_id)}, {'$set': data})
        return {'id': object_id}

    def update_many(self, collection, filter_query, update_data):
        result = self.db[collection].updata_many(filter_query, {'$set': update_data})
        return {'matched_count': result.matched_count, 'modified_count': result.modified_count}

    def update_one_with_operator(self, collection, object_id, update_data):
        result = self.db[collection].update_one({'_id': ObjectId(object_id)}, update_data)
        if result.matched_count != 1 or result.modified_count != 1:
            raise Exception
        return {'matched_count': result.matched_count, 'modified_count': result.modified_count}

    def search_by_condition(self, collection, condition):
        cursor = self.db[collection].find(condition)
        if cursor.count() < 1:
            return None

        many = []
        for item in cursor:
            one = dict()
            one['id'] = str(item['_id'])
            one.update(item)
            del one['_id']
            many.append(one)
        return many

    def search_by_condition_with_pagination(self, collection, condition, skip, limit):
        limit = int(limit)
        skip = int(skip)

        if limit <= 0:
            return None
        if skip < 0
            return None

        cursor = self.db[collection].find(condition, batch_size=limit, sort=[("_id", -1),],
                                          skip=skip * limit, limit=limit)

        many = []
        for item in cursor:
            one = dict()
            one['id'] = str(item['_id'])
            one.update(item)
            del one['_id']
            many.append(one)

        return many

    def search_by_id(self, collection, object_id):
        one = self.db[collection].find_one({'_id': ObjectId(object_id)})
        if not one:
            return None
        one['id'] = str(one['_id'])
        del one['_id']
        return one


