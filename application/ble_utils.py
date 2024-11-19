import asyncio
from bleak import BleakScanner, BLEDevice, AdvertisementData
import binascii
from .classroom_checker import get_classroom_name

# デバイス情報
TARGET_NAME = "ProxBeacon"
TARGET_UUID = "12300200-39fa-4005-860c-09362f6169da"  # Maintenance ServiceのUUID
DEVICE_ID_CHAR_UUID = "12300201-39fa-4005-860c-09362f6169da"  # デバイスIDのCharacteristic UUID

async def scan_beacons():
    devices = []
    # 周辺デバイスのスキャン
    # scanned_devices = await BleakScanner.discover()
    # for device in scanned_devices:
    #     # 名前とアドレスを取得
    #     devices.append({
    #         "name": device.name or "Unknown",
    #         "address": device.address,
    #         "rssi": device.rssi
    #     })
    # return devices

    async def detection_callback(device: BLEDevice, advertisement_data: AdvertisementData):
        try:
            name = device.name
            address = device.address
            manufacturer_data = advertisement_data.manufacturer_data

            # 条件に合うデバイスを見つけた場合
            if name == TARGET_NAME and manufacturer_data:

                # メーカー特有のデータを抽出し、UUID、major、minorを解読
                manufacturer_bytes = list(manufacturer_data.values())[0] if manufacturer_data else None
                if manufacturer_bytes and len(manufacturer_bytes) >= 22:
                    # UUIDを取得
                    uuid = binascii.hexlify(manufacturer_bytes[2:18]).decode("utf-8")
                    formatted_uuid = f"{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}"
                    print(f"UUID: {formatted_uuid}")

                    # Major と Minor を取得
                    major = int.from_bytes(manufacturer_bytes[18:20], 'big')
                    minor = int.from_bytes(manufacturer_bytes[20:22], 'big')
                    classname = await get_classroom_name(minor)
                    print(f"major: {major}, minor: {minor}")

                    # デバイス情報をリストに追加
                    devices.append({
                        'name': name,
                        'address': address,
                        'is_connected': True,
                        'uuid': formatted_uuid,
                        'major': major,
                        'minor': minor,
                        'classname': classname,
                    })



        except Exception as e:
            print(f"Error processing device: {e}")

    # スキャン実行
    async with BleakScanner(detection_callback=detection_callback) as scanner:
        await asyncio.sleep(5)  # 5秒間スキャン

    return devices

# メイン関数
async def main():
    found_devices = await scan_beacons()
    for device in found_devices:
        print(f"Found device: {device}")

# 実行
asyncio.run(main())


