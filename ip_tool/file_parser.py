import re

class FileParser(object):

    def __init__(self):
        self.inFile = None
        self.regex = re.compile("((?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9])\."
                           "(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9])\."
                           "(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9])\."
                           "(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]?[0-9]))")

    def __parseChunk(self, inputStr):
        return self.regex.findall(inputStr)

    def parseFile(self, filename):
        with open(filename) as inFile:
            ipaddresses = []
            chunk = inFile.read(1024)
            while chunk:
                ipaddresses += self.__parseChunk(chunk)
                #backtrack so we can't miss an IP
                #by splitting it during the read (unless at EOF)
                if len(chunk) == 1024:
                    inFile.seek(-16, 1)
                chunk = inFile.read(1024)
        return list(set(ipaddresses))    #no duplicates
