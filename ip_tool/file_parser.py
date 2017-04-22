import sys

if __name__ == '__main__':
    filename = None
    try:
        filename = sys.argv[1]
        inFile = open(filename, 'r')
    except Exception as e:
        print e

    #Read some bytes, process some bytes.
    #Handle an IP address in the middle of the read chunk...
    #Maybe look for something that looks like the start of an IP address
    #and then read some bytes after that and regex the thing out of it.

    #How do we handle IP addresses that are right next to each other?
    try:
        infile.close()
    except:
        pass
