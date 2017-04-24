import requests
import json

class GeoIP(object):
    """Make requests for geo IP lookups from freegeoip.net"""
    def __init__(self):
        self.requestFormats = ('json', 'csv', 'xml', 'jsonp')

    def getRawLocationInfo(self, ip, dataFmt='json'):
        """Request geo ip info and return string"""
        if dataFmt not in self.requestFormats:
            raise ValueError("dataFmt argument must be one of " + requestFormats)
        return requests.get("http://freegeoip.net/" + dataFmt + "/" + ip)

    def getBulkLocationInfo(self, ipList):
        return [self.getLocationDict(x) for x in ipList]

    def getLocationDict(self, ip):
        """Take an ip address as string and return a dictionary"""
        returnDict = {}
        try:
            jsonInfo = self.getRawLocationInfo(ip, dataFmt='json')
            returnDict = json.loads(jsonInfo.text.encode('ascii','ignore'))
        except Exception as e:
            returnDict['ip'] = ip
            returnDict['GeoIPError'] = str(e)
        return returnDict
