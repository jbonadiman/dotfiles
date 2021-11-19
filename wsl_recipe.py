from dotfile import Dpkg
from dotfile import Apt
from dotfile import Ubuntu
from dotfile import \
    abs_path, \
    create_folder, \
    make_link, \
    exists, \
    download_installer, \
    git_clone

import tempfile
import shutil
import requests

apt = Apt()
dpkg = Dpkg()

print('Installing essential packages...')
tmpdir = tempfile.mkdtemp(prefix='wsl_recipe')

# TODO: read from file
apt_pcks = (
    'httpie',
    'clang',
    'exa'
)

try:

    exa_repo = 'spvkgn/exa'
    if apt.is_repository_added(exa_repo):
        print('exa repository already added, skipping...')
    else:
        print('Adding exa repository to apt...')
        apt.add_repository(exa_repo)
        apt.update()

    if exists('bat'):
        print('bat already installed, skipping...')
    else:
        print('Installing bat...')
        bat_url = r'https://github.com/sharkdp/bat/releases/download/v0.18.3/bat_0.18.3_amd64.deb'
        bat_deb_path = os.path.join(tmpdir, 'bat_0.18.3_amd64.deb')
        
        download_installer(bat_url, bat_deb_path)
        print('Installing...')
        dpkg.install(bat_deb_path)

    print('Installing apt packages...')
    apt.install(' '.join(apt_pcks))

    if exists('rustup'):
        print('Rust already installed, skipping...')
    else: 
        rust_installer = os.path.join(tmpdir, 'rust_installer.sh')
        download_installer(r'https://sh.rustup.rs', rust_installer)
        print('Installing...')
        Ubuntu.execute_sh(rust_installer, '--', '-y')

    if exists('batman'):
        print('bat extra modules already installed, skipping...')
    else:
        print('Install bat extra modules...')
        bat_extras_dir = os.path.join(tmpdir, 'bat-extras')
        git_clone('https://github.com/eth-p/bat-extras', bat_extras_dir)
        print('Installing...')
        Ubuntu.execute_sh(os.path.join(bat_extras_dir, 'build.sh'), '--install')

    if exists('n'):
        print('n already installed, skipping...')
    else:
        print('Installing n...')
        n_installer = os.path.join(tmpdir, 'n_install')
        download_installer(r'https://git.io/n-install', n_installer) 
        print('Installing...')
        Ubuntu.execute_bash(n_installer, '-y')

    # TODO: Setup locale

    # TODO: Check if Vundle is installed

finally:
    shutil.rmtree(tmpdir)
