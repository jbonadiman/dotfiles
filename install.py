#!/usr/bin/env python3

import os
import os.path

class ansi_colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


folders = (
    '~/sources',
    '~/.local/bin'
)

links = {
    "~/.zshrc": "./wsl/zshrc",
    "~/.zshenv": "./wsl/zshenv",
    "~/.vimrc": "./wsl/vimrc",
    "~/.docker_service.zsh": "./wsl/docker_service.zsh",
}

scripts = (
    ''
)

def warn(message: str, is_result: bool=False) -> None:
    formatted_msg = f'{ansi_colors.WARNING}{message}{ansi_colors.ENDC}'
    print(f'{ansi_colors.UNDERLINE}{formatted_msg}' if is_result else formatted_msg)

def info(message: str, is_result: bool=False) -> None:
    formatted_msg = f'{ansi_colors.OKCYAN}{message}{ansi_colors.ENDC}'
    print(f'{ansi_colors.UNDERLINE}{formatted_msg}' if is_result else formatted_msg)

def error(message: str) -> None:
    print(f'{ansi_colors.BOLD}{ansi_colors.FAIL}An error occurred:\n{message}{ansi_colors.ENDC}')

def abs_path(path: str) -> str:
    return os.path.abspath(
        os.path.expandvars(
            os.path.expanduser(path)
        )
    )

def create_folders() -> None:
    all_successful = True
    try:
        for folder_path in folders:
            as_absolute = abs_path(folder_path)
            if os.path.exists(as_absolute):
                info(f"'{folder_path}' folder already exists. Skipping...")
                all_successful = False
                continue

            info(f"Creating folder '{folder_path}'...")
            os.makedirs(as_absolute, exist_ok=True)
    except Exception as e:
        all_successful = False
        error(str(e))
    finally:
        if all_successful:
            info("All folders created successfully", is_result=True)
        else:
            warn("Not all folders could be created", is_result=True)

def create_links() -> None:
    all_successful = True
    try:
        for dst, src in links.items():
            abs_dst = abs_path(dst)
            abs_src = abs_path(src)

            if not os.path.exists(abs_src):
                info(f"Origin '{src}' does not exist. Skipping...")
                all_successful = False
                continue

            if os.path.exists(abs_dst):
                if os.path.islink(abs_dst):
                    if os.readlink(abs_dst) == abs_src:
                        info(f"Link '{dst}' -> '{src}' already exists. Skipping...")
                        all_successful = False
                        continue
                    else:
                        info(f"Link exists, but it is outdated. Updating to '{dst}' -> '{abs_src}'...")
                        os.remove(abs_dst)
                        os.symlink(abs_src, abs_dst)
                        continue
                info(f"Destination '{dst}' already exists. Skipping...")
                all_successful = False
                continue

            info(f"Creating link '{dst}' -> '{abs_src}'...")
            os.symlink(abs_src, abs_dst)

    except Exception as e:
        error(str(e))
    finally:
        if all_successful:
            info('All links created or updated successfully', is_result=True)
        else:
            warn('Not all links could be created or updated', is_result=True)


def execute_scripts() -> None:
    pass

if __name__ == '__main__':
    create_folders()
    create_links()
