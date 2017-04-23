class IPFilter(object):
    def __init__(self, ips = None):
        self.filterKeys = ['ip','country_code', 'country_name', 'region_code', 'region_name', 'city', 'longitude','latitude','zip_code']
        self.data = ips

    def filter(query='all'):
        query
