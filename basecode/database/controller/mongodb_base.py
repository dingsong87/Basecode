from ..engine.mongodb_engine import MongoDBEngine
from datetime import datetime


class MongoDBBase(MongoDBEngine):

    def __init__(self, config):
        super(MongoDBBase, self).__init__(config)

    def two_phase_commit(self, watch_coll, main_coll, entity_data, update_data, object_id):
        result = self.create(watch_coll, entity_data)

        update_data.update({'$push': {'pendingTransactions': result['id']}})

        self.update_one_with_operator(main_coll, object_id, update_data)

        self.update(watch_coll, result['id'], {'state': 'Applied', 'lastModifiedDate': datetime.utcnow()})

        self.update_one_with_operator(main_coll, object_id, {'$pull': {'pendingTransactions': result['id']}})

        self.update(watch_coll, result['id'], {'state': 'Done', 'lastModifiedDate': datetime.utcnow()})