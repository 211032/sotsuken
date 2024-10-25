import asyncio
from bleak import BleakScanner, BleakClient, BLEDevice, AdvertisementData

# BAAB2 Beaconの設定
TARGET_UUID = "12300100-39fa-4005-860c-09362f6169da"
TARGET_NAME = "ProxBeacon"

# MajorとMinorのCharacteristic UUID
MAJOR_UUID = "12300102-39fa-4005-860c-09362f6169da"
MINOR_UUID = "12300103-39fa-4005-860c-09362f6169da"


async def scan_beacons():
    devices = []

    async def detection_callback(device: BLEDevice, advertisement_data: AdvertisementData):
        try:
            uuid = advertisement_data.service_uuids[0] if advertisement_data.service_uuids else None
            name = device.name

            # 条件に合うデバイスを見つけたら、Characteristicを読み取る
            if name == TARGET_NAME and uuid == TARGET_UUID:
                print(f"Device found: {name} with UUID: {uuid}. Attempting to connect...")
                for attempt in range(3):  # 最大3回接続を試行
                    try:
                        async with BleakClient(device) as client:
                            await client.connect(timeout=5.0)
                            if client.is_connected:
                                # Majorの読み取り
                                major_data = await client.read_gatt_char(MAJOR_UUID)
                                major = int.from_bytes(major_data, byteorder="big")

                                # Minorの読み取り
                                minor_data = await client.read_gatt_char(MINOR_UUID)
                                minor = int.from_bytes(minor_data, byteorder="big")

                                devices.append({
                                    'name': name,
                                    'is_connected': True,
                                    'uuid': uuid,
                                    'major': major,
                                    'minor': minor,
                                })
                                print(f"Device {name} connected - Major: {major}, Minor: {minor}")
                                return  # 成功したらループを抜ける

                            else:
                                print(f"Attempt {attempt + 1}: Connection failed, retrying...")

                    except Exception as e:
                        print(f"Attempt {attempt + 1}: Error during GATT operation: {e}")

                    await asyncio.sleep(1)  # 再試行の前に1秒待つ

        except Exception as e:
            print(f"Error processing device: {e}")

    async with BleakScanner(detection_callback=detection_callback) as scanner:
        await asyncio.sleep(5)  # 5秒間スキャンを実行

    return devices


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    devices = loop.run_until_complete(scan_beacons())
    print(devices)
