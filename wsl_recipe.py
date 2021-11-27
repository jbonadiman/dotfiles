#!/usr/bin/env python3

import tempfile

from dotfile import Wsl, Apt, Dpkg
from dotfile import abs_path
from dotfile import logger


apt = Apt()
dpkg = Dpkg()
wsl = Wsl()


# TODO: read from file
apt_pkgs = [
    'httpie',
    'clang',
    'exa',
    'make'
]

login_shell = 'zsh'
locales = [
    'pt_BR',
    'pt_BR.utf8'
]

folders = [
    '~/.local/bin'
]

links = {
    '~/.vimrc': 'vimrc',
    '~/.zshrc': 'zshrc',
    '~/.zshenv': 'zshenv',
    '~/.docker_service.zsh': 'docker_service.zsh',
    '/etc/wsl.conf': 'wsl.conf'
}


def install_bat_fn() -> None:
    import os.path
    from dotfile import download_file

    bat_url = 'https://github.com/sharkdp/bat/releases/download/v0.18.3/bat_0.18.3_amd64.deb'
    bat_deb_path = os.path.join(tmpdir, os.path.basename(bat_url))
    download_file(bat_url, bat_deb_path)
    dpkg.install([bat_deb_path])


def install_rust_fn() -> None:
    import os.path
    from dotfile import download_file

    rust_installer = os.path.join(tmpdir, 'rust_installer.sh')
    download_file('https://sh.rustup.rs', rust_installer)
    wsl.execute_sh(rust_installer, ['-y'])


def install_bat_extras_fn() -> None:
    import os.path
    from dotfile import git_clone

    bat_extras_dir = os.path.join(tmpdir, 'bat-extras')
    git_clone('https://github.com/eth-p/bat-extras', bat_extras_dir)
    wsl.execute_bash(os.path.join(bat_extras_dir, 'build.sh'), ['--install'], sudo=True)


def install_n_fn() -> None:
    import os.path
    from dotfile import download_file

    n_installer = os.path.join(tmpdir, 'n_install')
    download_file(r'https://git.io/n-install', n_installer)
    os.chmod(n_installer, 0o755)
    wsl.execute_bash(n_installer, ['-y'])


def install_vundle():
    import os.path
    from dotfile import git_clone

    vundle_path = abs_path('~/.vim/bundle/Vundle.vim')
    if os.path.isdir(vundle_path):
        logger.warn('Vundle already installed, skipping...')
    else:
        logger.info('Installing Vundle...')
        git_clone('https://github.com/VundleVim/Vundle.vim.git', vundle_path)
        logger.info('Finished installing Vundle!')


if __name__ == '__main__':
    from dotfile import create_folders
    from dotfile import make_links
    from shutil import rmtree

    logger.info('Running WSL recipe...', True)
    tmpdir = tempfile.mkdtemp(prefix='wsl_recipe')

    try:
        create_folders(folders)
        logger.info('Finished creating folders!', True)

        make_links(links)
        logger.info('Finished creating symlinks!', True)

        wsl.set_login_shell(login_shell)
        exa_repo = 'spvkgn/exa'
        if apt.is_repository_added(exa_repo):
            logger.warn('exa repository already added, skipping...')
        else:
            apt.add_repository(exa_repo)
            apt.update()

        wsl.set_locales(locales)
        logger.info('Finished setups!', True)

        apt.install(apt_pkgs)
        install_vundle()
        wsl.install('bat', install_bat_fn)
        wsl.install('rustup', install_rust_fn)
        wsl.install('batman', install_bat_extras_fn, alias='bat-extras')
        wsl.install('n', install_n_fn)
        logger.info('Finished installing packages!', True)
    finally:
        rmtree(tmpdir)
