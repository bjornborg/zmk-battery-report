#!/usr/bin/python3

from dbus_next.aio import MessageBus
from dbus_next.constants import BusType
import asyncio
import sys

BLUEZ = "org.bluez"
# replace hci0 with your bluetooth adapter name and FF_FF_FF_FF_FF_FF with your keyboard address
BLUEZ_PATH = "/org/bluez/hci0/"
GATT_SERVICE = 'org.bluez.GattService1'
GATT_CHARACTERISCITC = 'org.bluez.GattCharacteristic1'
GATT_CHARACTERISCITC_DESCR = 'org.bluez.GattDescriptor1'
BATTERY_UUID = "0000180f-0000-1000-8000-00805f9b34fb"
BATTERY_LEVEL_UUID = "00002a19-0000-1000-8000-00805f9b34fb"
BATTERY_USER_DESC = "00002901-0000-1000-8000-00805f9b34fb"

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def main():
    args = sys.argv[1:]
    btAdapterAddr = args[0].replace(':', '_')
    BLUEZ_DEVICE_PATH = BLUEZ_PATH+"dev_{}".format(btAdapterAddr)

    # print(BLUEZ_DEVICE_PATH)

    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    # the introspection xml would normally be included in your project, but
    # this is convenient for development
    introspection = await bus.introspect(BLUEZ, BLUEZ_DEVICE_PATH)

    device = bus.get_proxy_object(BLUEZ, BLUEZ_DEVICE_PATH, introspection)

    for svc in device.child_paths:
        intp = await bus.introspect(BLUEZ, svc)
        proxy = bus.get_proxy_object(BLUEZ, svc, intp)
        intf = proxy.get_interface(GATT_SERVICE)
        if BATTERY_UUID == await intf.get_uuid():
            for char in proxy.child_paths:
                intp = await bus.introspect(BLUEZ, char)
                proxy = bus.get_proxy_object(BLUEZ, char, intp)
                intf = proxy.get_interface(GATT_CHARACTERISCITC)
                level = int.from_bytes(await intf.call_read_value({}), byteorder='big')
                if BATTERY_LEVEL_UUID == await intf.get_uuid():
                    props = proxy.get_interface(
                        'org.freedesktop.DBus.Properties')
                    for desc in proxy.child_paths:
                        intp = await bus.introspect(BLUEZ, desc)
                        proxy = bus.get_proxy_object(BLUEZ, desc, intp)
                        intf = proxy.get_interface(GATT_CHARACTERISCITC_DESCR)
                        name = "Central"
                        if BATTERY_USER_DESC == await intf.get_uuid():
                            name = bytearray(await intf.call_read_value({})).decode()
                    print(name + ": ", str(level))

loop.run_until_complete(main())
