#!/usr/bin/env python3
from __future__ import annotations

import os
import platform
import re
import subprocess as sb
import sys
from typing import Callable, Iterable, Any
import inspect

from pathlib import Path
from loguru import logger
from nanoid import generate as gen_id

from colorama import Fore, Style

from utils import \
    requires_admin, \
    abs_path, \
    execute_cmd, \
    cmd_as_bool, \
    _make_links

logger.disable('dotfile')
script_dir = Path(inspect.getframeinfo(inspect.currentframe()).filename).parent


class SystemDependent:
    package_managers: dict[str, PackageManager]

    @classmethod
    def make_links(cls, links: dict[str, str]):
        pass

    @classmethod
    def can_execute(cls) -> bool:
        pass

    @classmethod
    @requires_admin
    def _run_script(cls, terminal: str, script_path: str, args: list[str] | None, sudo: bool | None = None):
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
    def exists(cls, arg: str) -> bool:
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
    @classmethod
    def can_execute(cls) -> bool:
        return platform.system().lower() == 'linux' and \
               'microsoft' in platform.release().lower()


class WindowsDependent(SystemDependent):
    @classmethod
    def can_execute(cls) -> bool:
        return platform.system().lower() == 'windows'


class AndroidDependent(SystemDependent):
    @classmethod
    def can_execute(cls) -> bool:
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

        Windows.package_managers = {
            'scoop': Scoop(),
            'winget': Winget()
        }

    @classmethod
    def set_environment_var(cls, name: str, value: str):
        from os import environ
        execute_cmd(f'SETX {name.upper()} {value}', stderr=False)
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


def execute_recipe(recipe: dict, system: SystemDependent):
    logger.info(f"Changing working directory to the script's directory...")
    execute_section(recipe, system)

    if 'sections' in recipe['settings']:
        for section_name in recipe['settings']['sections']:
            execute_section(recipe[section_name], system)


def create_file(path: str | os.PathLike):
    logger.info('Creating file {path}...', path=path)
    Path(path).touch()


def create_folder(path: str | os.PathLike):
    logger.info('Creating folder {path}...', path=path)
    Path(path).mkdir(parents=True)


def get_create_function(path: str | os.PathLike) -> Callable[[None], None]:
    path = Path(path).expanduser()
    if path.exists():
        if path.is_dir():
            path_type = 'Folder'
        elif path.is_symlink():
            path_type = 'Link'
        else:
            path_type = 'File'

        return lambda: logger.warning(
            "{type} '{path}' already exists. Skipping...",
            type=path_type,
            path=path
        )

    elif path.name.startswith('.') or path.suffix:  # file that still doesn't exist
        return lambda: create_file(path)

    # it must be a folder, then...
    return lambda: create_folder(path)


def execute_shell(path: os.PathLike | None = None, command: str | None = None) -> Any:
    if not path and not command:
        return

    return sb.check_output(
        path or command,
        stderr=sb.PIPE,
        shell=True,
        cwd=script_dir
    )


def get_shell_function(script_path: str | os.PathLike) -> Callable[[None], None]:
    script_path: Path = Path(script_path).expanduser()
    if not script_path.exists():
        return lambda: logger.error(
            "Shell script '{path}' doesn't exist. Is this the right path?...",
            path=script_path
        )

    return lambda: execute_shell(script_path)


def create_link(target: Path, link: Path):
    if not target or not link:
        logger.warning('Target and link paths must be provided for symlink creation!')
        return

    logger.info("Creating link '{link}' -> '{target}'")
    link.symlink_to(target)


def get_link_function(target: str | Path, link: str | Path) -> Callable[[None], None]:
    target_path = Path(target).expanduser().resolve()
    link_path = Path(link).expanduser().resolve()

    if link_path.exists():
        if link_path.is_symlink():
            link_target = link_path.readlink()

            if link_target == target_path:
                return lambda: logger.warning(
                    "Link '{}' already exists. Skipping creation...",
                    link_path)

        def update_link():
            logger.info(
                "Link '{}' already exists. Updating reference...",
                link_path)
            link_path.unlink()
            link_path.symlink_to(target_path)

        return update_link

    if not target_path.exists():
        return lambda: logger.error(
            "Target path '{}' doesn't exist. Is this the right path?",
            target_path
        )

    return lambda: create_link(target_path, link_path)


