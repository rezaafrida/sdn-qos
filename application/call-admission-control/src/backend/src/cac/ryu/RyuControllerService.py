'''
Documentation:
    - https://osrg.github.io/ryu-book/en/html/rest_qos.html
    - https://osrg.github.io/ryu-book/en/html/rest_qos.html#rest-api-list
    - https://ryu.readthedocs.io/en/latest/app/ofctl_rest.html#get-queues-stats

'''

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)

class RyuController():
    OVSDB = '/v1.0/conf/switches/'
    STATS_FLOW = '/stats/flow/' # <dpid>
    STATS_PORT = '/stats/port/' # <dpid>/[port-id]
    STATS_PORTDESC = '/stats/portdesc/' # <dpid>
    STATS_QUEUES = '/stats/queue/' # <queue-id>
    STATS_QUEUE_CONFIG = '/stats/queueconfig/' # <dpid>/[port-id]
    DELETE_ALL_FLOW_ENTRIES = '/stats/flowentry/clear/' # <dpid>
    QOS_RULES = '/qos/rules/' # <dpid>
    QOS_QUEUES = '/qos/queue/' # <dpid>    
    TOPOLOGY_SWITCHES = '/v1.0/topology/switches'
    TOPOLOGY_LINKS = '/v1.0/topology/links'
    MEDIA_PORT = '5606'

    def __init__(self, host, port, ovsdbConfiguration=None):
        self.switches = []
        self.links = []
        self.topology = {}
        self.api = host + ':' + port
        if ovsdbConfiguration != None:
            self.connectOVSDB(ovsdbConfiguration['ip'], ovsdbConfiguration['port'], \
                ovsdbConfiguration['protocol'], ovsdbConfiguration['switch'])

    def connectOVSDB(self, ip, port, protocol, switch):
        data = protocol + ':' + ip + ':' + port
        url = self.api + self.OVSDB + switch + '/ovsdb_addr'

        logging.info(data)
        logging.info(url)

        response = requests.put(url, json=data)
        return response.status_code

    def getTopologySwitches(self):
        response = requests.get(self.api + self.TOPOLOGY_SWITCHES)
        self.switches = response.json()
        # logging.info(self.switches)
        return self.switches

    def getSwitches(self):
        return self.switches

    def getTopologyLinks(self):
        response = requests.get(self.api + self.TOPOLOGY_LINKS)
        self.links = response.json()
        # logging.info(self.links)
        return self.links

    def getLinks(self):
        return self.links

    def buildTopology(self):
        self.topology['switches'] = self.getTopologySwitches()
        self.topology['links'] = self.getTopologyLinks()
    
    def getTopology(self):
        return self.topology

    def buildQueue(self, port, queues):
        queueData = {}
        queueData['port_name'] = port
        queueData['type'] = 'linux-htb'
        queueData['max_rate'] = '1000000'
        queueData['queues'] = []
        for queue in queues:
            queueData['queues'].append(queue)

        return queueData

    def configureQoSQueue(self, switch, port, queues):
        queueData = self.buildQueue(port, queues)
        response = requests.post(self.api + self.QOS_QUEUES + switch, json=queueData)
        result = response.json()

    def getQoSQueue(self, switch):
        response = requests.get(self.api + self.QOS_QUEUES + switch)
        result = response.json()
        logging.info(result)
        return result

    def configureQoSRule(self, switch, port, rule):
        pass

    def getQoSRule(self, switch):
        pass

    def deleteQoS(self):
        pass

if __name__ == '__main__':
    logging.info('starting app...')
    # Esto se deberia sacar de un inventario de dispositivos OVS en la red
    # Por el momento, podemos cargar los switches del laboratorio en settings.py
    ovsdbConfig = {}
    ovsdbConfig['ip'] = '127.0.0.1'
    ovsdbConfig['port'] = '6632'
    ovsdbConfig['protocol'] = 'tcp'
    ovsdbConfig['switch'] = '0000000000000001'
    
    ryuService = RyuController('http://127.0.0.1', '8080', ovsdbConfiguration=ovsdbConfig)
    logging.info('switches')
    ryuService.getTopologySwitches()
    logging.info('links')
    ryuService.getTopologyLinks()
    ryuService.getLinks()
    logging.info('topology')
    ryuService.buildTopology()
    topology = ryuService.getTopology()
    logging.info(topology)
    # configure queues
    logging.info('configure queues')
    for switch in topology['switches']:
        for port in switch['ports']:
            logging.info('configure queue for switch {}, port {}: '.format(switch['dpid'], port['name']))
            queues = [
                        {"max_rate": "300000"},
                        {"max_rate": "100000"},
                        {"min_rate": "50000"}
                    ]
            rules = [
                        {"match": {"ip_dscp": "26"}, "actions":{"queue": "0"}},
                        {"match": {"ip_dscp": "10"}, "actions":{"queue": "1"}},
                        {"match": {"ip_dscp": "12"}, "actions":{"queue": "2"}}
                    ]
            ryuService.configureQoSQueue(switch['dpid'], port['name'], queues)
            ryuService.configureQoSRule(switch['dpid'], port['name'], rules)
    # get queues
    logging.info('get queues')
    for switch in topology['switches']:
        logging.info('queue for switch: {}'.format(switch['dpid']))
        ryuService.getQoSQueue(switch['dpid'])