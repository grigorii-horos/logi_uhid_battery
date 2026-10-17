pkgname=logi-battery-uhid-git
pkgver=1.0.0
pkgrel=1
pkgdesc="A proxy daemon that exposes Logitech HID++ batteries as native Linux power_supply devices via uhid"
arch=('any')
url="https://github.com/grigorii-horos/logi_uhid_battery"
license=('MIT')
depends=('python')
makedepends=('git')
provides=('logi-battery-uhid')
conflicts=('logi-battery-uhid')
# from git, not from the files next to this PKGBUILD: a clean chroot (server-home's udom builder) only sees source=()
source=("$pkgname::git+https://github.com/grigorii-horos/logi_uhid_battery.git")
sha256sums=('SKIP')

pkgver() {
    cd "$pkgname"
    printf "1.0.0.r%s.g%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

package() {
    cd "$srcdir/$pkgname"
    
    # Install Python scripts
    install -Dm755 logi_battery_uhid.py "$pkgdir/usr/lib/logi-battery-uhid/logi_battery_uhid.py"
    install -Dm644 hidpp.py "$pkgdir/usr/lib/logi-battery-uhid/hidpp.py"
    
    # Install systemd user service
    install -Dm644 logi-battery-uhid.service "$pkgdir/usr/lib/systemd/user/logi-battery-uhid.service"
    
    # Install udev rule
    install -Dm644 99-uhid.rules "$pkgdir/usr/lib/udev/rules.d/99-uhid.rules"
}
