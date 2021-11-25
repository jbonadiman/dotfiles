#!/usr/bin/env python3

import os
import log
import platform
import subprocess as sb
from typing import List, Callable

import requests

logger = log.get_logger()


def git_clone(url: str, path: str = None) -> None:
    alt_path = path or ''
    sb.run(f'git clone "{url}" {alt_path}'.strip(), shell=True, stdout=sb.PIPE)


def download_file(url: str, path: str) -> None:
    logger.info('Downloading...')
    resp = requests.get(url, allow_redirects=True)
    with open(path, 'wb') as f:
        f.write(resp.content)
    logger.info('Done!')


def abs_path(path: str) -> str:
    return os.path.abspath(
        os.path.expandvars(
            os.path.expanduser(path)
        )
    )


def execute_cmd(command: str) -> None:
    sb.check_call(command, shell=True)


def cmd_as_bool(command: str) -> bool:
    result = sb.run(f'{command} && echo 1 || echo 0', shell=True, stdout=sb.PIPE)
    return bool(int(result.stdout))


def create_folder(path: str) -> None:
    as_absolute = abs_path(path)
    if os.path.exists(as_absolute):
        logger.info(f"'{path}' folder already exists. Skipping...")
        return

    logger.info(f"Creating folder '{path}'...")
    os.makedirs(as_absolute, exist_ok=True)


def make_link(original: str, symlink: str) -> None:
    abs_symlink = abs_path(symlink)
    abs_original = abs_path(original)

    try:
        if not os.path.exists(abs_original):
            logger.info(f"Origin '{original}' does not exist. Skipping...")
            return

        if os.path.lexists(abs_symlink):
            if os.path.islink(abs_symlink) and os.path.realpath(abs_symlink) == abs_original:
                logger.info(f"Link '{symlink}' -> '{abs_original}' already exists and is updated. Skipping...")
                return
            else:
                logger.info(f"File already exists, removing and creating link to '{symlink}' -> '{abs_original}'...")
                os.remove(abs_symlink)
        else:
            logger.info(f"Creating link '{symlink}' -> '{abs_original}'...")
            os.makedirs(os.path.dirname(abs_symlink), exist_ok=True)

        os.symlink(abs_original, abs_symlink)

    except OSError as err:
        if err.winerror == 1314:
            logger.error(f'This script needs administrative permissions to create a symlink in "{abs_symlink}"'
                         f' pointing to "{abs_original}".\nGrant the permission and try again!')
        else:
            raise err


class SystemDependent:
    def __init__(self):
        if not self._can_execute():
            raise RuntimeError("This script can't be run in the current platform!")

    @staticmethod
    def __run_script(terminal: str, script_path: str, args: List[str], sudo: bool = False) -> None:
        sudo_token = 'sudo' if sudo else ''

        args_token = ''
        if args and len(args):
            args_token = ' ' + ' '.join(args) if len(args) > 1 else args[0]

        sb.run(f'{sudo_token} {terminal} {script_path}{args_token}', shell=True, stdout=sb.PIPE)

    @classmethod
    def install(cls, cmd_name: str, install_fn: Callable, check_exists=True, alias=None):
        display_name = alias or cmd_name

        if check_exists and cls.exists(cmd_name):
            logger.info(f'{display_name} already installed, skipping...')
        else:
            logger.info(f'Installing {display_name}...')
            install_fn()
            logger.info('Done!')


class WslDependent(SystemDependent):
    @staticmethod
    def _can_execute() -> bool:
        return platform.system().lower() == 'linux' and \
               'microsoft' in platform.release().lower()


class WindowsDependent(SystemDependent):
    @staticmethod
    def _can_execute() -> bool:
        return platform.system().lower() == 'windows'


class AndroidDependent(SystemDependent):
    @staticmethod
    def _can_execute() -> bool:
        return 'ANDROID_DATA' in os.environ


class Wsl(WslDependent):
    @classmethod
    def exists(cls, arg: str) -> bool:
        return cmd_as_bool(f'command -v {arg} > /dev/null 2>&1')

    @classmethod
    def execute_sh(cls, script_path: str, args: List[str] = None, sudo=False) -> None:
        cls.__run_script('sh', script_path, args, sudo)

    @classmethod
    def execute_bash(cls, script_path: str, args: List[str] = None, sudo=False) -> None:
        cls.__run_script('bash', script_path, args, sudo)


