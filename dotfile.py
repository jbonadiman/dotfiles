#!/usr/bin/env python3
from __future__ import annotations

import os
import platform
import subprocess as sb
from typing import Callable

import log
from utils import \
    requires_admin, \
    abs_path, \
    execute_cmd, \
    cmd_as_bool, \
    _make_links, \
    exhaust

logger = log.get_logger()


class SystemDependent:
    def __init__(self):
        if not self._can_execute():
            raise RuntimeError("This script can't be run in the current platform!")

    @classmethod
    @requires_admin
    def _run_script(cls, terminal: str, script_path: str, args: list[str] | None, sudo: bool | None=None) -> None:
        sudo_token = 'sudo' if sudo else ''
        args_token = ''
        if args and len(args):
            args_token = ' '.join(args) if len(args) > 1 else args[0]

        script_name = os.path.basename(script_path)
        args_log = f"with args '{args_token}'" if args_token else 'without args'
        logger.info(
            f"Using terminal '{terminal}' to run the script '{script_name}'{' as sudo' if sudo else ''} {args_log}"
        )

        sb.run(f'{sudo_token} {terminal} {script_path}{" " + args_token}', shell=True, stdout=sb.PIPE, check=True)

    @classmethod
    def exists(cls, arg: str):
        pass

    @classmethod
    @requires_admin
    def install(cls, cmd_name: str, install_fn: Callable, check_exists=True, alias=None):
        display_name = alias or cmd_name

        if check_exists and cls.exists(cmd_name):
            logger.warn(f"'{display_name}' already installed, skipping...")
        else:
            logger.info(f"Installing '{display_name}'...")
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
    HOME: str = None

    def __init__(self):
        super().__init__()
        Wsl.HOME = abs_path('~')

    @classmethod
    def exists(cls, arg: str) -> bool:
        return cmd_as_bool(f'command -v "{arg}"')

    @classmethod
    def execute_sh(cls, script_path: str, args: list[str] = None, sudo=False) -> None:
        cls._run_script('sh', script_path, args, sudo)

    @classmethod
    def execute_bash(cls, script_path: str, args: list[str] = None, sudo=False) -> None:
        cls._run_script('bash', script_path, args, sudo)

    @classmethod
    @requires_admin
    def make_links(cls, links: dict[str, str]):
        import os.path

        logger.info('Creating symlinks...')

        for symlink, original in links.items():
            abs_symlink = abs_path(symlink)
            abs_original = abs_path(original)

            if not os.path.exists(abs_original):
                logger.warn(f"Origin '{original}' does not exist, skipping...")
                continue

            if os.path.lexists(abs_symlink):
                if os.path.islink(abs_symlink) and os.path.realpath(abs_symlink) == abs_original:
                    logger.warn(f"Link '{symlink}' -> '{abs_original}' already exists and is updated, skipping...")
                    continue
                else:
                    logger.info(
                        f"File already exists, removing and creating link to '{symlink}' -> '{abs_original}'...")
            else:
                logger.info(f"Creating link '{symlink}' -> '{abs_original}'...")
                os.makedirs(os.path.dirname(abs_symlink), exist_ok=True)

            execute_cmd(f'sudo ln -sf "{abs_original}" "{abs_symlink}"')

    @classmethod
    @requires_admin
    def set_login_shell(cls, shell: str):
        logger.info('Setting up login shell...')
        if cmd_as_bool(f'echo $SHELL | grep --quiet "{shell}"'):
            logger.warn(f'Login shell is already {shell}, skipping...')
        else:
            logger.info(f'Changing login shell to {shell}...')
            Apt.install([shell])
            execute_cmd(f'sudo usermod --shell $(which {shell}) $(whoami)')
        logger.info('Finished setting up login shell!')

    @classmethod
    @requires_admin
    def set_locales(cls, locales: list[str]):
        import locale
        must_install = []

        logger.info("Setting up locales...")
        for localization in locales:
            try:
                locale.setlocale(locale.LC_ALL, localization)
                logger.warn(f"Locale '{localization}' is already installed, skipping...")
            except locale.Error:
                must_install.append(localization)

        if len(must_install) > 0:
            logger.info('Installing missing locales...')
            execute_cmd(f'sudo locale-gen {" ".join(must_install)}; sudo update-locale')

        locale.setlocale(locale.LC_ALL, '')
        logger.info('Finished setting up locales!')


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

        logger.debug('Getting fonts folder location...')
        buffer = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(0, Windows.FONTS_NAMESPACE, 0, 0, buffer)
        Windows.FONTS_FOLDER = buffer.value
        logger.debug(f'Located font folder at "{buffer.value}"')

    @classmethod
    def set_environment_var(cls, name: str, value: str):
        from os import environ
        execute_cmd(f'SETX {name.upper()} {value}', quiet=True)
        environ[name.upper()] = value

    @classmethod
    @requires_admin
    def make_links(cls, links: dict[str, str]):
        return _make_links(links)

    @classmethod
    def exists(cls, arg: str) -> bool:
        return cmd_as_bool(f'WHERE /Q "{arg}"')

    @classmethod
    def execute_ps1(cls, script_path: str, args: list[str] = None):
        cls._run_script('powershell.exe', script_path, args)

    @classmethod
    @requires_admin
    def set_powershell_execution_policy(cls):
        execute_cmd("powershell.exe Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned")

    @classmethod
    @requires_admin
    def set_keyboard_layouts(cls, layouts: list[str]):
        logger.info('Setting up keyboard layout...')
        from winreg import \
            OpenKey, \
            EnumValue, \
            QueryInfoKey, \
            DeleteKey, \
            CreateKey, \
            SetValueEx, \
            HKEY_CURRENT_USER, REG_SZ

        keyboard_regname = f'HKEY_CURRENT_USER/{cls.KEYBOARD_REGKEY}'
        substitutes_regname = f'{keyboard_regname}/{cls.SUBSTITUTES_REGKEY}'
        preload_regname = f'{keyboard_regname}/{cls.PRELOAD_REGKEY}'

        logger.debug(f'Opening registry key "{keyboard_regname}"')
        with OpenKey(HKEY_CURRENT_USER, cls.KEYBOARD_REGKEY) as keyboard_layout:
            updated = True

            logger.debug(f'Opening registry key "{substitutes_regname}"')
            with OpenKey(keyboard_layout, cls.SUBSTITUTES_REGKEY) as substitutes:
                substitutes_values_count = QueryInfoKey(substitutes)
                logger.debug(f'Closing registry key "{substitutes_regname}"')

            logger.debug(f'Opening registry key "{preload_regname}"')
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
                logger.debug(f'Closing registry key "{preload_regname}"')

            if updated:
                logger.warn('Keyboard layout is updated, skipping...')
                return

            logger.info('Updating keyboard layout settings...')
            DeleteKey(keyboard_layout, cls.SUBSTITUTES_REGKEY)
            CreateKey(keyboard_layout, cls.SUBSTITUTES_REGKEY).Close()

            DeleteKey(keyboard_layout, cls.PRELOAD_REGKEY)
            with CreateKey(keyboard_layout, cls.PRELOAD_REGKEY) as preload:
                for name, value in enumerate(layouts, start=1):
                    SetValueEx(preload, str(name), 0, REG_SZ, value)

            logger.info('Done!')


