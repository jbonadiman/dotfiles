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
    download_installer, \
    install, \
    execute_cmd

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
scoop_pcks = (
    'aria2',
    'advancedrenamer',
    'authy',
    'treesize-free',
    'vlc',
    'bitwarden'
)

folders = (
    '~/sources'
)

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
    download_installer(r'get.scoop.sh', scoop_installer)
    Windows.execute_ps1(scoop_installer)
    if Scoop.SCOOP_VARNAME not in os.environ:
        print(f"Adding '{Scoop.SCOOP_VARNAME}' to environment variables...")
        os.environ[Scoop.SCOOP_VARNAME] = abs_path('~/scoop')
    print('Installing scoop essential packages...')
    scoop.install_packages('7zip', 'git', 'innounp', 'dark', 'wixtoolset', 'lessmsi')


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

        install('scoop', install_scoop_fn)
        install('shovel', install_shovel_fn)

        scoop.add_bucket('extras')
        scoop.install_packages(*scoop_pcks)


        sync_firefox_cookies()
    finally:
        shutil.rmtree(tmpdir)
