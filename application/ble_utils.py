from bleak import BleakScanner, BleakClient

# ターゲットのUUID, Major, Minor
TARGET_UUID = "E02CC25E-0049-4185-832C-3A65DB755D01"
TARGET_MAJOR = 1  # 実際のMajor値に置き換える
TARGET_MINOR = 22  # 実際のMinor値に置き換える


async def scan_beacons():
    devices = await BleakScanner.discover()
    target_device = None

    for device in devices:
        # 広告データからiBeacon情報を取得
        if "manufacturer_data" in device.metadata:
            manufacturer_data = device.metadata["manufacturer_data"]
            for key, value in manufacturer_data.items():
                # iBeaconデータの確認 (keyは会社ID、valueはiBeaconの詳細データ)
                if len(value) >= 23:  # iBeaconフォーマットの長さを確認
                    uuid = value[2:18].hex()  # UUIDの抽出
                    major = int.from_bytes(value[18:20], byteorder='big')  # Majorの抽出
                    minor = int.from_bytes(value[20:22], byteorder='big')  # Minorの抽出

                    if uuid == TARGET_UUID and major == TARGET_MAJOR and minor == TARGET_MINOR:
                        target_device = device
                        break

    # ターゲットデバイスに接続
    if target_device:
        device_info = {
            'name': target_device.name or 'Unknown',
            'address': target_device.address,
            'is_connected': False
        }

        try:
            async with BleakClient(target_device) as client:
                if client.is_connected:
                    device_info['is_connected'] = True
                    device_info['uuid'] = TARGET_UUID
        except Exception as e:
            print(f"接続失敗: {e}")

        return [device_info]
    else:
        return []
