# Logi UHID Battery Proxy

A lightweight, zero-kernel-patch userspace daemon for Linux that exposes the battery level of Logitech HID++ 2.0 devices (like the MX Keys Mini, MX Master, etc.) as native `power_supply` devices.

This allows the battery charge percentage and charging status to seamlessly appear in your desktop environment's native power widgets (e.g., KDE Plasma, GNOME) and `UPower`, without requiring complex kernel driver modifications.

## How it works

The Linux kernel (`hid-input.c`) natively creates battery indicators for HID devices that strictly follow the generic USB HID Battery System standard (`Usage Page 0x85`). However, many Logitech devices report their battery over a proprietary `HID++` protocol instead.

This daemon uses the `/dev/uhid` subsystem to dynamically inject a perfectly crafted virtual HID Report Descriptor into the kernel. It then polls the physical device using HID++ and proxies the battery level into the virtual device. The Linux kernel parses the virtual descriptor and automatically creates a `/sys/class/power_supply/` node, allowing `UPower` to pick it up immediately.

## Installation (Arch Linux / CachyOS)

A `PKGBUILD` is included for easy installation on Arch-based distributions.

```bash
git clone https://github.com/grigorii-horos/logi_uhid_battery.git
cd logi_uhid_battery
makepkg -si
```

## Running the Daemon

The package installs a systemd user service. To start and enable it on boot:

```bash
systemctl --user enable --now logi-battery-uhid.service
```

No root access is required for the daemon! The package installs a `udev` rule (`99-uhid.rules`) that allows members of the `input` group to write to `/dev/uhid`.

## Compatibility
Works with any Logitech Logi Bolt or Unifying receiver device that supports the HID++ 2.0 Unified Battery or Battery Status features (e.g., MX Keys Mini, MX Anywhere 3).

## License
MIT
