pkgname=logi-battery-uhid-git
pkgver=1.0.0
pkgrel=1
pkgdesc="A proxy daemon that exposes Logitech HID++ batteries as native Linux power_supply devices via uhid"
arch=('any')
url="https://github.com/grigorii-horos/logi_uhid_battery"
license=('MIT')
depends=('python')
source=()
md5sums=()

package() {
    cd "$srcdir/.."
    
    # Install Python scripts
    install -Dm755 logi_battery_uhid.py "$pkgdir/usr/lib/logi-battery-uhid/logi_battery_uhid.py"
    install -Dm644 hidpp.py "$pkgdir/usr/lib/logi-battery-uhid/hidpp.py"
    
    # Install systemd user service
    install -Dm644 logi-battery-uhid.service "$pkgdir/usr/lib/systemd/user/logi-battery-uhid.service"
    
    # Install udev rule
    install -Dm644 99-uhid.rules "$pkgdir/usr/lib/udev/rules.d/99-uhid.rules"
}
