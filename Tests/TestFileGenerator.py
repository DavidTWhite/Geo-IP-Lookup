from datetime import datetime
import random
import string

def generateSomeCharacters():
    return ''.join(random.sample(string.ascii_letters, random.randint(0,9)))

if __name__ == '__main__':
    outfilename = "TestInput-" + datetime.now().strftime("%d-%m-%y-%H-%M-%S")
    outputFile = open(outfilename, 'w')
    ipfile = open('IPAddresses.txt', 'r')
    for ip in ipfile:
        outputFile.write(generateSomeCharacters())
        outputFile.write(ip.strip())
    outputFile.write(generateSomeCharacters())
    outputFile.close()
    ipfile.close()
