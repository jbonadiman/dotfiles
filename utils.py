from __future__ import annotations

import os
import os.path
import subprocess as sp
from collections import deque
from functools import wraps
from typing import Generator, Callable, Any

import requests

import log

logger = log.get_logger()


def git_clone(url: str, path: str | None):
    alt_path = f' "{path}"' or ''
    sp.run(f'git clone -q "{url}"{alt_path}'.strip(), shell=True, stdout=sp.PIPE)


def download_file(url: str, path: str):
    logger.info(f"Downloading file '{os.path.dirname(url)}'...")
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


def execute_cmd(command: str, stderr: bool = False) -> Any:
    return sp.check_output(
        command,
        shell=True,
        stderr=sp.DEVNULL if not stderr else None
    )


def cmd_as_bool(command: str) -> bool:
    result = execute_cmd(
        f'{command} && echo 1 || echo 0',
        stderr=False
    )
    return bool(int(result))


def read_yaml(path: str) -> dict:
    import yaml

    yaml_content: dict
    with open(path, 'r') as stream:
        try:
            yaml_content = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.error(str(exc))
    return yaml_content


def exhaust(generator: Generator):
    deque(generator, maxlen=0)


def requires_admin(fn: Callable):
    @wraps(fn)
    def wrapped_f(*args, **kwargs):
        logger.info(f"Using administrative privileges to '{fn.__qualname__}'...")
        try:
            return fn(*args, **kwargs)
        except (OSError, PermissionError) as err:
            if err.errno == 13 or (hasattr(err, 'winerror') and err.winerror == 1314):
                logger.error(f"Administrative privileges are required to {fn.__qualname__}\n"
                             f'ARGUMENTS: {args} {kwargs}')
            else:
                raise err

    return wrapped_f


@requires_admin
def create_folders(paths: list[str]):
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
def _make_links(links: dict[str, str]):
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
