import requests
import json

class RDAPLookup(object):
    """ Lookup RDAP info for given ips from rdap.arin.net """
    def makeRDAPRequest(self,ip):
        return requests.get("http://rdap.arin.net/bootstrap/ip/" + ip)

    def getRDAPDict(self, ip):
        """ Request RDAP info for given ip and return dictionary """
        returnDict = {}
        try:
            jsonData = self.makeRDAPRequest(ip)
            returnDict = json.loads(jsonData.text.encode('ascii','ignore'))
        except Exception as e:
            returnDict['RDAPError'] = str(e)
        returnDict['ip'] = ip
        return returnDict

    def getBulkRDAPInfo(self, ipList):
        return [self.getRDAPDict(ip) for ip in ipList]
