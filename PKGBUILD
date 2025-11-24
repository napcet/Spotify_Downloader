# Maintainer: Mokshit Bindal <your-email@example.com>

pkgname=spotify-downloader
pkgver=1.0.2
pkgrel=2
pkgdesc="Download Spotify playlists, albums, and tracks in FLAC/MP3 format from free sources with beautiful terminal UI"
arch=('any')
url="https://github.com/MokshitBindal/Spotify_Downloader"
license=('MIT')
depends=(
    'python'
    'ffmpeg'
    'yt-dlp'
    'python-click'
    'python-requests'
    'python-yaml'
    'python-tqdm'
    'python-mutagen'
)
makedepends=('python-setuptools' 'python-build' 'python-installer' 'python-wheel' 'python-pip')
optdepends=()
source=("${pkgname}-${pkgver}.tar.gz::https://github.com/MokshitBindal/Spotify_Downloader/archive/v${pkgver}.tar.gz")
sha256sums=('bbbbf9633a607543e45494af2469495895a262925bda2f31150a2f3028d6c8df')

build() {
    cd "${srcdir}/Spotify_Downloader-${pkgver}"
    python -m build --wheel --no-isolation
}

package() {
    cd "${srcdir}/Spotify_Downloader-${pkgver}"
    
    # Install the wheel
    python -m installer --destdir="$pkgdir" dist/*.whl
    
    # Install spotipy and pydub to package site-packages (not available in Arch repos)
    local site_packages="$pkgdir/usr/lib/python3.13/site-packages"
    pip install --no-deps --target="$site_packages" spotipy>=2.24.0 pydub>=0.25.1
    
    # Install documentation
    install -Dm644 README.md "${pkgdir}/usr/share/doc/${pkgname}/README.md"
    
    # Install license
    install -Dm644 LICENSE "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
}
