//
//  GenericClient.h
//
//  Created by Liam on 2/1/2014.
//  Copyright (c) 2013 Liam Conroy (Vitei). All rights reserved.
//

#import "AppDelegate.h"
#import "GenericClient.h"

/*[[[cog
 from autogen import CodeGenerator
 cg = CodeGenerator("transport.idl")
 cog.outl(cg.generateEventStructures())
 ]]]*/


@interface FireCatapultEvent : NSObject

@property CGFloat force;
@property NSUInteger planetID;
@property CGFloat slingAngle;
@property NSUInteger buildingID;

@end


@implementation FireCatapultEvent

@synthesize force;
@synthesize planetID;
@synthesize slingAngle;
@synthesize buildingID;
@end

@interface CreateBuildingEvent : NSObject

@property NSUInteger byPlayer;
@property CGFloat atPosition;
@property NSUInteger onPlanetID;
@property NSUInteger withNumberDenizens;

@end


@implementation CreateBuildingEvent

@synthesize byPlayer;
@synthesize atPosition;
@synthesize onPlanetID;
@synthesize withNumberDenizens;
@end

@interface SpawnPlanetEvent : NSObject

@property CGFloat orbitRadius;
@property CGFloat innerRadius;
@property CGFloat surfaceRadius;
@property NSUInteger player;
@property CGFloat centerX;
@property CGFloat centerY;
@property NSUInteger population;

@end


@implementation SpawnPlanetEvent

@synthesize orbitRadius;
@synthesize innerRadius;
@synthesize surfaceRadius;
@synthesize player;
@synthesize centerX;
@synthesize centerY;
@synthesize population;
@end

@interface SetCameraEvent : NSObject

@property CGFloat positionY;
@property CGFloat rotation;
@property CGFloat scale;
@property CGFloat positionX;

@end


@implementation SetCameraEvent

@synthesize positionY;
@synthesize rotation;
@synthesize scale;
@synthesize positionX;
@end


//[[[end]]]

@interface GenericClient ()

@end

@implementation GenericClient

