#!/usr/bin/env python3
from __future__ import annotations

import inspect
import shlex
import subprocess as sb
import sys
import os.path
from itertools import islice
from pathlib import Path
from typing import Callable, Any

from loguru import logger
from nanoid import generate as gen_id

logger.disable('dotfile')
script_dir = Path(inspect.getframeinfo(inspect.currentframe()).filename).parent


def execute_recipe(recipe: dict):
    logger.info(f"Changing working directory to the script's directory...")
    execute_section(recipe)

    if 'settings' in recipe and 'sections' in recipe['settings']:
        for section_name in recipe['settings']['sections']:
            execute_section(recipe[section_name])


def create_file(path: str | Path):
    logger.info('Creating file {path}...', path=path)
    Path(path).touch()


def create_folder(path: str | Path):
    logger.info('Creating folder {path}...', path=path)
    Path(path).mkdir(parents=True)


def get_create_function(path: str | Path) -> Callable[[None], None]:
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


def execute_shell(path: Path | None = None, command: str | None = None) -> Any:
    if not path and not command:
        return
    import shlex
    from subprocess import SubprocessError

    result = sb.run(
        args=str(path) if path else shlex.split(command),
        stdout=sb.PIPE,
        stderr=sb.PIPE,
        shell=True,
        cwd=script_dir)

    logger.debug('Command result:'
                 "\ncode:\t'{code}'\nargs:\t'{args}'"
                 "\nstdout:\t'{out}'\nstderr:\t'{err}'",
                 code=result.returncode,
                 args=result.args,
                 out=result.stdout.decode(),
                 err=result.stderr.decode())
    try:
        result.check_returncode()
        return result.stdout
    except sb.CalledProcessError as exc:
        if result.returncode == 13:
            raise PermissionError(result.stderr, exc)
        raise SubprocessError(
            f'Command \'{" ".join(result.args)}\' failed '
            f'with return code \'{result.returncode}\' '
            f'and stderr \'{result.stderr.decode()}\'')


def get_shell_function(script_path: str | Path) -> Callable[[None], None]:
    script_path: Path = Path(script_path).expanduser()
    if not script_path.exists():
        return lambda: logger.error(
            "Shell script '{path}' doesn't exist. Is this the right path?...",
            path=script_path
        )

    return lambda: logger.info('[Script output] {}', execute_shell(script_path).decode())


def create_link(target: Path, link: Path, use_sudo: bool = False):
    if not target or not link:
        logger.warning('Target and link paths must be provided for symlink creation!')
        return

    logger.info("Creating link '{link}' -> '{target}'", link=link, target=target)
    link.parent.mkdir(parents=True, exist_ok=True)

    command = f"ln -sf {target} {link}"
    if use_sudo:
        command = "sudo " + command

    execute_shell(command=command)
    # link.symlink_to(target)


def get_link_function(target: str | Path, link: str | Path) -> Callable[[None], None]:
    target_path = Path(os.path.expandvars(target)).expanduser().resolve()
    link_path = Path(os.path.expandvars(link)).expanduser()

    if link_path.exists or link_path.is_symlink():
        link_target = link_path.resolve()
        if link_target == target_path:
            return lambda: logger.warning(
                "Link '{}' already exists. Skipping creation...",
                link_path)

        def update_link():
            logger.info(
                "Link '{}' already exists. Updating reference...",
                link_path)
            # link_path.unlink()
            try:
                create_link(target_path, link_path)
            except PermissionError:
                logger.warning("Admin privileges are required to create this link...")
                create_link(target_path, link_path, use_sudo=True)

        return update_link

    if not target_path.exists():
        return lambda: logger.error(
            "Target path '{}' doesn't exist. Is this the right path?",
            target_path
        )

    return lambda: create_link(target_path, link_path)


def get_install_functions(
        token_col: str | dict | list,
        current_id_dict: dict[str, dict[str, Callable[[None], None]] | str],
        buffer: list[str]):
    for token in token_col:
        action_id: str = gen_id()
        action_dict: dict = {}
        if type(token_col) == dict:
            buffer.append(token.strip())
            get_install_functions(
                token_col[token],
                current_id_dict,
                buffer)
            buffer.pop()
            continue
        elif type(token) == str:
            final_token = token
        elif type(token) == dict:
            if 'id' in token:
                if token['id'] in current_id_dict:
                    continue
                action_id = token['id']
            if 'must_have' in token:
                action_dict['must_have'] = token['must_have']
            if 'only_if' in token:
                action_dict['only_if'] = token['only_if']

            final_token = token['name']
        elif type(token_col) == str:  # for key: value cases
            final_token = token_col
        else:
            final_token = ''

        buffer.append(final_token)
        action_dict['function'] = lambda: execute_shell(command=shlex.join(buffer))
        current_id_dict[action_id] = action_dict
        buffer.pop()