def parse_section(section: dict, system: SystemDependent):
    id_dict: dict[str, Callable[[None], None]] = {}

    if 'create' in section:
        for action in section['create']:
            path: str = action
            action_id: str = gen_id()

            if type(action) == dict:
                if 'id' in action:
                    # action was already parsed
                    if action['id'] in id_dict:
                        continue
                    action_id = action['id']
                else:
                    path = action['path']
            id_dict[action_id] = get_create_function(path)

    if 'shell' in section:
        for action in section['shell']:
            script: str = action
            action_id: str = gen_id()

            if type(action) == dict:
                if 'id' in action:
                    # action was already parsed
                    if action['id'] in id_dict:
                        continue
                    action_id = action['id']
                else:
                    script = action['script']
            id_dict[action_id] = get_shell_function(script)

    if 'link' in section:
        for action in section['link']:
            target: str = ''
            link: str = ''
            action_id: str = gen_id()

            if 'id' in action:
                action_id = action['id']

            if 'target' in action and 'link' in action:
                target = action['target']
                link = action['link']
            else:
                target, link = list(action.items())[0]

            id_dict[action_id] = get_link_function(target, link)


def execute_section(section: dict, system: SystemDependent):
    from utils import create_folders

    logger.info(f"Running \'{section['name']}\'...", accented=True)

    if 'create' in section:
        create_folders(section['create'])
        logger.info('Finished creating folders!', accented=True)

    if 'link' in section:
        system.make_links(section['link'])
        logger.info('Finished creating symlinks!', accented=True)

    if 'install' in section:
        for manager_name, packages_info in section['install'].items():
            if manager_name in system.package_managers:
                package_manager = system.package_managers[manager_name]
                packages: set[str] = set()
                repos: set[str] = set()

                for info in packages_info:
                    if type(info) == str:
                        packages.add(info)
                        continue

                    if 'depends_on' in info:
                        packages.update((dep for dep in info['depends_on']))
                    if 'repository' in info:
                        repos.add(info['repository'])
                    packages.add(info['name'])

                package_manager.install_itself()
                if repos:
                    package_manager.add_repositories(repos)
                package_manager.install(packages)
            elif manager_name == 'custom':
                for custom_install in packages_info:
                    logger.info(custom_install["name"])
                    for cmd in custom_install['commands']:
                        execute_cmd(cmd, stderr=True)
            else:
                logger.error(f"Invalid package manager: '{manager_name}'")

    if 'shell' in section:
        for execution in section['shell']:
            execute_cmd(
                command=execution['command'],
                stderr=execution['stderr']
            )

        logger.info('Finished executing scripts!', accented=True)


class PackageManager:
    @classmethod
    def install_itself(cls):
        logger.info(f'Installing {Fore.RED}{cls.__name__.lower()}{Style.RESET_ALL}...')

    @classmethod
    def install(cls, package_names: Iterable[str]):
        stylized_names = map(
            lambda name: f'{Fore.BLUE}{name}{Style.RESET_ALL}',
            package_names
        )

        logger.info(f'Using {Fore.RED}{cls.__name__.lower()}{Style.RESET_ALL} to install package(s): '
                    f"{', '.join(stylized_names)}...")

    @classmethod
    def upgrade(cls):
        logger.info(f'Upgrading {Fore.RED}{cls.__name__.lower()}{Style.RESET_ALL} packages...')

    @classmethod
    def update(cls):
        logger.info(f'Updating {Fore.RED}{cls.__name__.lower()}{Style.RESET_ALL} references...')

    @classmethod
    def add_repositories(cls, repositories: Iterable[str]):
        logger.info(f'Adding repositories to {Fore.RED}{cls.__name__.lower()}{Style.RESET_ALL}...')

    @classmethod
    def clean(cls):
        logger.info(f'Cleaning up {Fore.RED}{cls.__name__.lower()}{Style.RESET_ALL} cache...')


