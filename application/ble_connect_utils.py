import asyncio

from bleak import BleakClient

# デバイスのUUIDとCharacteristic UUID
TARGET_UUID = "12300200-39fa-4005-860c-09362f6169da"  # Maintenance ServiceのUUID
DEVICE_ID_CHAR_UUID = "12300201-39fa-4005-860c-09362f6169da"  # デバイスIDのCharacteristic UUID


async def get_device_id(address):
    print("Attempting to connect to the device...")

    for attempt in range(3):  # 最大3回接続を試みる
        try:
            with BleakClient(address)as client:
                if client.is_connected:
                    print('yes')
            async with BleakClient(address, timeout=10.0) as client:  # タイムアウトを10秒に延長
                # 接続が確立されているか確認
                if client.is_connected:
                    print(f"Successfully connected to the device on attempt {attempt + 1}")

                    # デバイスIDのCharacteristicを読み取る
                    device_id_data = await client.read_gatt_char(DEVICE_ID_CHAR_UUID)
                    device_id = device_id_data.hex()
                    print(f"Device ID: {device_id}")
                    return device_id  # 成功したらデバイスIDを返す
                else:
                    print(f"Connection attempt {attempt + 1} failed, retrying...")

        except Exception as e:
            print(f"Attempt {attempt + 1}: Failed to connect or read Device ID - {e}")

        # 次の試行前に遅延を挟む
        await asyncio.sleep(2)

    print("Unable to connect to the device after multiple attempts.")
    return None