class App:
    def __init__(self,
                 name: str,
                 system: SystemDependent,
                 depends_on: list[App] | None = None,
                 exists_function_or_command: Callable[[None], bool] | str = None,
                 install_function_or_commands: Callable[[None], None] | list[str] = None):
        if not name.strip():
            raise ValueError('Application name is required!')
        if not system:
            raise ValueError('Application system is required!')
        if not install_function_or_commands:
            raise ValueError('Custom install function or commands list must be supplied!')
        if not exists_function_or_command:
            raise ValueError('Custom exists function or commands list must be supplied!')

        self.name: str = name
        self.system: SystemDependent = system
        self.depends_on: list[App] = depends_on

        self.install_routine: Callable[[None], None] = lambda: exhaust(
            (execute_cmd(cmd) for cmd in install_function_or_commands)
        ) if install_function_or_commands is str else install_function_or_commands

        self.exists_routine: Callable[[None], bool] = \
            lambda: system.exists(exists_function_or_command) \
                if exists_function_or_command is str \
                else exists_function_or_command

    def install(self):
        if self.exists:
            logger.warn(f"'{self.name}' is already installed, skipping...")
        else:
            if self.depends_on:
                logger.info(f"Installing dependencies for '{self.name}'...")
                for dependency in self.depends_on:
                    dependency.install()

            logger.info(f"Installing '{self.name}'...")
            self.install_routine()

    def exists(self) -> bool:
        return self.exists_routine()