def parse_actions(section: dict) -> dict[str, dict[str, Callable[[None], None] | str]]:
    id_dict: dict[str, dict[str, Callable[[None], None] | str]] = {}

    if 'create' in section:
        for action in section['create']:
            path: str = action
            action_id: str = gen_id()
            action_dict: dict = {}

            if type(action) == dict:
                if 'id' in action:
                    # action was already parsed
                    if action['id'] in id_dict:
                        continue
                    action_id = action['id']
                if 'path' in action:
                    path = action['path']
                if 'must_have' in action:
                    action_dict['must_have'] = action['must_have']
                if 'only_if' in action:
                    action_dict['only_if'] = action['only_if']

            action_dict['function'] = get_create_function(path)
            id_dict[action_id] = action_dict

    if 'shell' in section:
        for action in section['shell']:
            script: str = action
            action_id: str = gen_id()
            action_dict: dict = {}

            if type(action) == dict:
                if 'id' in action:
                    # action was already parsed
                    if action['id'] in id_dict:
                        continue
                    action_id = action['id']
                if 'script' in action:
                    script = action['script']
                if 'must_have' in action:
                    action_dict['must_have'] = action['must_have']
                if 'only_if' in action:
                    action_dict['only_if'] = action['only_if']
            action_dict['function'] = get_shell_function(script)
            id_dict[action_id] = action_dict

    if 'links' in section:
        for action in section['links']:
            action_id: str = gen_id()
            action_dict: dict = {}

            if type(action) == dict:
                if 'id' in action:
                    if action['id'] in id_dict:
                        continue
                    action_id = action['id']

                if 'target' in action and 'link' in action:
                    target = action['target']
                    link = action['link']
                else:
                    target, link = list(action.items())[0]

                if 'must_have' in action:
                    action_dict['must_have'] = action['must_have']
                if 'only_if' in action:
                    action_dict['only_if'] = action['only_if']

            action_dict['function'] = get_link_function(target, link)
            id_dict[action_id] = action_dict

    if 'packages' in section:
        get_install_functions(section['packages'], id_dict, [])

    return id_dict


def visit_dependency(
        installation_id: str,
        installation_details: dict[str, dict | str],
        actions: dict[str, dict],
        priorities: dict[str, int],
        dependency_path: list[str]):
    if installation_id not in dependency_path:
        dependency_path.append(installation_id)
    original_id = next(islice(dependency_path, 1))

    if 'only_if' in installation_details:
        opt_dep_id = installation_details['only_if']
        if type(opt_dep_id) == str:
            # only one
            if opt_dep_id not in dependency_path:
                dependency_path.append(opt_dep_id)
            if opt_dep_id in actions:
                priorities[original_id] -= 1
                priorities[installation_id] -= 1
                priorities[opt_dep_id] += 1
                visit_dependency(
                    opt_dep_id,
                    actions[opt_dep_id],
                    actions,
                    priorities,
                    dependency_path)

        elif type(opt_dep_id) == list:
            # multiple dependencies
            for dependency in opt_dep_id:
                if dependency in actions:
                    priorities[original_id] -= 1
                    priorities[installation_id] -= 1
                    priorities[dependency] += 1
                    visit_dependency(
                        dependency,
                        actions[dependency],
                        actions,
                        priorities,
                        dependency_path)
                else:
                    logger.info(
                        "Installation of id '{install_id}' won't be executed, since one of its dependencies (id '{"
                        "dependency_id}') is not present in the recipe...", install_id=installation_id,
                        dependency_id=opt_dep_id)
                    logger.debug("Optional dependency path: {}", ' -> '.join(dependency_path))
                    priorities.pop(installation_id)
                    break

    if 'must_have' in installation_details:
        opt_dep_id = installation_details['must_have']
        if type(opt_dep_id) == str:
            # only one
            if opt_dep_id not in dependency_path:
                dependency_path.append(opt_dep_id)
            if opt_dep_id in actions:
                priorities[original_id] -= 1
                priorities[installation_id] -= 1
                priorities[opt_dep_id] += 10
                visit_dependency(
                    opt_dep_id,
                    actions[opt_dep_id],
                    actions,
                    priorities,
                    dependency_path)

        elif type(opt_dep_id) == list:
            # multiple dependencies
            for dependency in opt_dep_id:
                if dependency in actions:
                    priorities[original_id] -= 1
                    priorities[installation_id] -= 1
                    priorities[dependency] += 10
                    visit_dependency(
                        dependency,
                        actions[dependency],
                        actions,
                        priorities,
                        dependency_path)
                else:
                    logger.error("Installation of id '{install_id}' can't be executed, since one of its dependencies"
                                 " (id '{dependency_id}') is not present in the recipe. Check the recipe for any"
                                 " missing installs!",
                                 install_id=installation_id,
                                 dependency_id=opt_dep_id)
                    logger.debug("Required dependency path: {}", ' -> '.join(dependency_path))
                    priorities.pop(installation_id)

    dependency_path.pop()


def get_execution_order(
        actions: dict[str, dict[str, Callable[[None], None] | str]]
) -> list[str]:
    priorities = {action_id: 0 for action_id in actions}

    for action_id, action in actions.items():
        visit_dependency(
            action_id,
            action,
            actions,
            priorities,
            []
        )

    return [k for k, _ in sorted(priorities.items(), key=lambda item: item[1], reverse=True)]


def execute_section(section: dict):
    actions = parse_actions(section)
    ordered_actions = get_execution_order(actions)

    for action_id in ordered_actions:
        actions[action_id]['function']()


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

    recipe_file = read_yaml('./linux_recipe.yaml')

    execute_recipe(recipe_file)
