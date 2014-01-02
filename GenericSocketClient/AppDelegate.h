//
//  AppDelegate.h
//  GenericSocketClient
//
//  Created by Liam on 02/01/2014.
//  Copyright (c) 2014 Liam. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "GenericClient.h"

@interface AppDelegate : UIResponder <UIApplicationDelegate>

@property (strong, nonatomic) UIWindow *window;
@property (strong, nonatomic) GenericClient *client;

@end
