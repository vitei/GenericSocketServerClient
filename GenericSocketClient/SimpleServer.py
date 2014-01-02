# TODO
# expand out login stuff to generate client-side representation of the world on login
# change sling so angle is relative to itself (i.e. 0-180 in semi-circle around building)
# Make Error| command to flash screen white
# start bringing more gameplay logic over here
    # contested buildings
    #
# start doing some error checking on the content/params and sending errors when hooky data is put through
# refactoring pass
# consider code autogeneration for client receiving transport
# consider code autogeneration for python server code (extend out commandDict?)
# consider adding "rooms" to add a 2nd layer of organisation (could perhaps be used to spatially separate communications)

from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
from pprint import pformat
import string


"""
@interface SpawnPlanetEvent : NSObject

        @property CGPoint center;
@property CGFloat innerRadius;
@property CGFloat surfaceRadius;
@property CGFloat orbitRadius;
@property NSUInteger population;
@property PlayerNum player;

@interface FireCatapultEvent : NSObject

@property NSUInteger planetID;
@property NSUInteger buildingID;
@property CGFloat slingAngle;
@property CGFloat force;

@interface BuildingCreateEvent : NSObject

@property NSUInteger onPlanetID;
@property CGFloat atPosition;
@property NSUInteger withNumberDenizens;
@property PlayerNum byPlayer;

event.center = CGPointMake([[[args componentsSeparatedByString:@" "] objectAtIndex:0] floatValue],
                                                           [[[args componentsSeparatedByString:@" "] objectAtIndex:1] floatValue]);
                                event.innerRadius = [[[args componentsSeparatedByString:@" "] objectAtIndex:2] floatValue];
                                event.surfaceRadius = [[[args componentsSeparatedByString:@" "] objectAtIndex:3] floatValue];
                                event.orbitRadius = [[[args componentsSeparatedByString:@" "] objectAtIndex:4] floatValue];
                                event.population = [[[args componentsSeparatedByString:@" "] objectAtIndex:5] intValue];
                                event.player = [[[args componentsSeparatedByString:@" "] objectAtIndex:6] intValue];

event.planetID = [[[args componentsSeparatedByString:@" "] objectAtIndex:0] floatValue];
                                event.buildingID = [[[args componentsSeparatedByString:@" "] objectAtIndex:1] floatValue];
                                event.slingAngle = [[[args componentsSeparatedByString:@" "] objectAtIndex:2] floatValue];
                                event.force = [[[args componentsSeparatedByString:@" "] objectAtIndex:3] floatValue];

BuildingCreateEvent *event = [[BuildingCreateEvent alloc] init];
                                event.onPlanetID = [[[args componentsSeparatedByString:@" "] objectAtIndex:0] floatValue];
                                event.atPosition = [[[args componentsSeparatedByString:@" "] objectAtIndex:1] floatValue];
                                event.withNumberDenizens = [[[args componentsSeparatedByString:@" "] objectAtIndex:2] floatValue];
                                event.byPlayer = [[[args componentsSeparatedByString:@" "] objectAtIndex:3] floatValue];

event.rotation = [[[args componentsSeparatedByString:@" "] objectAtIndex:0] floatValue];
                                event.scale = [[[args componentsSeparatedByString:@" "] objectAtIndex:1] floatValue];
                                event.position = CGPointMake([[[args componentsSeparatedByString:@" "] objectAtIndex:2] floatValue],
                                                             [[[args componentsSeparatedByString:@" "] objectAtIndex:3] floatValue]);

"""

