from geo_ip import GeoIP, MaxMindIPProvider
from file_parser import FileParser
from ip_filter import IPFilter
from rdap_lookup import RDAPLookup

import sys
from multiprocessing import Pool
import json

def mergeDicts(x, y): #Built in way to combine two dictionaries is a python 3 feature
    z = x.copy()
    z.update(y)
    return z

def getCombinedDataDict(ip):
    geolookup = GeoIP()
    rdaplookup = RDAPLookup()
    combinedDict = mergeDicts(geolookup.getLocationDict(ip), rdaplookup.getRDAPDict(ip))
    return combinedDict

def getRDAP(ip):
    rdaplookup = RDAPLookup()
    return rdaplookup.getRDAPDict(ip)

def rdapLookup(ipList):
    rdaplookup = RDAPLookup()
    results = []
    p = Pool(8)     #Using fewer workers reduces risk of connection refusal from lookup servers
    numTasks = len(ipList)
    for i, result in enumerate(p.imap_unordered(getRDAP, ipList), 1):
        try:
            sys.stderr.write('\rProgress: {0:.2%}'.format(i/float(numTasks)))
            results.append(result)
        except Exception as e:
            print e
    p.close()
    p.join()
    return results

if __name__ == '__main__':
    try:
        filename = sys.argv[1]
        print "Parsing", filename
    except IndexError:
        filename = raw_input("Please enter a filename to parse IP Addresses from: ")
    parser = FileParser()
    ipAddresses = parser.parseFile(filename)
    print len(ipAddresses), "IP addresses found in file. Performing RDAP Lookup"
    results = rdapLookup(ipAddresses)
    print "Finished RDAP lookup"
    mmIP = MaxMindIPProvider('C:\Users\david\OneDrive\Documents\pythonIPtool\ip_tool\geoIPdatabases\GeoLite2-City_20170404\GeoLite2-City.mmdb')
    geoList = [{'ip':ip} for ip in ipAddresses]
    for each in geoList:
        each['city'] = mmIP.getCity(each['ip'])
    print "GeoIPResults: ", geoList

    queryTool = IPFilter(results)
    queryTool.printHelp()
    while True:
        print
        print "Type 'exit' to quit and 'help' to see query help"
        print
        userInput = raw_input("Enter Your Query: ")
        if userInput.lower() == 'exit':
            break
        elif userInput.lower() == 'help':
            queryTool.printHelp()
        else:
            try:
                userData = queryTool.userQuery(userInput)
            except Exception as e:
                print "Error in query:", e
            else:
                for record in userData:
                    print "-------------------"
                    for requestedKey in record:
                        print requestedKey[0],':', requestedKey[1]
                    print "-------------------"