class Windows(WindowsDependent):
    PRELOAD_REGKEY = 'Preload'
    SUBSTITUTES_REGKEY = 'Substitutes'
    KEYBOARD_REGKEY = 'Keyboard Layout'

    FONTS_NAMESPACE = 0x14
    FONTS_FOLDER = ''
    PACKAGES_FOLDER = abs_path(
        os.path.join(
            '%LOCALAPPDATA%',
            'Packages'
        )
    )

    def __init__(self):
        super().__init__()

        import ctypes.wintypes

        buffer = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(0, Windows.FONTS_NAMESPACE, 0, 0, buffer)
        Windows.FONTS_FOLDER = buffer.value

    @classmethod
    def exists(cls, arg: str) -> bool:
        return cmd_as_bool(f'WHERE /Q {arg}')

    @classmethod
    def execute_ps1(cls, script_path: str, args: List[str] = None) -> None:
        cls.__run_script('powershell.exe', script_path, args, sudo=False)

    @classmethod
    def set_keyboard_layouts(cls, layouts: List[str]) -> None:
        from winreg import \
            OpenKey, \
            EnumValue, \
            QueryInfoKey, \
            DeleteKey, \
            CreateKey, \
            SetValueEx, \
            HKEY_CURRENT_USER, REG_SZ

        with OpenKey(HKEY_CURRENT_USER, cls.KEYBOARD_REGKEY) as keyboard_layout:
            updated = True

            with OpenKey(keyboard_layout, cls.SUBSTITUTES_REGKEY) as substitutes:
                substitutes_values_count = QueryInfoKey(substitutes)

            with OpenKey(keyboard_layout, cls.PRELOAD_REGKEY) as preload:
                preload_values_count = QueryInfoKey(preload)

                # Values in key and list differ in size or there is substitutions information
                if preload_values_count[1] != len(layouts) or substitutes_values_count[1] > 0:
                    updated = False
                else:
                    for i in range(len(layouts)):
                        value = EnumValue(preload, i)

                        # Key value differ in type or not in list
                        if value[2] != REG_SZ or value[1] not in layouts:
                            updated = False
                            break

            if updated:
                logger.info('Keyboard layout is updated, skipping...')
                return

            logger.info('Updating keyboard layout settings...')
            DeleteKey(keyboard_layout, cls.SUBSTITUTES_REGKEY)
            CreateKey(keyboard_layout, cls.SUBSTITUTES_REGKEY).Close()

            DeleteKey(keyboard_layout, cls.PRELOAD_REGKEY)
            with CreateKey(keyboard_layout, cls.PRELOAD_REGKEY) as preload:
                for name, value in enumerate(layouts, start=1):
                    SetValueEx(preload, str(name), 0, REG_SZ, value)

            logger.info('Done!')


class Scoop(WindowsDependent):
    SCOOP_VAR = 'SCOOP'
    SHOVEL_VAR = 'SHOVEL'

    @staticmethod
    def upgrade() -> None:
        sb.check_call(['scoop', 'update', '-q', '*'], shell=True)

    @staticmethod
    def install(packages: List[str]) -> None:
        sb.check_call(['scoop', 'install'] + packages, shell=True)

    @staticmethod
    def update() -> None:
        sb.check_call(['scoop', 'update', '-q'], shell=True)

    @staticmethod
    def add_bucket(bucket_name: str) -> None:
        if cmd_as_bool(f'scoop bucket list | findstr {bucket_name} > NUL'):
            logger.info(f"Bucket '{bucket_name}' already added, skipping...")
            return

        logger.info(f"Adding bucket '{bucket_name}'...")
        sb.check_call(['scoop', 'bucket', 'add', bucket_name], shell=True)

    @staticmethod
    def change_repo(repo: str) -> None:
        sb.check_call(['scoop', 'config', 'SCOOP_REPO', repo], shell=True)


class Msix(WindowsDependent):
    @staticmethod
    def install(packages_paths: List[str]) -> None:
        for path in packages_paths:
            logger.info(f"Installing {os.path.basename(path)}...")
            sb.check_call(['powershell.exe', '-c', 'Add-AppPackage', '-path', path], shell=True)


class Winget(WindowsDependent):
    @staticmethod
    def install(packages_id: List[str]) -> None:
        for pck_id in packages_id:
            if Winget.exists(pck_id):
                logger.info(f"Package with ID '{pck_id}' is already installed, skipping...")
                continue

            logger.info(f"Installing package with ID '{pck_id}'...")
            sb.check_call(
                ['winget', 'install', '-e', '--id', f'"{pck_id}"', '--accept-package-agreements', '--force'],
                shell=True)
            logger.info('Done!')

    @classmethod
    def exists(cls, package_id: str) -> bool:
        return cmd_as_bool(f'winget list -e --id "{package_id}" > NUL')


class Apt(WslDependent):
    @staticmethod
    def upgrade() -> None:
        sb.check_call(('sudo', 'apt-get', 'upgrade', '-y'))

    @staticmethod
    def install(packages: List[str]) -> None:
        sb.check_call(['sudo', 'apt-get', 'install', '-y'] + packages)

    @staticmethod
    def update() -> None:
        sb.check_call(('sudo', 'apt-get', 'update'))

    @staticmethod
    def add_repository(repo_name: str) -> None:
        sb.check_call(('sudo', 'add-apt-repository', f'ppa:{repo_name}', '-y'))

    @staticmethod
    def is_repository_added(repo_name: str) -> bool:
        return cmd_as_bool(f'grep -q "^deb .*{repo_name}" /etc/apt/sources.list /etc/apt/sources.list.d/*')


class Dpkg(WslDependent):
    @staticmethod
    def install(deb_paths: List[str]) -> None:
        sb.check_call(['sudo', 'dpkg', '-i'] + deb_paths)
