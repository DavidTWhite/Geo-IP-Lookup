import requests
import json

class RDAPLookup(object):
    def __init__(self):
        self.rdapKeys = [u'handle', u'name', u'links', u'entities', u'port43',
                         u'endAddress', u'parentHandle', u'ipVersion', u'startAddress',
                          u'rdapConformance', u'notices', u'objectClassName', u'events']

    def makeRDAPRequest(self,ip):
        return requests.get("http://rdap.arin.net/bootstrap/ip/" + ip)

    def getRDAPDict(self, ip):
        jsonData = self.makeRDAPRequest(ip)
        return json.loads(jsonData.text.encode('ascii','ignore'))

    def getBulkRDAPInfo(self, ipList):
        return [self.getRDAPDict(ip) for ip in ipList]
