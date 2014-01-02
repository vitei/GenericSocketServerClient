from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
import argparse
import json

class SimpleGenericServer(Protocol):

    msgSelf   = []
    msgOthers = []
    msgServer = []
    commandPipe = []

    messageSeparator = ""

    def connectionMade(self):

        self.factory.clients.append(self)
        self.msgServer.append("clients are %s" % self.factory.clients)
        self.name = "test"

    def connectionLost(self, reason):
    
        self.msgServer.append("losing a connection")
        self.msgSelf.append("log|closing connection...")
        self.factory.clients.remove(self)

    def runFunction(self, event):

        self.msgServer.append("command triggered")
        self.msgSelf.append("command triggered")
        self.commandPipe.append(event)

    def sendMessage(self, content):

        msgToSend = content[0]
        self.msgServer.append("%s: %s" %(self.name, msgToSend))
        self.msgOthers.append("%s: %s" %(self.name, msgToSend))

    def dataReceived(self, data):
        
        data = data.rstrip('\r\n')
        dataIntoArray = data.split('|')
        command = dataIntoArray[0]
        params = dataIntoArray[1:len(dataIntoArray)]

        if command in self.factory.idl["events"]:
            
            expectedNumArgs   = len(self.factory.idl["events"][command]["params"])
            functionToExecute = self.runFunction
            functionHelpText  = "this is just a test"

            if expectedNumArgs == 0 and len(content) == 0:
                functionToExecute(self.factory.idl["events"][command])

            elif len(params) != expectedNumArgs:
                self.sendMessage("Incorrect Args, try %s\n" % functionHelpText)
            
            else:
                functionToExecute(data)
        
        else:
            self.msgServer.append("Invocation of unknown command")
            self.msgSelf.append("Invocation of unknown command") 

        
        if self.name != "":
            self.processMessages()
        else:
            self.sendMessage("Please identify with the server first\n")

    def sendMessage(self, message):
        
        self.transport.write(message)

    def processMessages(self):
        
        for c in self.factory.clients:
            
            for message in self.msgServer:
                
                print self.msgServer
                print "%s\n" % self.messageSeparator

            if c.name != self.name:
                for message in self.msgOthers:
                    c.sendMessage("%s\n" % message)
                    c.sendMessage("%s\n" % self.messageSeparator)

            else:
                for message in self.msgSelf:
                    c.sendMessage("%s\n" % message)
                    c.sendMessage("%s\n" % self.messageSeparator)    
            
            for message in self.commandPipe:
                c.sendMessage("%s\n" % message)
                c.sendMessage("%s\n" % self.messageSeparator)

        del self.msgSelf[:]
        del self.msgServer[:]
        del self.msgOthers[:]
        del self.commandPipe[:]

class SimpleGenericServerFactory(Factory):

    protocol = SimpleGenericServer

    def __init__(self, idl):
        self.idl = idl or 'No IDL was defined!'

# initial argument parsing
parser = argparse.ArgumentParser(description="Start a generic python server")
parser.add_argument('port', type=int, help="the number of the port to use")
parser.add_argument('idl', help="the definition file to use")
args = parser.parse_args()

# parse idl
json_data = open(args.idl)
idl = json.load(json_data)

# server setup
factory = SimpleGenericServerFactory(idl)
factory.clients = []
factory.protocol = SimpleGenericServer
print "Simple Generic Server Started on port %d with definition file %s" % (args.port, args.idl)
reactor.listenTCP(args.port, factory)
reactor.run()