class Scoop(PackageManager):
    SCOOP_VAR_NAME: str = 'SCOOP'
    SHOVEL_VAR_NAME: str = 'SHOVEL'
    BUCKETS: set = set()
    APPS: set = set()

    # TODO: This should be gone when I find a way to update the env var after installation
    PATH = abs_path('~/scoop/shims/scoop')
    CMD = 'scoop' if SCOOP_VAR_NAME in os.environ else PATH

    def __init__(self):
        try:
            self.load_buckets()
            self.load_installed()
        except Exception as exc:
            logger.warn(exc)

    @classmethod
    def install_itself(cls):
        if cls.SCOOP_VAR_NAME in os.environ and os.path.isfile(cls.PATH):
            pass
        else:
            super().install_itself()

            import tempfile
            from utils import download_file
            from glob import glob
            from shutil import copy2

            global tmpdir
            if not tmpdir:
                tmpdir = str(tempfile.mkdtemp(prefix=os.path.basename(__file__)))

            scoop_installer = os.path.join(tmpdir, 'install.ps1')
            download_file(r'https://get.scoop.sh', scoop_installer)
            windows.execute_ps1(scoop_installer)
            if cls.SCOOP_VAR_NAME not in os.environ:
                logger.info(f"Adding '{cls.SCOOP_VAR_NAME}' to environment variables...")
                windows.set_environment_var(cls.SCOOP_VAR_NAME, cls.PATH)

            scoop.change_repo('https://github.com/Ash258/Scoop-Core')
            # shovel installation
            for file in glob(f'{cls.PATH}.*'):
                new_filename = os.path.join(
                    os.path.dirname(file),
                    f'shovel{os.path.splitext(file)[1]}'
                )
                copy2(file, new_filename)

            cls.load_buckets()

    @classmethod
    def load_installed(cls):
        app_list = execute_cmd(f'{cls.CMD} list').decode('utf-8')
        regex = r'^\s{2}([0-9a-zA-Z-]+)\s+(?:\d*(?:\.\d+)+(?:(?:\-\d+)|\.\w+\.\d+)?)?\s+\[\w+\]'
        matches = re.finditer(regex, app_list, re.MULTILINE)

        cls.APPS.update((match.group(1) for match in matches))

    @classmethod
    def load_buckets(cls):
        cls.BUCKETS.update(
            execute_cmd(f'{cls.CMD} bucket list').decode('utf-8').split()
        )

    @classmethod
    def upgrade(cls):
        super().upgrade()
        execute_cmd(f'{cls.CMD} update *')

    @classmethod
    def install(cls, package_names: Iterable[str]):
        listed = set(package_names)
        if not len(listed):
            logger.warn(f'{Fore.RED}{cls.__name__.lower()}{Style.RESET_ALL} install list is empty, skipping...')
            return

        inter = cls.APPS.intersection(listed)
        listed.difference_update(cls.APPS)

        if len(inter) > 0:
            if len(listed) == 0:
                logger.warn(f'All {Fore.RED}{cls.__name__.lower()}{Style.RESET_ALL} packages are already installed. '
                            f'Skipping installation...')
                return

            stylized_names = map(
                lambda name: f'{Fore.BLUE}{name}{Style.RESET_ALL}',
                inter
            )

            logger.warn(f'The following {Style.BRIGHT}{cls.__name__.lower()}{Style.NORMAL} package(s) are already '
                        f'installed and will be skipped: {", ".join(stylized_names)}...')
        super().install(listed)
        logger.info(execute_cmd(f'{cls.CMD} install {" ".join(listed)}', stderr=True))
        cls.APPS.update(listed)

    @classmethod
    def update(cls):
        super().update()
        execute_cmd(f'{cls.CMD} update')

    @classmethod
    def clean(cls):
        super().clean()
        execute_cmd(f'{cls.CMD} cleanup *')

    @classmethod
    def add_repositories(cls, repositories: Iterable[str]):
        super().add_repositories(repositories)
        for bucket_name in repositories:
            if bucket_name in cls.BUCKETS:
                logger.warn(f"Bucket '{bucket_name}' already added, skipping...")
                continue

            logger.info(f"Adding bucket '{bucket_name}' to {cls.__name__.lower()}...")
            execute_cmd(f'{cls.CMD} bucket add {bucket_name}')
            cls.BUCKETS.add(bucket_name)

    @classmethod
    def change_repo(cls, repo: str):
        logger.info(f"Changing {cls.__name__.lower()} repository to '{repo}'...")
        execute_cmd(f'{cls.CMD} config SCOOP_REPO {repo}')


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


class Winget(PackageManager):
    @classmethod
    def install(cls, package_names: Iterable[str]):
        super().install(package_names)

        for pck_id in package_names:
            if cls.exists(pck_id):
                logger.warn(f"Package with ID '{pck_id}' is already installed, skipping...")
                continue

            execute_cmd(
                f'winget install -e --id {pck_id} --accept-package-agreements --accept-source-agreements --force')

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


# TODO: This should be improved
tmpdir: str = ''

if __name__ == '__main__':
    from utils import read_yaml

    logger.enable('dotfile')

    config = {
        'handlers': [
            {'sink': sys.stdout, 'colorize': True, 'format': '[{time}]: {message}'}
        ]
    }

    logger.configure(**config)

    windows = Windows()
    wsl = Wsl()

    scoop = Scoop()
    winget = Winget()
    apt = Apt()

    systems: Iterable[SystemDependent] = [windows, wsl]

    recipe_file = read_yaml('./windows_recipe.yaml')

    for host_system in systems:
        if host_system.can_execute():
            execute_recipe(recipe_file, host_system)
