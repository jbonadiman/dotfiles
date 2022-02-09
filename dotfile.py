#!/usr/bin/env python3
from __future__ import annotations

import inspect
import os.path
import shlex
import subprocess as sb
import sys
from concurrent.futures import ThreadPoolExecutor
from itertools import islice
from pathlib import Path
from queue import Queue, Empty
from typing import Callable

from loguru import logger
from nanoid import generate as gen_id

script_dir = Path(inspect.getframeinfo(inspect.currentframe()).filename).parent

# TODO: only_if, must_have -> depends_on

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


def enqueue_output(file, queue):
    for line in iter(file.readline, ''):
        queue.put(line)
    file.close()


def read_popen_pipes(p):
    with ThreadPoolExecutor(2) as pool:
        q_stdout, q_stderr = Queue(), Queue()
        pool.submit(enqueue_output, p.stdout, q_stdout)
        pool.submit(enqueue_output, p.stderr, q_stderr)

        while True:
            if p.poll() is not None and q_stdout.empty() and q_stderr.empty():
                break

            out_line = err_line = ''
            try:
                out_line = q_stdout.get_nowait()
                err_line = q_stderr.get_nowait()
            except Empty:
                pass

            yield out_line, err_line


def execute_shell(path: Path | None = None, command: str | None = None) -> str | None:
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print("EXECUTANDO", path, 'OU', command)
    if not path and not command:
        return None
    import shlex
    from subprocess import SubprocessError

    args = str(path) if path else shlex.split(command)
    process_desc = ' '.join(args) if type(args) == list else args

    stdout_buffer = []
    stderr_buffer = []
    with sb.Popen(
            args=args,
            stdout=sb.PIPE,
            stderr=sb.PIPE,
            text=True,
            encoding='utf-8',
            cwd=script_dir
    ) as process:
        for out_line, err_line in read_popen_pipes(process):
            if out_line:
                if out_line.endswith('\n'):
                    out_line = out_line.replace('\n', '', 1)
                logger.info("[{} stdout] {}", process_desc, out_line)
                stdout_buffer.append(out_line)
            if err_line:
                if err_line.endswith('\n'):
                    err_line = err_line.replace('\n', '', 1)
                logger.info("[{} stderr] {}", process_desc, err_line)
                stderr_buffer.append(err_line)

        stdout = '\n'.join(stdout_buffer)
        stderr = '\n'.join(stderr_buffer)

        logger.debug('Command result:'
                     "\ncode:\t'{code}'\nargs:\t'{args}'"
                     "\nstdout:\t'{out}'\nstderr:\t'{err}'",
                     code=process.returncode,
                     args=process.args,
                     out=stdout,
                     err=stderr)

        if process.returncode > 0:
            if stderr and "permission" in stderr.lower():
                raise PermissionError(stderr)
            raise SubprocessError(
                f'Command \'{process.args}\' failed '
                f'with return code \'{process.returncode}\' '
                f'and stderr \'{stderr}\'')

    return stdout


def get_shell_function(script_path: str | Path) -> Callable[[None], None]:
    script_path: Path = Path(script_path).expanduser()
    if not script_path.exists():
        return lambda: logger.exception(
            "Shell script '{path}' doesn't exist. Is this the right path?",
            path=script_path
        )
    return lambda: execute_shell(script_path)


def create_link(target: Path, link: Path, use_sudo: bool = False):
    if not target or not link:
        logger.warning('Target and link paths must be provided for symlink creation!')
        return

    logger.info("Creating link '{link}' -> '{target}'", link=link, target=target)
    link.parent.mkdir(parents=True, exist_ok=True)

    command = f"ln --symbolic --force {target} {link}"
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
        only_if: str = ''
        must_have: str = ''
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
                must_have = token['must_have']
            if 'only_if' in token:
                only_if = token['only_if']

            final_token = token['name']
        elif type(token_col) == str:  # for key: value cases
            final_token = token_col
        else:
            final_token = ''

        buffer.append(final_token)
        cmd = shlex.join(buffer)
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(cmd)
        action_dict: dict = {
            'function': lambda: execute_shell(command=cmd)
        }
        if only_if:
            action_dict['only_if'] = only_if
        if must_have:
            action_dict['must_have'] = must_have

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


def execute_section(section: dict, section_name: str = None):
    if section_name:
        actions = parse_actions(section, section_name)
    else:
        actions = parse_actions(section)

    ordered_actions = get_execution_order(actions)

    # calls each action in section
    for action_id in ordered_actions:
        print('#################')
        print(action_id)
        print(actions[action_id]['function'].__dict__)
        actions[action_id]['function']()

    # finished section execution, going to the next one...

    if not section_name and \
            'settings' in section and \
            'sections' in section['settings']:

        for name in sectino['settings']['sections']:
            execute_section(section, name)

def parse_arguments() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument('yaml_path')
    return parser.parse_args()


def main():
    from utils import read_yaml
    import argparse

    logger.enable('dotfile')

    tmpdir: str = ''

    config = {
        'handlers': [
            {
                'sink': sys.stdout,
                'colorize': True,
                'format': '[{time}]: {message}',
                'level': 'DEBUG',
                'diagnose': True
            }
        ]
    }
    logger.configure(**config)
    args = parse_arguments()

    recipe_yaml = read_yaml(args.yaml_path)
    execute_section(recipe_yaml)

if __name__ == '__main__':
    main()

