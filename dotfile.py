#!/usr/bin/env python3

from abc import ABC, abstractmethod
import platform
import subprocess as sb
import os
import ctypes

def abs_path(path: str) -> str:
    return os.path.abspath(
        os.path.expandvars(
            os.path.expanduser(path)
        )
    )

def exists(arg: str) -> bool:
    if Wsl.can_execute():
        result = sb.run(f'$(command -v {arg} > /dev/null 2>&1) && echo 1 || echo 0', shell=True, stdout=sb.PIPE)
        return bool(int(result.stdout))
    elif Windows.can_execute():
        result = sb.run(f'where {arg}', shell=True, stdout=sb.PIPE)
        print(result.stdout)
        print(result.stderr)
        return False
    raise NotImplementedError

def create_folder(self, path: str) -> None:
    as_absolute = abs_path(path)
    if os.path.exists(as_absolute):
        print(f"'{path}' folder already exists. Skipping...")
        return

    print(f"Creating folder '{path}'...")
    os.makedirs(as_absolute, exist_ok=True)

def make_link(self, source: str, destination: str) -> None:
    abs_dst = abs_path(destination)
    abs_src = abs_path(source)

    if not os.path.exists(abs_src):
        print(f"Origin '{source}' does not exist. Skipping...")
        return

    if os.path.exists(abs_dst):
        if os.path.islink(abs_dst):
            if os.readlink(abs_dst) == abs_src:
                print(f"Link '{destination}' -> '{source}' already exists. Skipping...")
                return
            print(f"Link exists, but it is outdated. Updating to '{destination}' -> '{abs_src}'...")
            os.remove(abs_dst)
            os.symlink(abs_src, abs_dst)
            return
        print(f"Destination '{destination}' already exists. Skipping...")
        return

    print(f"Creating link '{destination}' -> '{abs_src}'...")
    os.symlink(abs_src, abs_dst)

class SystemSpecific(ABC):
    def __init__(self):
        if not self._can_execute():
            raise RuntimeError("This script can't be run in the current platform!")

    @abstractmethod
    def _can_execute(self) -> bool:
        pass

class Wsl(SystemSpecific):
    def can_execute() -> bool:
        return platform.system().lower() == 'linux' and \
            'microsoft' in platform.release().lower()

    def _can_execute(self) -> bool:
        return Wsl.can_execute()

class Windows(SystemSpecific):
    def can_execute() -> bool:
        return platform.system().lower() == 'windows'

    def _can_execute(self) -> bool:
        return Windows.can_execute()

class PackageManager(ABC):
    @abstractmethod
    def upgrade(self) -> None:
        pass

    @abstractmethod
    def install(self, package_name: str) -> None:
        pass

    @abstractmethod
    def remove(self, package_name: str) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

class Scoop(Windows, PackageManager):
    def upgrade(self) -> None:
        pass

    def install(self, package_name: str) -> None:
        pass

    def remove(self, package_name: str) -> None:
        pass

    def upgrade(self) -> None:
        pass

class Apt(Wsl, PackageManager):
    def upgrade(self) -> None:
        sb.check_call(['sudo', 'apt-get', 'upgrade', '-y'])

    def install(self, package_name: str) -> None:
        sb.check_call(['sudo', 'apt-get', 'install', '-y', package_name])

    def remove(self, package_name: str) -> None:
        sb.check_call(['sudo', 'apt-get', 'remove', '-y', package_name])

    def update(self) -> None:
        sb.check_call(['sudo', 'apt-get', 'update'])
