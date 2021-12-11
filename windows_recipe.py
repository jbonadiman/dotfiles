#!/usr/bin/env python3

import os.path
import tempfile

from dotfile import Msix, Scoop, Winget, Windows, App
from dotfile import abs_path
from dotfile import logger

windows = Windows()
scoop = Scoop()
msix = Msix()
winget = Winget()

WSL_DISTRO = 'Ubuntu-20.04'

KEYBOARD_LAYOUTS = [
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

winget_ids = [
    'da2x.EdgeDeflector',

    # personal
    # '9WZDNCRFJ3TJ',  # Netflix
    # 'Amazon.Games',
    'Amazon.Kindle',
    # 'EpicGames.EpicGamesLauncher',
    # 'GOG.Galaxy',
    # 'Valve.Steam',
    'Telegram.TelegramDesktop',
    # 'Ubisoft.Connect',
    'WhatsApp.WhatsApp',
    # 'StartIsBack.StartAllBack',
    # 'Stremio.Stremio',

    # dev
    # 'dbeaver.dbeaver',
]

folders = [
    '~/sources'
]


# BEGIN aliases
jn = os.path.join


def pt_cfg(cfg):
    return jn('PowerToys', cfg, f'{cfg}.settings.json')
# END aliases


links = {
    TERMINAL_SETTINGS: 'terminal.settings.json',
    WINGET_SETTINGS: 'winget.settings.json',
    '~/Documents/PowerShell/Microsoft.PowerShell_profile.ps1': 'PowerShell_Profile.ps1',
    '%APPDATA%/Rainmeter/Layouts/default/Rainmeter.ini': 'rainmeter_layout.ini',
    '~/.vimrc': 'vimrc',

    # POWERTOYS SECTION
    '%LOCALAPPDATA%/Microsoft/PowerToys/settings.json': jn('PowerToys', 'PowerToys.settings.json'),
    '%LOCALAPPDATA%/Microsoft/PowerToys/Awake/settings.json': pt_cfg('Awake'),
    '%LOCALAPPDATA%/Microsoft/PowerToys/ColorPicker/settings.json': pt_cfg('ColorPicker'),
    '%LOCALAPPDATA%/Microsoft/PowerToys/FancyZones/settings.json': pt_cfg('FancyZones'),
    '%LOCALAPPDATA%/Microsoft/PowerToys/FancyZones/zones-settings.json':
        jn('PowerToys', 'FancyZones', 'zones-settings.json'),

    '%LOCALAPPDATA%/Microsoft/PowerToys/File Explorer/settings.json': pt_cfg('FileExplorer'),
    '%LOCALAPPDATA%/Microsoft/PowerToys/Find My Mouse/settings.json': pt_cfg('FindMyMouse'),
    '%LOCALAPPDATA%/Microsoft/PowerToys/ImageResizer/settings.json': pt_cfg('ImageResizer'),
    '%LOCALAPPDATA%/Microsoft/PowerToys/ImageResizer/image-resizer-settings.json':
        jn('PowerToys', 'ImageResizer', 'image-resizer-settings.json'),

    '%LOCALAPPDATA%/Microsoft/PowerToys/Keyboard Manager/settings.json': pt_cfg('KeyboardManager'),
    '%LOCALAPPDATA%/Microsoft/PowerToys/Keyboard Manager/default.json':
        jn('PowerToys', 'KeyboardManager', 'default.json'),

    '%LOCALAPPDATA%/Microsoft/PowerToys/PowerRename/power-rename-settings.json':
        jn('PowerToys', 'PowerRename', 'power-rename-settings.json'),

    '%LOCALAPPDATA%/Microsoft/PowerToys/PowerToys Run/settings.json': pt_cfg('PowerToysRun'),
    '%LOCALAPPDATA%/Microsoft/PowerToys/Shortcut Guide/settings.json': pt_cfg('ShortcutGuide'),
    '%LOCALAPPDATA%/Microsoft/PowerToys/Video Conference/settings.json': pt_cfg('VideoConference'),
}


def download_and_install_font(url: str) -> None:
    from urllib.parse import unquote

    font_name = unquote(os.path.basename(url))

    if os.path.exists(os.path.join(Windows.FONTS_FOLDER, font_name)):
        logger.warn(f"Font '{font_name}' already installed, skipping...")
        return

    from windows_font_installer import install_font
    from utils import download_file

    logger.info(f"Downloading and installing font '{font_name}'...")
    font_path = os.path.join(tmpdir, font_name)
    download_file(url, font_path)

    logger.info('Installing...')
    install_font(font_path)


def install_winget_fn() -> None:
    from utils import download_file

    dep_url = 'https://aka.ms/Microsoft.VCLibs.x64.14.00.Desktop.appx'
    dep_setup = os.path.join(tmpdir, os.path.basename(dep_url))
    download_file(dep_url, dep_setup)

    download_url = 'https://github.com/microsoft/winget-cli/releases/download/v1.1.12653/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle'
    winget_setup = os.path.join(tmpdir, os.path.basename(download_url))

    download_file(download_url, winget_setup)
    msix.install(winget_setup, dependencies_paths=[dep_setup])


def setup_wsl() -> None:
    from utils import execute_cmd, cmd_as_bool
    if cmd_as_bool('wsl --status'):
        logger.warn('WSL is already installed, skipping installation...')
    else:
        logger.info(f"Installing WSL with distro {WSL_DISTRO}...")
        execute_cmd(f'wsl --install -d {WSL_DISTRO}')

    logger.info(f"Setting WSL version 2 as default...")
    execute_cmd(f'wsl --set-default-version 2')

    logger.info(f"Setting distro '{WSL_DISTRO}' as default...")
    execute_cmd(f'wsl --set-default {WSL_DISTRO}')
    logger.info('Done!')


if __name__ == '__main__':
    from utils import create_folders
    from shutil import rmtree

    logger.info(f"Changing working directory to the script's directory...")
    os.chdir(os.path.dirname(__file__))

    logger.info('Running Windows recipe...', True)
    tmpdir = tempfile.mkdtemp(prefix='windows_recipe')

    try:
        create_folders(folders)
        logger.info('Finished creating folders!', True)

        windows.make_links(links)
        logger.info('Finished creating symlinks!', True)

        windows.set_keyboard_layouts(KEYBOARD_LAYOUTS)
        windows.set_powershell_execution_policy()

        setup_wsl()

        if 'WSLENV' not in os.environ or 'USERPROFILE' not in os.environ['WSLENV']:
            logger.info('Adding Windows profile in WSL environment variables')
            windows.set_environment_var('WSLENV', 'USERPROFILE/p')
        else:
            logger.warn('Windows profile already added to WSL environment variables, skipping...')

        download_and_install_font(
            'https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/CascadiaCode/Regular/complete/Caskaydia%20Cove%20Regular%20Nerd%20Font%20Complete%20Windows%20Compatible.otf'
        )

        logger.info('Finished setups!', True)
        windows.install('scoop', install_scoop)
        windows.install('shovel', install_shovel_fn) # Keeps being reinstalled
        scoop.install(['7zip', 'git', 'shellcheck', 'innounp', 'dark', 'wixtoolset', 'lessmsi'])
        scoop.add_bucket('extras')
        scoop.install(scoop_apps)

        scoop.clean()

        windows.install('winget', install_winget_fn) # Keeps being reinstalled

        winget.install(winget_ids)
        logger.info('Finished installing packages!', True)
    finally:
        rmtree(tmpdir)
