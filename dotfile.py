#!/usr/bin/env python3

import os
import platform
import subprocess as sb
from functools import wraps
from typing import List, Callable, Dict

import requests

import log

logger = log.get_logger()


def requires_admin(fn: Callable):
    @wraps(fn)
    def wrapped_f(*args, **kwargs):
        logger.info(f"Using administrative privileges to '{fn.__qualname__}'...")
        try:
            return fn(*args, **kwargs)
        except (OSError, PermissionError) as err:
            if err.errno == 13 or ('winerror' in err.__dict__ and err.winerror == 1314):
                logger.error(f"Administrative privileges are required to {fn.__qualname__}\n"
                             f'ARGUMENTS: {args} {kwargs}')
            else:
                raise err

    return wrapped_f


def git_clone(url: str, path: str = None) -> None:
    alt_path = f' "{path}"' or ''
    sb.run(f'git clone -q "{url}"{alt_path}'.strip(), shell=True, stdout=sb.PIPE)


def download_file(url: str, path: str) -> None:
    logger.info('Downloading...')
    resp = requests.get(url, allow_redirects=True)
    with open(path, 'wb') as f:
        f.write(resp.content)
    logger.info('Finished downloading!')


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


@requires_admin
def create_folders(paths: List[str]) -> None:
    import os.path

    logger.info('Creating folders...')
    for p in paths:
        as_absolute = abs_path(p)
        if os.path.exists(as_absolute):
            logger.warn(f"'{p}' folder already exists, skipping...")
            continue

        logger.info(f"Creating folder '{p}'...")
        os.makedirs(as_absolute, exist_ok=True)


@requires_admin
def _make_links(links: Dict[str, str]) -> None:
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
                logger.info(f"File already exists, removing and creating link to '{symlink}' -> '{abs_original}'...")
                os.remove(abs_symlink)
        else:
            logger.info(f"Creating link '{symlink}' -> '{abs_original}'...")
            os.makedirs(os.path.dirname(abs_symlink), exist_ok=True)

        os.symlink(abs_original, abs_symlink)


class SystemDependent:
    def __init__(self):
        if not self._can_execute():
            raise RuntimeError("This script can't be run in the current platform!")

    @classmethod
    @requires_admin
    def _run_script(cls, terminal: str, script_path: str, args: List[str], sudo: bool = False) -> None:
        sudo_token = 'sudo' if sudo else ''
        args_token = ''
        if args and len(args):
            args_token = ' '.join(args) if len(args) > 1 else args[0]

        script_name = os.path.basename(script_path)
        args_log = f"with args '{args_token}'" if args_token != '' else 'without args'
        logger.info(
            f"Using terminal '{terminal}' to run the script '{script_name}'{' as sudo' if sudo else ''} {args_log}"
        )

        sb.run(f'{sudo_token} {terminal} {script_path}{" " + args_token}', shell=True, stdout=sb.PIPE, check=True)

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
        return cmd_as_bool(f'command -v "{arg}" > /dev/null 2>&1')

    @classmethod
    def execute_sh(cls, script_path: str, args: List[str] = None, sudo=False) -> None:
        cls._run_script('sh', script_path, args, sudo)

    @classmethod
    def execute_bash(cls, script_path: str, args: List[str] = None, sudo=False) -> None:
        cls._run_script('bash', script_path, args, sudo)

    @classmethod
    @requires_admin
    def make_links(cls, links: Dict[str, str]) -> None:
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
                    # os.remove(abs_symlink)
            else:
                logger.info(f"Creating link '{symlink}' -> '{abs_original}'...")
                os.makedirs(os.path.dirname(abs_symlink), exist_ok=True)

            execute_cmd(f'sudo ln -sf "{abs_original}" "{abs_symlink}"')

    @classmethod
    @requires_admin
    def set_login_shell(cls, shell: str) -> None:
        logger.info('Setting up login shell...')
        if cmd_as_bool(f'echo $SHELL | grep --quiet "{shell}"'):
            logger.warn(f'Login shell is already {shell}, skipping...')
        else:
            logger.info(f'Changing login shell to {shell}...')
            Apt.install(shell)
            execute_cmd(f'sudo usermod --shell $(which {shell}) $(whoami)')
        logger.info('Finished setting up login shell!')

    @classmethod
    @requires_admin
    def set_locales(cls, locales: List[str]) -> None:
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
    def set_environment_var(cls, name: str, value: str) -> None:
        from os import environ
        execute_cmd(f'SETX {name.upper()} {value} > NUL')
        environ[name.upper()] = value

    @classmethod
    @requires_admin
    def make_links(cls, links: Dict[str, str]) -> None:
        return _make_links(links)

    @classmethod
    def exists(cls, arg: str) -> bool:
        return cmd_as_bool(f'WHERE /Q "{arg}"')

    @classmethod
    def execute_ps1(cls, script_path: str, args: List[str] = None) -> None:
        cls._run_script('powershell.exe', script_path, args)

    @classmethod
    @requires_admin
    def set_powershell_execution_policy(cls):
        execute_cmd("powershell.exe Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned")

    @classmethod
    @requires_admin
    def set_keyboard_layouts(cls, layouts: List[str]) -> None:
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
            logger.warn(f"Bucket '{bucket_name}' already added, skipping...")
            return

        logger.info(f"Adding bucket '{bucket_name}'...")
        sb.check_call(['scoop', 'bucket', 'add', bucket_name], shell=True)

    @staticmethod
    def change_repo(repo: str) -> None:
        sb.check_call(['scoop', 'config', 'SCOOP_REPO', repo], shell=True)

    @staticmethod
    def clean() -> None:
        sb.check_call(['scoop', 'cleanup', '*'], shell=True)


class Msix(WindowsDependent):
    @staticmethod
    def install(package_path: str, dependencies_paths: List[str] = None) -> None:
        logger.info(f"Installing {os.path.basename(package_path)}...")
        dep_token = ''

        if dependencies_paths:
            dep_token = f' {" ".join(dependencies_paths)}'

        sb.check_call(
            ['powershell.exe', '-c', 'Add-AppxPackage', '-Path', package_path]
            + ['-DependencyPackages', dep_token] if dependencies_paths else [], shell=True)


class Winget(WindowsDependent):
    @staticmethod
    def install(packages_id: List[str]) -> None:
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
        return cmd_as_bool(f'winget list -e --id "{package_id}" > NUL')


class Apt(WslDependent):
    @staticmethod
    @requires_admin  # TODO: is it really?
    def upgrade() -> None:
        sb.check_call(('sudo', 'apt-get', 'upgrade', '-y'))

    @staticmethod
    @requires_admin
    def install(packages: List[str]) -> None:
        sb.check_call(['sudo', 'apt-get', 'install', '-y'] + packages)

    @staticmethod
    @requires_admin
    def update() -> None:
        logger.info('Updating apt references...')
        sb.check_call(('sudo', 'apt-get', 'update'))

    @staticmethod
    @requires_admin  # TODO: is it really?
    def add_repository(repo_name: str) -> None:
        logger.info(f"Adding '{repo_name}' repository to apt...")
        sb.check_call(('sudo', 'add-apt-repository', f'ppa:{repo_name}', '-y'))

    @staticmethod
    def is_repository_added(repo_name: str) -> bool:
        return cmd_as_bool(f'grep -q "^deb .*{repo_name}" /etc/apt/sources.list /etc/apt/sources.list.d/*')


class Dpkg(WslDependent):
    @staticmethod
    @requires_admin
    def install(deb_paths: List[str]) -> None:
        for path in deb_paths:
            sb.check_call(['sudo', 'dpkg', '-i', f'{path}'])
