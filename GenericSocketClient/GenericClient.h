//
//  GenericClient.h
//
//  Created by Liam on 2/1/2014.
//  Copyright (c) 2013 Liam Conroy (Vitei). All rights reserved.
//

#import <Foundation/Foundation.h>

@interface GenericClient : NSObject <NSStreamDelegate>

@property (nonatomic, strong) NSMutableArray * messages;

@property NSInputStream  *inputStream;
@property NSOutputStream *outputStream;

- (void)sendTestData:(NSString *)testData;

@end

/*[[[cog
 from autogen import CodeGenerator
 cg = CodeGenerator("transport.idl")
 cog.outl(cg.generateMessageSeparators())
 cog.outl(cg.generateNotificationDefines())
 ]]]*/

#define kMessageSeparator @"###"
#define kParamSeperator @"|"
		
#define kFireCatapultNotification @"FireCatapult"
#define kCreateBuildingNotification @"CreateBuilding"
#define kSpawnPlanetNotification @"SpawnPlanet"
#define kSetCameraNotification @"SetCamera"

//[[[end]]]