- (void)initNetworkCommunication
{
    CFReadStreamRef readStream;
    CFWriteStreamRef writeStream;
    CFStreamCreatePairWithSocketToHost(NULL, (CFStringRef)@"127.0.0.1", 80, &readStream, &writeStream);
    _inputStream = (__bridge NSInputStream *)readStream;
    _outputStream = (__bridge NSOutputStream *)writeStream;
    
    [_inputStream setDelegate:self];
    [_outputStream setDelegate:self];
    
    [_inputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
    [_outputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
    
    [_inputStream open];
    [_outputStream open];
}

- (void)sendTestData:(NSString *)testData
{
    NSData *data = [[NSData alloc] initWithData:[testData dataUsingEncoding:NSASCIIStringEncoding]];
    [_outputStream write:[data bytes] maxLength:[data length]];
}

- (void)stream:(NSStream *)theStream handleEvent:(NSStreamEvent)streamEvent
{
	NSLog(@"stream event %i", streamEvent);
    
    switch(streamEvent)
    {
        case NSStreamEventOpenCompleted:
            NSLog(@"Stream opened");
            break;
            
        case NSStreamEventHasBytesAvailable:
            
            if(theStream == _inputStream)
            {
                uint8_t buffer[1024];
                int len;
                
                while ([_inputStream hasBytesAvailable])
                {
                    len = [_inputStream read:buffer maxLength:sizeof(buffer)];
                    
                    if(len > 0)
                    {
                        NSString *output = [[NSString alloc] initWithBytes:buffer length:len encoding:NSASCIIStringEncoding];
                        
                        if(nil != output)
                        {
                            NSLog(@"Server Said: %@", output);
                            
                            // first, strip out any new lines or carriage returns
                            output = [output stringByReplacingOccurrencesOfString:@"\n" withString:@""];
                            output = [output stringByReplacingOccurrencesOfString:@"\r" withString:@""];
                            
                            // first, process any messages in the stream that maybe have been mashed together by twisted into separate messages
                            NSArray *separatedOutput = [output componentsSeparatedByString:kMessageSeparator];
                            
                            // next, process each message individually
                            for(NSString * message in separatedOutput)
                            {
                                NSArray *components = [message componentsSeparatedByString:kParamSeperator];
                                
                                NSString * cmd = [components objectAtIndex:0];
                                
                                /*[[[cog
                                 
                                 from autogen import CodeGenerator
                                 cg = CodeGenerator("transport.idl")
                                 cog.outl(cg.generateTransportReceiver())
                                 ]]]*/
                                
                                if([cmd isEqualToString:@"sling"])
                                {
                                	FireCatapultEvent *event = [[FireCatapultEvent alloc] init];

                                	event.force = [[components objectAtIndex:1] floatValue];
                                	event.planetID = [[components objectAtIndex:2] intValue];
                                	event.slingAngle = [[components objectAtIndex:3] floatValue];
                                	event.buildingID = [[components objectAtIndex:4] intValue];
                                	
                                	[[NSNotificationCenter defaultCenter] postNotificationName:kFireCatapultNotification object:event];

                                }



                                if([cmd isEqualToString:@"building"])
                                {
                                	CreateBuildingEvent *event = [[CreateBuildingEvent alloc] init];

                                	event.byPlayer = [[components objectAtIndex:1] intValue];
                                	event.atPosition = [[components objectAtIndex:2] floatValue];
                                	event.onPlanetID = [[components objectAtIndex:3] intValue];
                                	event.withNumberDenizens = [[components objectAtIndex:4] intValue];
                                	
                                	[[NSNotificationCenter defaultCenter] postNotificationName:kCreateBuildingNotification object:event];

                                }



                                if([cmd isEqualToString:@"planet"])
                                {
                                	SpawnPlanetEvent *event = [[SpawnPlanetEvent alloc] init];

                                	event.orbitRadius = [[components objectAtIndex:1] floatValue];
                                	event.innerRadius = [[components objectAtIndex:2] floatValue];
                                	event.surfaceRadius = [[components objectAtIndex:3] floatValue];
                                	event.player = [[components objectAtIndex:4] intValue];
                                	event.centerX = [[components objectAtIndex:5] floatValue];
                                	event.centerY = [[components objectAtIndex:6] floatValue];
                                	event.population = [[components objectAtIndex:7] intValue];
                                	
                                	[[NSNotificationCenter defaultCenter] postNotificationName:kSpawnPlanetNotification object:event];

                                }



                                if([cmd isEqualToString:@"camera"])
                                {
                                	SetCameraEvent *event = [[SetCameraEvent alloc] init];

                                	event.positionY = [[components objectAtIndex:1] floatValue];
                                	event.rotation = [[components objectAtIndex:2] floatValue];
                                	event.scale = [[components objectAtIndex:3] floatValue];
                                	event.positionX = [[components objectAtIndex:4] floatValue];
                                	
                                	[[NSNotificationCenter defaultCenter] postNotificationName:kSetCameraNotification object:event];

                                }


                                //[[[end]]]
                            }
                        }
                    }
                }
                
            }
            break;
            
        case NSStreamEventErrorOccurred:
            NSLog(@"Can not connect to the host!");
            break;
            
        case NSStreamEventEndEncountered:
            [theStream close];
            [theStream removeFromRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
            break;
            
        default:
            NSLog(@"unknown event");
    }
}

- (void)messageReceived:(NSString *)message
{
    NSString * cleanString = [[message stringByReplacingOccurrencesOfString:@"\n" withString:@" "] stringByReplacingOccurrencesOfString:@"\r" withString:@" "];
    [_messages addObject:cleanString];
    [[NSNotificationCenter defaultCenter] postNotificationName:@"MessageReceived" object:_messages];
}

- (id)init
{
    self = [super init];
    
    if (self)
    {
        [self initNetworkCommunication];
        //[self sendTestData:@"iam|iphone"];
        _messages = [[NSMutableArray alloc] init];
    }
    
    return self;
}

@end
