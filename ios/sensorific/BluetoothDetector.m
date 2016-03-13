#import "BluetoothDetector.h"

@implementation BluetoothDetector : NSObject

- (id) init
{
    myCentralManager = [[CBCentralManager alloc] initWithDelegate:self queue:nil options:nil];
    return self;
}

- (void) detectBluetoothDevices
{
    if (myCentralManager.state == CBCentralManagerStatePoweredOn)
    {
        [myCentralManager scanForPeripheralsWithServices:nil options:nil];
    }
}


- (void)centralManagerDidUpdateState:(CBCentralManager *)central
{
    if (central.state == CBCentralManagerStatePoweredOn)
    {
        [self detectBluetoothDevices];
    }
}


- (void)centralManager:(CBCentralManager *)central didDiscoverPeripheral:(CBPeripheral *)peripheral advertisementData:(NSDictionary *)advertisementData RSSI:(NSNumber *)RSSI
{
    NSLog(@"Discovered %@ %@", peripheral.name, peripheral.description);
    
    [self detectBluetoothDevices];
}

@end
