from geo_ip import GeoIP
from file_parser import FileParser
from ip_filter import IPFilter
from rdap_lookup import RDAPLookup

import sys
from multiprocessing import Pool

def mergeDicts(x, y):
    z = x.copy()
    z.update(y)
    return z

def getCombinedDataDict(ip):
    print "ip", ip
    geolookup = GeoIP()
    rdaplookup = RDAPLookup()
    combinedDict = mergeDicts(geolookup.getLocationDict(ip), rdaplookup.getRDAPDict(ip))
    return combinedDict

if __name__ == '__main__':
    try:
        filename = sys.argv[1]
        print "Parsing", filename
    except IndexError:
        filename = raw_input("Please enter a filename to parse IP Addresses from: ")
    parser = FileParser()
    ipAddresses = parser.parseFile(filename)
    print len(ipAddresses), "IP addresses found in file. Performing GeoIP and RDAP Lookup"
    combinedDataList = []
    p = Pool(8)
    results = p.map(getCombinedDataDict, ipAddresses)
    p.close()
    p.join()

    print results
    # for ip in ipAddresses:
    #     print "pulling data for ", ip
    #     threads.append(threading.Thread(target = getCombinedDataDict, args=(ip, globalResultList)))
    #
    # print globalResultList
