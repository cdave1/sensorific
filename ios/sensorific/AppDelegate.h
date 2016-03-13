//
//  AppDelegate.h
//  sensorific
//
//  Created by David Petrie on 27/01/14.
//  Copyright (c) 2014 David Petrie. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "BluetoothDetector.h"

@interface AppDelegate : UIResponder <UIApplicationDelegate>
{
    BluetoothDetector *bluetoothDetector;
}

@property (strong, nonatomic) UIWindow *window;

@end
