import sys
import os
import time
import select
import ctypes

from hidpp import get_batteries

# UHID API Structs
UHID_CREATE2 = 11
UHID_DESTROY = 1
UHID_INPUT2 = 12

class UHIDCreate2Req(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_uint8 * 128),
        ("phys", ctypes.c_uint8 * 64),
        ("uniq", ctypes.c_uint8 * 64),
        ("rd_size", ctypes.c_uint16),
        ("bus", ctypes.c_uint16),
        ("vendor", ctypes.c_uint32),
        ("product", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("country", ctypes.c_uint32),
        ("rd_data", ctypes.c_uint8 * 4096),
    ]

class UHIDInput2Req(ctypes.Structure):
    _fields_ = [
        ("size", ctypes.c_uint16),
        ("data", ctypes.c_uint8 * 4096),
    ]

class UHIDEventUnion(ctypes.Union):
    _fields_ = [
        ("create2", UHIDCreate2Req),
        ("input2", UHIDInput2Req),
        ("raw", ctypes.c_uint8 * 4380),
    ]

class UHIDEvent(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_uint32),
        ("u", UHIDEventUnion),
    ]

# HID Report Descriptor for a Keyboard + Battery
HID_REPORT_DESCRIPTOR = bytes([
    0x05, 0x01,        # Usage Page (Generic Desktop Ctrls)
    0x09, 0x06,        # Usage (Keyboard)
    0xA1, 0x01,        # Collection (Application)
    
    # Dummy keyboard report
    0x05, 0x07,        #   Usage Page (Kbrd/Keypad)
    0x19, 0xE0,        #   Usage Minimum (0xE0)
    0x29, 0xE7,        #   Usage Maximum (0xE7)
    0x15, 0x00,        #   Logical Minimum (0)
    0x25, 0x01,        #   Logical Maximum (1)
    0x75, 0x01,        #   Report Size (1)
    0x95, 0x08,        #   Report Count (8)
    0x81, 0x02,        #   Input (Data,Var,Abs)
    0x95, 0x01,        #   Report Count (1)
    0x75, 0x08,        #   Report Size (8)
    0x81, 0x01,        #   Input (Const,Array,Abs)

    # Battery Report (Report ID 2)
    0x85, 0x02,        #   Report ID (2)
    
    0x05, 0x06,        #   Usage Page (Generic Device Controls)
    0x09, 0x20,        #   Usage (Battery Strength)
    0x15, 0x00,        #   Logical Minimum (0)
    0x25, 0x64,        #   Logical Maximum (100)
    0x75, 0x08,        #   Report Size (8)
    0x95, 0x01,        #   Report Count (1)
    0x81, 0x02,        #   Input (Data,Var,Abs)
    
    0x05, 0x85,        #   Usage Page (Battery System)
    0x09, 0x44,        #   Usage (Charging)
    0x15, 0x00,        #   Logical Minimum (0)
    0x25, 0x01,        #   Logical Maximum (1)
    0x75, 0x01,        #   Report Size (1)
    0x95, 0x01,        #   Report Count (1)
    0x81, 0x02,        #   Input (Data,Var,Abs)

    0x75, 0x07,        #   Report Size (7) padding
    0x95, 0x01,        #   Report Count (1)
    0x81, 0x03,        #   Input (Const,Var,Abs)
    
    0xC0               # End Collection
])

class VirtualBattery:
    def __init__(self, name, phys, uniq):
        self.fd = os.open('/dev/uhid', os.O_RDWR | os.O_NONBLOCK)
        
        ev = UHIDEvent()
        ev.type = UHID_CREATE2
        name_b = name.encode('utf-8')[:127]
        phys_b = phys.encode('utf-8')[:63]
        uniq_b = uniq.encode('utf-8')[:63]
        
        for i, b in enumerate(name_b): ev.u.create2.name[i] = b
        for i, b in enumerate(phys_b): ev.u.create2.phys[i] = b
        for i, b in enumerate(uniq_b): ev.u.create2.uniq[i] = b
        ev.u.create2.bus = 3 # BUS_USB
        ev.u.create2.vendor = 0x046D
        ev.u.create2.product = 0x0001
        ev.u.create2.version = 0x0100
        ev.u.create2.country = 0
        ev.u.create2.rd_size = len(HID_REPORT_DESCRIPTOR)
        ev.u.create2.rd_data[:len(HID_REPORT_DESCRIPTOR)] = HID_REPORT_DESCRIPTOR
        
        os.write(self.fd, bytes(ev))
        print(f"Created virtual battery for {name}")

    def update_level(self, percent, charge_state):
        ev = UHIDEvent()
        ev.type = UHID_INPUT2
        ev.u.input2.size = 3 # Report ID (1) + Percent (1) + Charging (1)
        ev.u.input2.data[0] = 2 # Report ID 2
        ev.u.input2.data[1] = int(percent)
        
        # In lnxlink, charge_state 1 or 2 usually means charging
        is_charging = 1 if charge_state in (1, 2) else 0
        ev.u.input2.data[2] = is_charging
        
        os.write(self.fd, bytes(ev))

    def close(self):
        ev = UHIDEvent()
        ev.type = UHID_DESTROY
        os.write(self.fd, bytes(ev))
        os.close(self.fd)

def main():
    virtual_devices = {}
    
    try:
        while True:
            batteries = get_batteries()
            for bat in batteries:
                uid = f"{bat['node']}_{bat['slot']}"
                
                if uid not in virtual_devices:
                    name = bat['name'] or f"Logitech Device {uid}"
                    virtual_devices[uid] = VirtualBattery(name, uid, uid)
                    time.sleep(1) # Give kernel time to init power_supply
                
                # Update the level
                if bat['percent'] is not None:
                    charge_state = bat.get('charge_state', 0)
                    virtual_devices[uid].update_level(bat['percent'], charge_state)
                    print(f"[{time.strftime('%H:%M:%S')}] Updated {bat['name']} to {bat['percent']}% (Charging: {charge_state})")
            
            # Poll every 60 seconds
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\nExiting and cleaning up virtual devices...")
        for dev in virtual_devices.values():
            dev.close()

if __name__ == '__main__':
    main()