class IphoneChat(Protocol):

    msgSelf   = []
    msgOthers = []
    msgServer = []
    # maybe get rid of this or refactor to message all
    commandPipe = []

    messageSeparator = "###"

    name = ""
    space = {}
    currentPlanetID = 0
    currentBuildingID = 0

    def connectionMade(self):
    
        self.factory.clients.append(self)
        self.msgServer.append("clients are %s" %self.factory.clients)

    def connectionLost(self, reason):
    
        self.msgServer.append("losing a connection")
        self.msgSelf.append("log|closing connection...")
        self.factory.clients.remove(self)

    def changeCamera(self, content):

        #camera|<rotation>|<scale>|<posX>|<posY>
        rotation = content[0]
        scale = content[1]
        posX = content[2]
        posY = content[3]

        self.msgServer.append("camera event triggered")
        self.msgSelf.append("log|changing camera to %s" %content)
        self.commandPipe.append("camera%s%s" % ("|", "|".join(content)))

    def displayHelp(self, content):

        whichHelp = content[0]
        
        if whichHelp in self.commandDict:
            self.msgServer.append("help invocated by %s for command %s" % (self.name, whichHelp))
            self.msgSelf.append(self.commandDict[whichHelp][2])

        elif whichHelp == "all":
            self.msgServer.append("help invocated with all")
            self.msgSelf.append("commands: %s" % self.commandDict.keys())
        else:
            self.msgServer.append("help invocated with non-present command")
            self.msgSelf.append("such a command doesn't exist, current commands include %s" % self.commandDict.keys())

    def sendMessage(self, content):

        msgToSend = content[0]
        self.msgServer.append("%s: %s" %(self.name, msgToSend))
        self.msgOthers.append("%s: %s" %(self.name, msgToSend))

    def printSpace(self):

        self.msgSelf.append("Space currently looks like this:\n%s" % pformat(self.space))
        self.msgServer.append("Request to print space received")

    def identifyWithName(self, content):
        
        name = content[0]

        if self.name == "":
            self.name = name
            self.msgServer.append("Client has identified with the name %s" %name)
            self.msgSelf.append("log|You have identified to the server with the name %s" %name)
            self.msgOthers.append("log|A client with name %s has joined" %name)
            self.commandPipe.append("iam%s%s" % ("|", "|".join(content)))

        else:
            self.msgServer.append("% has attempted to identify with the name %s. Ignoring this request." %(self.name, name))
            self.msgSelf.append("log|You have already identified with the name %s to the server" %self.name)

    def spawnPlanet(self, content):
        
        #planet|<x>|<y>|<innerRadius>|<surfaceRadius>|<orbitRadius>|<population>|<ownership>
        x = content[0]
        y = content[1]
        innerRadius = content[2]
        surfaceRadius = content[3]
        orbitRadius = content[4]
        population = content[5]
        ownership = content[6]

        # TODO: test for overlaps/collisions
        planet = {'buildings':{}, 'owner': ownership, 'population' : population, 'innerRadius' : innerRadius, 'surfaceRadius' : surfaceRadius, 'orbitRadius' : orbitRadius }

        self.space.update({str(self.currentPlanetID) : planet})
        self.msgServer.append("Attempting to spawn a planet with data %s" % planet)
        self.msgSelf.append("log|Attempting to spawn a planet with data %s" % planet)
        self.msgOthers.append("log|%s is attempting to spawn a planet with data %s" % (self.name, planet))
        self.currentPlanetID += 1

        self.commandPipe.append("planet%s%s" % ("|", "|".join(content)))
        
        self.printSpace()
        
    # should I think about a building ID
    def spawnBuilding(self, content):

        #building|<planetID>|<position>|<numberDenizens>|<ownership>
        planetID  = content[0]
        position  = content[1]
        denizens  = content[2]
        ownership = content[3]

        # test if planet actually exists
        
        if planetID in self.space:
        
            building = { "id" : self.currentBuildingID, "position" : position, "ownership" : ownership, "denizens" : denizens}
            self.space[planetID]['buildings'].update({str(self.currentBuildingID) : building})
            self.msgServer.append("%s spawned a building with data %s" %(self.name, content))
            self.msgSelf.append("Spawning a building with data %s" %content)
            self.msgOthers.append("%s spawned a building with data %s" %(self.name, content))
            self.commandPipe.append("building%s%s" % ("|", "|".join(content)))

            self.printSpace()
            self.currentBuildingID += 1
        
        else:
        
            self.msgSelf.append("Attempting to spawn a building on a non-existant planet")
            self.msgServer.append("%s attempting to spawn a building on a non-existant planet" % (self.name))

    def fireCatapult(self, content):
        
        planetID = content[0]
        buildingID = content[1]
        slingAngle = content[2]
        force = content[3]

        del self.space[planetID]['buildings'][buildingID]

        # TODO: Check if valid output
        self.msgServer.append("%s is firing catapult from planetID: %s buildingID: %s with angle %s and force %s" % (self.name, planetID, buildingID, slingAngle, force))
        self.msgSelf.append("firing catapult from planetID: %s buildingID: %s with angle %s and force %s" % (planetID, buildingID, slingAngle, force))
        self.msgOthers.append("%s is firing catapult from planetID: %s buildingID: %s with angle %s and force %s" % (self.name, planetID, buildingID, slingAngle, force))
        self.commandPipe.append("sling%s%s" % ("|", "|".join(content)))
 
    # number represents number of arguments
    # string represents help for the command
    commandDict = { "iam" : [1, identifyWithName, "iam|<name>\n    identifies with the server\n    <name> - name you wish to identify with\n\n"], 
                    "msg" : [1, sendMessage, "msg|<content>\n    \n    sends a message across the server\n    <content> - the content of the message to send\n\n"], 
                    "planet" : [7, spawnPlanet, "planet|<x>|<y>|<innerRadius>|<surfaceRadius>|<orbitRadius>|<population>|<ownership>\n    spawns a planet\n\n"], 
                    "sling" : [4, fireCatapult, "sling|<planetID>|<buildingID>|<slingAngle>|<force>\n    fires a catapult from a specified planet with a given force\n\n"], 
                    "building" : [4, spawnBuilding, "building|<planetID>|<position>|<numberDenizens>|<ownership>\n    spawns a build on a specified planet holding a number of citizens and owned by a specified player\n\n"], 
                    "camera" : [4, changeCamera, "camera|<rotation>|<scale>|<posX>|<posY>\n    change the position of the camera in the world\n\n"], 
                    "help" : [1, displayHelp, "help|<command>\n    display help on a given command\n\n"],
                    "quit" : [0, connectionLost, "quit\n    quit from the server\n\n"],
                    "space" : [0, printSpace, "space\n    print the current status of space\n\n"] }

    def dataReceived(self, data):
        
        data = data.rstrip('\r\n')
        dataIntoArray = data.split('|')
        command = dataIntoArray[0]
        content = dataIntoArray[1:len(dataIntoArray)]
        
        """print "data is %s" % data
        print "dataIntoArray is %s" % dataIntoArray
        print "command is %s" % command
        print "content is %s" % content
        print "len(content) is %s" % len(content)"""

        if command in self.commandDict:
            
            expectedNumArgs = self.commandDict[command][0]
            functionToExecute = self.commandDict[command][1]
            functionHelpText = self.commandDict[command][2]

            if expectedNumArgs == 0 and len(content) == 0:
                functionToExecute(self)

            elif len(content) != expectedNumArgs:
                self.sendMessage("Incorrect Args, try %s\n" % functionHelpText)
            
            else:
                functionToExecute(self, content)
        
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
                #print "DEBUG >>> c.name: %s" % c.name
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

factory = Factory()
factory.clients = []
factory.protocol = IphoneChat
print "Virius Multiplayer Server Started"
reactor.listenTCP(80, factory)
reactor.run()
