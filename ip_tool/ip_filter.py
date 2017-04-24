from ast import literal_eval

class IPFilter(object):
    """Accept list of dictionaries and provide methods for accessing
    subsets of that data through user input"""
    def __init__(self, dataList):
        self.geoIPFilterKeys = ['ip','country_code', 'country_name', 'region_code',
                           'region_name', 'city', 'longitude','latitude','zip_code']
        self.rdapFilterKeys = ['handle', 'name', u'links', u'entities', u'port43',
                         u'endAddress', u'parentHandle', u'ipVersion', u'startAddress',
                          u'rdapConformance', u'notices', u'objectClassName', u'events']
        self.keys = self.geoIPFilterKeys + self.rdapFilterKeys
        self.data = dataList

    def userQuery(self, query):
        """ Take user query string, parse and return data """
        displayKeys, conditions = self.parseQuery(query)
        return self.query(displayKeys, conditions)

    def parseQuery(self, query):
        """ Strip non essential syntax from query and return list of strings
        and conditional tuple for use in query function. Throws exception if
        command cannot be parsed """
        stripQuery = query.strip("GET")
        splitQuery = stripQuery.split("WHERE")

        selections = splitQuery[0].strip()
        selections = literal_eval(selections)

        conditions = splitQuery[1].strip()
        conditions = literal_eval(conditions)

        return selections, conditions

    def query(self, displayKeys, conditions):
        """ Take a list of information to retrieve, and a list of tuples of
        conditional statements in the form (key, operator, value) and return a list """
        subset = []
        for cond in conditions:
            queryString = "record['" + cond[0] + "'] " + cond[1] + " '" +cond[2] + "'"
            for record in self.data:
                try:
                    if eval(queryString):
                        subset.append(record)
                except:
                    pass #ignore errors and keep trying (usually key errors)

        displayData = []
        for record in subset:
            displayRecord = []
            for key in displayKeys:
                try:
                    queryString = "record['" + key + "']"
                    displayRecord.append((key, eval(queryString)))
                except:
                    pass
            displayData.append(displayRecord)
        return displayData

    def printHelp(self):
        print
        print "Sample Query:"
        print "GET ['ip', 'events'] WHERE [('country_code','==','US')]"
        print
        print "Available Query Keys:", self.keys

if __name__ == '__main__':
    with open('testoutput', 'r') as f:
        ip = IPFilter(eval(f.read()))
        # displayKeys, conditions = ip.parseQuery("GET ['ip', 'events'] WHERE [('country_code','==','US')]")
        # ip.query(displayKeys, conditions)

        displayKeys, conditions = ip.parseQuery("GET ['ip', 'city', 'events'] WHERE [('city','!=','')]")
        data = ip.query(displayKeys, conditions)
        ip.printHelp()
