import json
import abc
import requests
import geoip2.database as geodb
from geoip2.records import City

class BaseGEOIPProvider(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def getCity(self, ip): return

    @abc.abstractmethod
    def getCountry(self, ip): return

    @abc.abstractmethod
    def getLatLon(self, ip): return

class FreeGeoIPProvider(BaseGEOIPProvider):
    """ Make requests to the freegeoip.net API for IP information """
    def getLocationDict(self, ip):
        jsonInfo = requests.get("http://freegeoip.net/json/" + ip)
        return json.loads(jsonInfo.text.encode('ascii','ignore'))

    def getCity(self, ip):
        return (self.getLocationDict(ip))['city']

    def getCountry(self, ip):
        return (self.getLocationDict(ip))['country_name']

    def getLatLon(self, ip):
        jsonDict = self.getLocationDict(ip)
        return (jsonDict['latitude'], jsonDict['longitude'], None)

class MaxMindIPProvider(BaseGEOIPProvider):
    """ Access a maxmind geoip2 City database for IP information """
    def __init__(self, dbFilename):
        self.cityDB = geodb.Reader(dbFilename)

    def getCityObject(self, ip):
        try:
            return self.cityDB.city(ip)
        except Exception as e:
            # return a blank city object if we have trouble
            return City()

    def getCity(self, ip):
        try:
            return self.getCityObject(ip).city.name
        except Exception as e:
            return ''

    def getCountry(self, ip):
        #TODO: Make these methods consistent
        try:
            return self.cityDB.city(ip).country.name
        except:
            return None

    def getLatLon(self, ip):
        try:
            location = self.cityDB.city(ip).location
            rv = (location.latitude,location.longitude, location.accuracy_radius)
        except Exception as e:
            rv = (0,0,0)
        return rv
