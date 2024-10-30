import asyncio
from bleak import BleakScanner, BLEDevice, AdvertisementData

# デバイス情報
TARGET_UUID = "12300100-39fa-4005-860c-09362f6169da"
TARGET_NAME = "ProxBeacon"


async def scan_beacons():
    devices = []

    async def detection_callback(device: BLEDevice, advertisement_data: AdvertisementData):
        try:
            # デバイス情報を取得
            uuid = advertisement_data.service_uuids[0] if advertisement_data.service_uuids else None
            name = device.name
            manufacturer_data = advertisement_data.manufacturer_data

            # 条件に合うデバイスを見つけた場合
            if name == TARGET_NAME and uuid == TARGET_UUID:
                print(f"Device found: {device} with advertisement_data: {advertisement_data}")

                # メーカー特有のデータを抽出し、majorとminorを解読
                #manufacturer_bytes = list(manufacturer_data.values())[0] if manufacturer_data else None #個々の行がとってこれているのか次回検証
                #if manufacturer_bytes and len(manufacturer_bytes) >= 25:
                    # バイトデータの構造を確認し、majorとminorを抽出
                    #major = int.from_bytes(manufacturer_bytes[18:20], 'big')
                    #minor = int.from_bytes(manufacturer_bytes[20:22], 'big')
                    #print(f"major: {major}, minor: {minor}")

                    # デバイス情報をリストに追加
            devices.append({
                'name': name,
                'is_connected': True,
                'uuid': uuid,
                #'major': major,
                #'minor': minor,
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
