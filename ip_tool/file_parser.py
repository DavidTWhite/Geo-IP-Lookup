import sys
import re

regex = re.compile("((?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9])\."
                   "(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9])\."
                   "(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9])\."
                   "(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9]))")

def parseChunk(inputStr):
    return regex.findall(inputStr)

if __name__ == '__main__':
    filename = None
    inFile = None
    ipaddresses = []
    try:
        filename = sys.argv[1]
        inFile = open(filename, 'r')
    except Exception as e:
        print e
    else:
        chunk = inFile.read(1024)
        while chunk:
            ipaddresses += parseChunk(chunk)
            #backtrack 16 bytes so we can't miss an IP
            #by splitting it during the read
            if len(chunk) == 1024:
                inFile.seek(-16, 1)
            chunk = inFile.read(1024)

    print set(ipaddresses)
    try:
        inFile.close()
    except Exception as e:
        print e
