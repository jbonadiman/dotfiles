#!/usr/bin/env python3

import os.path

import requests
import shutil
import tempfile
import glob

import firefox
from dotfile import Scoop
from dotfile import Windows
from dotfile import abs_path, \
    create_folder, \
    make_link, \
    download_file

from windows_font_installer import install_font

windows = Windows()
scoop = Scoop()
print('Installing Windows packages...')
tmpdir = tempfile.mkdtemp(prefix='windows_recipe')

TERMINAL_PATH = abs_path(
    os.path.join(
        '%LOCALAPPDATA%',
        'Packages',
        'Microsoft.WindowsTerminal_8wekyb3d8bbwe',
        'LocalState',
        'settings.json')
)

# TODO: read from file
scoop_pcks = [
    'aria2',
    'advancedrenamer',
    'authy',
    'treesize-free',
    'vlc',
    'bitwarden'
]

folders = [
    '~/sources'
]

links = {
    TERMINAL_PATH: 'terminal.settings.json',
    '~/Documents/PowerShell/Microsoft.PowerShell_profile.ps1': 'PowerShell_Profile.ps1'
}


def sync_firefox_cookies() -> None:
    print('Syncing Firefox cookies exceptions...')

    print('Loading hosts...')
    resp = requests.get('https://pastebin.com/raw/FjKvjMzz')
    hosts = resp.text.split()

    print('Syncing...')
    firefox.sync_cookies(*hosts)
    print('Done!')


def install_scoop_fn() -> None:
    scoop_installer = os.path.join(tmpdir, 'install.ps1')
    download_file(r'get.scoop.sh', scoop_installer)
    Windows.execute_ps1(scoop_installer)
    if Scoop.SCOOP_VAR not in os.environ:
        print(f"Adding '{Scoop.SCOOP_VAR}' to environment variables...")
        os.environ[Scoop.SCOOP_VAR] = abs_path('~/scoop')
    print('Installing scoop essential packages...')
    scoop.install('7zip', 'git', 'innounp', 'dark', 'wixtoolset', 'lessmsi')


def download_and_install_font(url: str) -> None:
    from urllib.parse import unquote

    font_name = unquote(os.path.basename(url))

    if os.path.exists(os.path.join(Windows.FONTS_FOLDER, font_name)):
        print(f"Font '{font_name}' already installed, skipping...")
        return

    print(f"Downloading and installing font '{font_name}'...")
    font_path = os.path.join(tmpdir, font_name)
    download_file(url, font_path)

    print('Installing...')
    install_font(font_path)


def install_shovel_fn() -> None:
    scoop.change_repo('https://github.com/Ash258/Scoop-Core')
    scoop.update()
    scoop.add_bucket('Base')
    p = os.path
    # copy everything that is /scoop.ext to the same folder as /shovel.ext
    for file_path in glob.glob(p.join(os.environ['SCOOP'], 'shims', 'scoop.*')):
        new_filename = p.join(p.dirname(file_path), f'shovel{p.splitext(file_path)[1]}')
        shutil.copy2(file_path, new_filename)


if __name__ == '__main__':
    try:
        list(map(create_folder, folders))

        for symlink, original in links.items():
            make_link(original, symlink)

        windows.install('scoop', install_scoop_fn)
        windows.install('shovel', install_shovel_fn)

        scoop.add_bucket('extras')
        scoop.install(scoop_pcks)

        download_and_install_font(
            'https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/CascadiaCode/Regular/complete/Caskaydia%20Cove%20Regular%20Nerd%20Font%20Complete%20Windows%20Compatible.otf'
        )

        sync_firefox_cookies()
    finally:
        shutil.rmtree(tmpdir)
