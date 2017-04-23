from geo_ip import GeoIP
from file_parser import FileParser
from ip_filter import IPFilter
from rdap_lookup import RDAPLookup

import sys

if __name__ == '__main__':
    try:
        filename = sys.argv[1]
        print "Parsing", filename
    except IndexError:
        filename = raw_input("Please enter a filename to parse IP Addresses from: ")
    parser = FileParser()
    ipAddresses = parser.parseFile(filename)
    print len(ipAddresses), "IP addresses found in file. Performing GeoIP and RDAP Lookup"
    geolookup = GeoIP()
    ipLookupData = geolookup.getBulkLocationInfo(ipAddresses)
    print ipLookupData
    #rdap = RDAPLookup()
    #rdapData = rdap.performQueries(ipAddresses)
