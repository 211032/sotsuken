from bleak import BleakScanner

async def scan_beacons():
    devices = await BleakScanner.discover()
    return devices
