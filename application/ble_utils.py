import asyncio
from bleak import BleakScanner, BLEDevice, AdvertisementData

# BAAB2 Beaconの設定
TARGET_UUID = "12300100-39fa-4005-860c-09362f6169da"
TARGET_MAJOR = 1
TARGET_MINOR = 22
TARGET_NAME = "ProxBeacon"

async def scan_beacons():
    devices = []

    async def detection_callback(device: BLEDevice, advertisement_data: AdvertisementData):
        try:
            uuid = advertisement_data.service_uuids[0] if advertisement_data.service_uuids else None
            name = device.name

            # MajorとMinorの解析
            if advertisement_data.manufacturer_data:  # メーカー情報がある場合
                manufacturer_data = advertisement_data.manufacturer_data
                if name == TARGET_NAME:
                    print(manufacturer_data)
                for key in manufacturer_data.keys():
                    data = manufacturer_data[key]
                    # MajorとMinorを取得するための解析を行います
                    if len(data) >= 6:  # 6バイト以上のデータがある場合
                        major = int.from_bytes(data[2:4], 'big')  # 2バイト目から4バイト目
                        minor = int.from_bytes(data[3:6], 'big')  # 4バイト目から6バイト目
                        ade_uuid = int.from_bytes(data[:], 'big')

                        if name == TARGET_NAME:
                            devices.append({
                                'name': name,
                                'is_connected': True,
                                'ade_uuid': ade_uuid,  # UUIDをここに格納
                                'uuid': uuid,
                                'major': major,
                                'minor': minor,
                            })
                            print(f"Device found: {name} ade_uuid: {ade_uuid} - Major: {major}, Minor: {minor}")
                            return  # デバイスが見つかったら早期に戻る

        except Exception as e:
            print(f"Error processing device: {e}")

    async with BleakScanner(detection_callback=detection_callback) as scanner:
        await asyncio.sleep(2)  # 2秒間スキャンを実行

    return devices


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    devices = loop.run_until_complete(scan_beacons())
    print(devices)
