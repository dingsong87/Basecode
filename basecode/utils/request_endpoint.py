SMS_API_PORT = 10088
UDM_API_PORT = 10087

class RouteHandler(object):

    def __init__(self, config):
        self.base_url = 'http://%s:%s'
        self.api_endpoint = dict()
        if config.get('api_port'):
            self.api_endpoint['LoopBack'] = self.base_url % ('127.0.0.1', config['api_port'])

        if config.get('service'):
            for service, entry in config['service'].items():
                self.api_endpoint[service] = self.base_url % (entry['host'], entry['api_port'])