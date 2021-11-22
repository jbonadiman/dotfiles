from dotfile import Dpkg
from dotfile import Apt
from dotfile import Ubuntu
from dotfile import \
    abs_path, \
    create_folder, \
    make_link, \
    exists, \
    download_installer, \
    git_clone, \
    install

import os
import os.path
import tempfile
import shutil
import requests

apt = Apt()
dpkg = Dpkg()

print('Installing essential packages...')
tmpdir = tempfile.mkdtemp(prefix='wsl_recipe')

folders = (
    '~/sources',
    '~/.local/bin'
)

# TODO: read from file
apt_pcks = (
    'httpie',
    'clang',
    'exa',
    'make'
)

links = {
    '~/.vimrc': 'vimrc',
    '~/.zshrc': 'zshrc',
    '~/.zshenv': 'zshenv',
    '~/.docker_service.zsh': 'docker_service.zsh',
}

def install_bat_fn() -> None:
    bat_url = r'https://github.com/sharkdp/bat/releases/download/v0.18.3/bat_0.18.3_amd64.deb'
    bat_deb_path = os.path.join(tmpdir, 'bat_0.18.3_amd64.deb')
    download_installer(bat_url, bat_deb_path)
    dpkg.install_packages(bat_deb_path)

def install_rust_fn() -> None:
    rust_installer = os.path.join(tmpdir, 'rust_installer.sh')
    download_installer(r'https://sh.rustup.rs', rust_installer)
    Ubuntu.execute_sh(rust_installer, ['--', '-y'])

def install_bat_extras_fn() -> None:
    bat_extras_dir = os.path.join(tmpdir, 'bat-extras')
    git_clone('https://github.com/eth-p/bat-extras', bat_extras_dir)
    Ubuntu.execute_bash(os.path.join(bat_extras_dir, 'build.sh'), ['--install'], sudo=True)

def install_n_fn() -> None:
    n_installer = os.path.join(tmpdir, 'n_install')
    download_installer(r'https://git.io/n-install', n_installer)
    os.chmod(n_installer, 0o755)
    Ubuntu.execute_bash(n_installer, ['-y'])

try:
    list(map(create_folder, folders))

    for symlink, original in links.items():
        make_link(original, symlink)

    exa_repo = 'spvkgn/exa'
    if apt.is_repository_added(exa_repo):
        print('exa repository already added, skipping...')
    else:
        print('Adding exa repository to apt...')
        apt.add_repository(exa_repo)
        apt.update()

    print('Installing apt packages...')
    apt.install_packages(*apt_pcks)

    install('bat', install_bat_fn)
    install('rustup', install_rust_fn)
    install('batman', install_bat_extras_fn, alias='bat-extras')
    install('n', install_n_fn)

    # TODO: Setup locale

    # TODO: Check if Vundle is installed

finally:
    shutil.rmtree(tmpdir)
