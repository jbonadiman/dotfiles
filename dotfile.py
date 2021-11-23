#!/usr/bin/env python3

import os
import platform
import subprocess as sb
from typing import List, Callable

import requests


def git_clone(url: str, path: str = None) -> None:
    alt_path = path or ''
    sb.run(f'git clone "{url}" {alt_path}'.strip(), shell=True, stdout=sb.PIPE)


def download_installer(url: str, path: str) -> None:
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


def exists(arg: str) -> bool:
    if Ubuntu.can_execute():
        return cmd_as_bool(f'command -v {arg} > /dev/null 2>&1')
    elif Windows.can_execute():
        return cmd_as_bool(f'WHERE /Q {arg}')
    raise NotImplementedError


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
        if os.path.islink(abs_symlink):
            if os.readlink(abs_symlink) == abs_original:
                print(f"Link '{symlink}' -> '{abs_original}' already exists and is updated. Skipping...")
                return
            print(f"Link exists, but it is outdated. Updating to '{symlink}' -> '{abs_original}'...")
            os.remove(abs_symlink)
            os.symlink(abs_original, abs_symlink)
            return
        print(f"Path '{symlink}' already exists and is not a link (is it correct?). Skipping...")
        return

    print(f"Creating link '{symlink}' -> '{abs_original}'...")
    os.symlink(abs_original, abs_symlink)


def install(cmd_name: str, install_fn: Callable, check_exists=True, alias=None):
    display_name = alias or cmd_name

    if check_exists and exists(cmd_name):
        print(f'{display_name} already installed, skipping...')
    else:
        print(f'Installing {display_name}...')
        install_fn()
        print('Done!')


class System:
    def __init__(self):
        if not self._can_execute():
            raise RuntimeError("This script can't be run in the current platform!")

    def _can_execute(self) -> bool:
        pass


class Ubuntu(System):
    @staticmethod
    def can_execute() -> bool:
        return platform.system().lower() == 'linux' and \
               'microsoft' in platform.release().lower()

    @staticmethod
    def __execute_terminal(terminal: str, path: str, args: List[str], sudo: bool = True) -> None:
        sudo_token = 'sudo' if sudo else ''
        args_token = ' '.join(args) if len(args) > 1 else args[0]
        sb.run(f'{sudo_token} {terminal} {path} {args_token}', shell=True, stdout=sb.PIPE)

    @staticmethod
    def execute_sh(path: str, args: List[str], sudo=False) -> None:
        Ubuntu.__execute_terminal('sh', path, args, sudo)

    @staticmethod
    def execute_bash(path: str, args: List[str], sudo=False) -> None:
        Ubuntu.__execute_terminal('bash', path, args, sudo)

    def _can_execute(self) -> bool:
        return Ubuntu.can_execute()


class Windows(System):
    @staticmethod
    def can_execute() -> bool:
        return platform.system().lower() == 'windows'

    def _can_execute(self) -> bool:
        return Windows.can_execute()


class Android(System):
    @staticmethod
    def can_execute() -> bool:
        return 'ANDROID_DATA' in os.environ

    def _can_execute(self) -> bool:
        return Android.can_execute()


class Scoop(Windows):
    def upgrade(self) -> None:
        pass

    def install_packages(self, *args: str) -> None:
        pass

    def remove_packages(self, *args: str) -> None:
        pass

    def update(self) -> None:
        pass


class Apt(Ubuntu):
    def upgrade(self) -> None:
        sb.check_call(('sudo', 'apt-get', 'upgrade', '-y'), shell=True)

    def install_packages(self, *args: str) -> None:
        sb.check_call(('sudo', 'apt-get', 'install', '-y') + args)

    def remove_packages(self, *args: str) -> None:
        sb.check_call(('sudo', 'apt-get', 'remove', '-y') + args, shell=True)

    def update(self) -> None:
        sb.check_call(('sudo', 'apt-get', 'update'), shell=True)

    def add_repository(self, repo_name: str) -> None:
        sb.check_call(('sudo', 'add-apt-repository', f'ppa:{repo_name}', '-y'), shell=True)

    def is_repository_added(self, repo_name: str) -> bool:
        return cmd_as_bool(f'grep -q "^deb .*{repo_name}" /etc/apt/sources.list /etc/apt/sources.list.d/*')


class Dpkg(Ubuntu):
    def install_packages(self, *args: str) -> None:
        sb.check_call(('sudo', 'dpkg', '-i') + args, shell=True)

    def remove_packages(self, *args: str) -> None:
        sb.check_call(('sudo', 'dpkg', '-r') + args, shell=True)
