from geo_ip import MaxMindIPProvider
from file_parser import FileParser
from ip_filter import IPFilter
from rdap_lookup import RDAPLookup

import sys
from multiprocessing import Pool
import json

import wx

def mergeDicts(x, y): #Built in way to combine two dictionaries is a python 3 feature
    z = x.copy()
    z.update(y)
    return z

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
    app = wx.App()
    frame = wx.Frame(None, -1, 'iptool.py')
    frame.Show()
    app.MainLoop()