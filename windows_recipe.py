#!/usr/bin/env python3

import tempfile
import os.path

from dotfile import abs_path

from dotfile import Msix, Scoop, Winget, Windows

windows = Windows()
scoop = Scoop()
msix = Msix()
winget = Winget()

keyboard_layouts = [
    '00020409'  # en-US International
]

TERMINAL_SETTINGS = abs_path(
    os.path.join(
        windows.PACKAGES_FOLDER,
        'Microsoft.WindowsTerminal_8wekyb3d8bbwe',
        'LocalState',
        'settings.json'
    )
)

WINGET_SETTINGS = abs_path(
    os.path.join(
        windows.PACKAGES_FOLDER,
        'Microsoft.DesktopAppInstaller_8wekyb3d8bbwe',
        'LocalState',
        'settings.json'
    )
)

# TODO: read from file
scoop_apps = [
    # essential
    'aria2',
    'advancedrenamer',
    'authy',
    'treesize-free',
    'vlc',
    'bitwarden',
    # dev
    'gitkraken',
    'jetbrains-toolbox',
    # personal
    'ccleaner',
    'discord',
    'gimp',
    'inkscape',
    'qbittorrent'
]

winget_ids = [
    # essential
    'Mozilla.Firefox',

    # personal
    '9WZDNCRFJ3TJ',  # Netflix
    # 'Amazon.Games',
    'Amazon.Kindle',
    'EpicGames.EpicGamesLauncher',
    'GOG.Galaxy',
    'Valve.Steam',
    'Telegram.TelegramDesktop',
    'Ubisoft.Connect',
    'WhatsApp.WhatsApp',

    # dev
    'dbeaver.dbeaver',

    # TODO: Should only be installed if WSL is present
    # 'Canonical.Ubuntu.2004'

]

folders = [
    '~/sources'
]

links = {
    TERMINAL_SETTINGS: 'terminal.settings.json',
    WINGET_SETTINGS: 'winget.settings.json',
    '~/Documents/PowerShell/Microsoft.PowerShell_profile.ps1': 'PowerShell_Profile.ps1'
}


def install_scoop_fn() -> None:
    from dotfile import download_file
    from dotfile import abs_path
    from os import environ

    scoop_installer = os.path.join(tmpdir, 'install.ps1')
    download_file(r'get.scoop.sh', scoop_installer)
    windows.execute_ps1(scoop_installer)
    if Scoop.SCOOP_VAR not in environ:
        print(f"Adding '{Scoop.SCOOP_VAR}' to environment variables...")
        environ[Scoop.SCOOP_VAR] = abs_path('~/scoop')
    print('Installing scoop essential packages...')
    scoop.install(['7zip', 'git', 'innounp', 'dark', 'wixtoolset', 'lessmsi'])


def download_and_install_font(url: str) -> None:
    from urllib.parse import unquote

    font_name = unquote(os.path.basename(url))

    if os.path.exists(os.path.join(Windows.FONTS_FOLDER, font_name)):
        print(f"Font '{font_name}' already installed, skipping...")
        return

    from windows_font_installer import install_font
    from dotfile import download_file

    print(f"Downloading and installing font '{font_name}'...")
    font_path = os.path.join(tmpdir, font_name)
    download_file(url, font_path)

    print('Installing...')
    install_font(font_path)


def install_shovel_fn() -> None:
    from glob import glob
    from shutil import copy2

    scoop.change_repo('https://github.com/Ash258/Scoop-Core')
    scoop.update()
    scoop.add_bucket('Base')
    p = os.path
    # copy everything that is /scoop.ext to the same folder as /shovel.ext
    for file_path in glob(p.join(os.environ['SCOOP'], 'shims', 'scoop.*')):
        new_filename = p.join(p.dirname(file_path), f'shovel{p.splitext(file_path)[1]}')
        copy2(file_path, new_filename)


def install_winget_fn() -> None:
    from dotfile import download_file

    download_url = 'https://github.com/microsoft/winget-cli/releases/download/v1.1.12653/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle'
    winget_setup = os.path.join(tmpdir, os.path.basename(download_url))

    download_file(download_url, winget_setup)

    msix.install([winget_setup])


def install_wsl_fn() -> None:
    from dotfile import execute_cmd

    print('Installing WSL...')
    execute_cmd('wsl --install')
    print('Done!')


if __name__ == '__main__':
    from dotfile import create_folder
    from dotfile import make_link
    from shutil import rmtree

    print('Installing Windows packages...')
    tmpdir = tempfile.mkdtemp(prefix='windows_recipe')

    try:
        list(map(create_folder, folders))

        for symlink, original in links.items():
            make_link(original, symlink)

        windows.set_keyboard_layouts(keyboard_layouts)

        # TODO: how to check if wsl is installed?
        # windows.install('wsl', install_wsl_fn)

        if 'WSLENV' not in os.environ or 'USERPROFILE' not in os.environ['WSLENV']:
            print("Adding Windows profile in WSL environment variables")
            os.environ['WSLENV'] = 'USERPROFILE/p'
        else:
            print("Windows profile already added to WSL environment variables")

        windows.install('scoop', install_scoop_fn)
        windows.install('shovel', install_shovel_fn)

        scoop.add_bucket('extras')
        scoop.install(scoop_apps)

        windows.install('winget', install_winget_fn)

        winget.install(winget_ids)

        download_and_install_font(
            'https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/CascadiaCode/Regular/complete/Caskaydia%20Cove%20Regular%20Nerd%20Font%20Complete%20Windows%20Compatible.otf'
        )

        # sync_firefox_cookies()
    finally:
        rmtree(tmpdir)
