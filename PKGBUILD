# Maintainer: Mokshit Bindal <your-email@example.com>

pkgname=spotify-downloader
pkgver=1.0.0
pkgrel=1
pkgdesc="Download Spotify playlists, albums, and tracks in FLAC/MP3 format from free sources"
arch=('x86_64')
url="https://github.com/MokshitBindal/Spotify_Downloader"
license=('MIT')
depends=('python' 'python-pip' 'ffmpeg')
makedepends=('python-setuptools' 'python-build' 'python-installer' 'python-wheel')
optdepends=(
    'yt-dlp: YouTube download support'
    'python-spotipy: Spotify API access'
)
source=("${pkgname}-${pkgver}.tar.gz::https://github.com/MokshitBindal/Spotify_Downloader/archive/v${pkgver}.tar.gz")
sha256sums=('0a821a4b2da3c6fd6e7a903bf5fd007ff08069e501bf6a0927263b89905f6ec2')

build() {
    cd "${srcdir}/Spotify_Downloader-${pkgver}"
    python -m build --wheel --no-isolation
}

package() {
    cd "${srcdir}/Spotify_Downloader-${pkgver}"
    python -m installer --destdir="$pkgdir" dist/*.whl
    
    # Install documentation
    install -Dm644 README.md "${pkgdir}/usr/share/doc/${pkgname}/README.md"
    
    # Install license
    install -Dm644 LICENSE "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
}
