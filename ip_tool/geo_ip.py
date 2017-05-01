import requests
import json
import abc
import geopip2.database as geodb

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

class FreeGeoIPProvider(BaseGEOIPProvider):
    """ Make requests to the freegeoip.net API for IP information """
    def getLocationDict(self, ip):
        jsonInfo = requests.get("http://freegeoip.net/json/" + ip)
        return json.loads(jsonInfo.text.encode('ascii','ignore'))

    def getCity(self, ip):
        return self.getLocationDict(ip)['city']

    def getCountry(self, ip):
        return self.cityDB.city(ip).city.country.name

    def getLatLon(self, ip):
        return (self.cityDB.city(ip).location.latitude,
                self.cityDB.city(ip).location.longitude,
                self.cityDB.city(ip).location.accuracy_radius)

class MaxMindIPProvider(BaseGEOIPProvider):
    """ Access a maxmind geoip2 City database for IP information """
    def __init__(self, dbFilename):
        self.cityDB = geodb.Reader(dbFilename)

    def getMaxMindCity(self, ip):
        return self.cityDB.city(ip)

    def getCity(self, ip):
        return self.cityDB.city(ip).city.name

    def getCountry(self, ip):
        return self.cityDB.city(ip).city.country.name

    def getLatLon(self, ip):
        return (self.cityDB.city(ip).location.latitude,
                self.cityDB.city(ip).location.longitude,
                self.cityDB.city(ip).location.accuracy_radius)

class BaseGEOIPProvider(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def getCity(self, ip): return

    @abc.abstractmethod
    def getCountry(self, ip): return

    @abc.abstractmethod
    def getLatLon(self, ip): return

    @abc.abstractmethod
    def getContinent(self, ip): return

    @abc.abstractmethod
    def getLocationSubdivisions(self, ip): return
