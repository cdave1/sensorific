#import <UIKit/UIKit.h>
#import <CoreBluetooth/CoreBluetooth.h>

@interface BluetoothDetector : NSObject <CBCentralManagerDelegate>
{
    CBCentralManager *myCentralManager;
}

- (void) detectBluetoothDevices;

- (void)centralManagerDidUpdateState:(CBCentralManager *)central;

- (void)centralManager:(CBCentralManager *)central didDiscoverPeripheral:(CBPeripheral *)peripheral advertisementData:(NSDictionary *)advertisementData RSSI:(NSNumber *)RSSI;

@end