class Scoop(WindowsDependent):
    SCOOP_VAR = 'SCOOP'
    SHOVEL_VAR = 'SHOVEL'

    @staticmethod
    def upgrade():
        sb.check_call(['scoop', 'update', '-q', '*'], shell=True)

    @staticmethod
    def install(packages: list[str]):
        sb.check_call(['scoop', 'install'] + packages, shell=True)

    @staticmethod
    def update():
        sb.check_call(['scoop', 'update', '-q'], shell=True)

    @staticmethod
    def add_bucket(bucket_name: str):
        if cmd_as_bool(f'scoop bucket list | findstr {bucket_name}'):
            logger.warn(f"Bucket '{bucket_name}' already added, skipping...")
            return

        logger.info(f"Adding bucket '{bucket_name}'...")
        sb.check_call(['scoop', 'bucket', 'add', bucket_name], shell=True)

    @staticmethod
    def change_repo(repo: str):
        sb.check_call(['scoop', 'config', 'SCOOP_REPO', repo], shell=True)

    @staticmethod
    def clean():
        sb.check_call(['scoop', 'cleanup', '*'], shell=True)


class Msix(WindowsDependent):
    @staticmethod
    def install(package_path: str, dependencies_paths: list[str] = None):
        logger.info(f"Installing {os.path.basename(package_path)}...")
        dep_token = ''

        if dependencies_paths:
            dep_token = f' {" ".join(dependencies_paths)}'

        sb.check_call(
            ['powershell.exe', '-c', 'Add-AppxPackage', '-Path', package_path]
            + ['-DependencyPackages', dep_token] if dependencies_paths else [], shell=True)


class Winget(WindowsDependent):
    @staticmethod
    def install(packages_id: list[str]):
        for pck_id in packages_id:
            if Winget.exists(pck_id):
                logger.warn(f"Package with ID '{pck_id}' is already installed, skipping...")
                continue

            logger.info(f"Installing package with ID '{pck_id}'...")
            sb.run(f'winget install -e --id {pck_id} --accept-package-agreements --accept-source-agreements --force',
                   shell=True,
                   check=True)
            logger.info('Done!')

    @classmethod
    def exists(cls, package_id: str) -> bool:
        return cmd_as_bool(f'winget list -e --id "{package_id}"')


class Apt(WslDependent):
    @staticmethod
    @requires_admin  # TODO: is it really?
    def upgrade():
        sb.check_call(('sudo', 'apt-get', 'upgrade', '-y'))

    @staticmethod
    @requires_admin
    def install(packages: list[str]):
        sb.check_call(['sudo', 'apt-get', 'install', '-y'] + packages)

    @staticmethod
    @requires_admin
    def update():
        logger.info('Updating apt references...')
        sb.check_call(('sudo', 'apt-get', 'update'))

    @staticmethod
    @requires_admin  # TODO: is it really?
    def add_repository(repo_name: str):
        logger.info(f"Adding '{repo_name}' repository to apt...")
        sb.check_call(('sudo', 'add-apt-repository', f'ppa:{repo_name}', '-y'))

    @staticmethod
    def is_repository_added(repo_name: str) -> bool:
        return cmd_as_bool(f'grep -q "^deb .*{repo_name}" /etc/apt/sources.list /etc/apt/sources.list.d/*')

    @staticmethod
    def clean():
        sb.check_call(('sudo', 'apt-get', 'autoremove'))


class Dpkg(WslDependent):
    @staticmethod
    @requires_admin
    def install(deb_paths: list[str]):
        for path in deb_paths:
            sb.check_call(['sudo', 'dpkg', '-i', f'{path}'])
