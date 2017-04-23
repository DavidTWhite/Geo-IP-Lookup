import requests
import json

class GeoIP(object):

    def __init__(self):
        self.requestFormats = ('json', 'csv', 'xml', 'jsonp')

    def getRawLocationInfo(self, ip, dataFmt='json'):
        if dataFmt not in self.requestFormats:
            raise ValueError("dataFmt argument must be one of " + requestFormats)
        return requests.get("http://freegeoip.net/" + dataFmt + "/" + ip)

    def getBulkLocationInfo(self, ipList):
        return [self.getLocationDict(x) for x in ipList]

    def getLocationDict(self, ip):
        print "getting info for", ip
        jsonInfo = self.getRawLocationInfo(ip, dataFmt='json')
        return json.loads(jsonInfo.text.encode('ascii','ignore'))
