from __future__ import annotations

import os
import os.path
import subprocess as sp
from collections import deque
from functools import wraps
from typing import Generator, Callable, Any

import requests
import loguru


def read_yaml(path: str) -> dict:
    import yaml

    yaml_content: dict
    with open(path, 'r') as stream:
        try:
            yaml_content = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.exception(str(exc))
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
                logger.exception(f"Administrative privileges are required to {fn.__qualname__}\n"
                             f'ARGUMENTS: {args} {kwargs}')
            else:
                raise err

    return wrapped_f

