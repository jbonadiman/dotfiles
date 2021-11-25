#!/usr/bin/env python3

import os
import platform
import subprocess as sb
from typing import List, Callable

import requests


def git_clone(url: str, path: str = None) -> None:
    alt_path = path or ''
    sb.run(f'git clone "{url}" {alt_path}'.strip(), shell=True, stdout=sb.PIPE)


def download_file(url: str, path: str) -> None:
    print('Downloading...')
    resp = requests.get(url, allow_redirects=True)
    with open(path, 'wb') as f:
        f.write(resp.content)
    print('Done!')


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
        print(f"'{path}' folder already exists. Skipping...")
        return

    print(f"Creating folder '{path}'...")
    os.makedirs(as_absolute, exist_ok=True)


def make_link(original: str, symlink: str) -> None:
    abs_symlink = abs_path(symlink)
    abs_original = abs_path(original)

    if not os.path.exists(abs_original):
        print(f"Origin '{original}' does not exist. Skipping...")
        return

    if os.path.lexists(abs_symlink):
        if os.path.islink(abs_symlink) and os.path.realpath(abs_symlink) == abs_original:
            print(f"Link '{symlink}' -> '{abs_original}' already exists and is updated. Skipping...")
            return
        else:
            print(f"File already exists, removing and creating link to '{symlink}' -> '{abs_original}'...")
            os.remove(abs_symlink)
    else:
        print(f"Creating link '{symlink}' -> '{abs_original}'...")
        os.makedirs(os.path.dirname(abs_symlink), exist_ok=True)

    os.symlink(abs_original, abs_symlink)


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
            print(f'{display_name} already installed, skipping...')
        else:
            print(f'Installing {display_name}...')
            install_fn()
            print('Done!')


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
    FONTS_NAMESPACE = 0x14
    FONTS_FOLDER = ''

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


class Scoop(WindowsDependent):
    SCOOP_VAR = 'SCOOP'
    SHOVEL_VAR = 'SHOVEL'

    @staticmethod
    def upgrade() -> None:
        sb.check_call(['scoop', 'update', '*'], shell=True)

    @staticmethod
    def install(packages: List[str]) -> None:
        sb.check_call(['scoop', 'install'] + packages, shell=True)

    @staticmethod
    def update() -> None:
        sb.check_call(['scoop', 'update'], shell=True)

    @staticmethod
    def add_bucket(bucket_name: str) -> None:
        if cmd_as_bool(f'scoop bucket list | findstr {bucket_name} > NUL'):
            print(f"Bucket '{bucket_name}' already added, skipping...")
            return

        print(f"Adding bucket '{bucket_name}'...")
        sb.check_call(['scoop', 'bucket', 'add', bucket_name], shell=True)

    @staticmethod
    def change_repo(repo: str) -> None:
        sb.check_call(['scoop', 'config', 'SCOOP_REPO', repo], shell=True)


class Msix(WindowsDependent):
    @staticmethod
    def install(packages_paths: List[str]) -> None:
        for path in packages_paths:
            print(f"Installing {os.path.basename(path)}...")
            sb.check_call(['powershell.exe', '-c', 'Add-AppPackage', '-path', path], shell=True)


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
