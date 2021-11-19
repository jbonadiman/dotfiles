#!/usr/bin/env python3

from abc import ABC, abstractmethod
import platform
from subprocess import STDOUT, check_call
import os
import ctypes

class SystemSpecific(ABC):
    def __init__(self):
        if not self.can_execute():
            raise RuntimeError("This script can't be run in the current platform!")

    @abstractmethod
    def is_admin(self) -> bool:
        pass

    @abstractmethod
    def can_execute(self) -> bool:
        pass

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

class WslPackageManager(SystemSpecific, PackageManager, ABC):
    def is_admin(self) -> bool:
        return os.getuid() == 0

    def can_execute(self) -> bool:
        return platform.system().lower() == 'linux' and \
            'microsoft' in platform.release().lower()

class WindowsPackageManager(SystemSpecific, PackageManager, ABC):
    def is_admin(self) -> bool:
        ctypes.windll.shell32.IsUserAnAdmin() != 0

    def can_execute(self) -> bool:
        return platform.system().lower() == 'windows'

class Apt(WslPackageManager):
    def upgrade(self) -> None:
        print('apt upgrade')

    def install(self, package_name: str) -> None:
        check_call(['apt-get', 'install', '-y', package_name], stdout=open(os.devnull,'wb'), stderr=STDOUT)

    def remove(self, package_name: str) -> None:
        print('sudo apt remove ' + package_name)

    def update(self) -> None:
        check_call(['sudo', 'apt-get', '-y', 'update'])

if __name__ == '__main__':
    apt = Apt()
    apt.update()
