#!/usr/bin/env python3

import tempfile

from dotfile import Wsl, Apt, Dpkg
from dotfile import abs_path
from dotfile import logger
from dotfile import requires_admin

apt = Apt()
dpkg = Dpkg()
wsl = Wsl()


# TODO: read from file
apt_pkgs = [
    'httpie',
    'clang',
    'exa',
    'make',
]

login_shell = 'zsh'
locales = [
    'pt_BR',
    'pt_BR.utf8'
]

folders = [
    f'{wsl.HOME}/.local/bin'
]

links = {
    f'{wsl.HOME}/.vimrc': 'vimrc',
    f'{wsl.HOME}/.zshrc': 'zshrc',
    f'{wsl.HOME}/.zshenv': 'zshenv',
    f'{wsl.HOME}/.docker_service.zsh': 'docker_service.zsh',
    '/etc/wsl.conf': 'wsl.conf',
    f'{wsl.HOME}/sources': '$USERPROFILE/sources'
}


def install_bat() -> None:
    import os.path
    from dotfile import download_file

    bat_url = 'https://github.com/sharkdp/bat/releases/download/v0.18.3/bat_0.18.3_amd64.deb'
    bat_deb_path = os.path.join(tmpdir, os.path.basename(bat_url))
    download_file(bat_url, bat_deb_path)
    dpkg.install([bat_deb_path])


def install_rust() -> None:
    import os.path
    from dotfile import download_file

    rust_installer = os.path.join(tmpdir, 'rust_installer.sh')
    download_file('https://sh.rustup.rs', rust_installer)
    wsl.execute_sh(rust_installer, ['-y'])


def install_bat_extras() -> None:
    import os.path
    from dotfile import git_clone

    bat_extras_dir = os.path.join(tmpdir, 'bat-extras')
    git_clone('https://github.com/eth-p/bat-extras', bat_extras_dir)
    wsl.execute_bash(os.path.join(bat_extras_dir, 'build.sh'), ['--install'], sudo=True)


def install_n() -> None:
    import os.path
    from dotfile import download_file

    n_installer = os.path.join(tmpdir, 'n_install')
    download_file(r'https://git.io/n-install', n_installer)
    os.chmod(n_installer, 0o755)
    wsl.execute_bash(n_installer, ['-y'])


def install_vundle():
    import os.path
    from dotfile import git_clone
    import subprocess as sb

    vundle_path = abs_path(f'{wsl.HOME}/.vim/bundle/Vundle.vim')
    if os.path.isdir(vundle_path):
        logger.warn('Vundle already installed, skipping...')
    else:
        logger.info('Installing Vundle...')
        git_clone('https://github.com/VundleVim/Vundle.vim.git', vundle_path)
        logger.info('Finished installing Vundle!')
    logger.info('Installing vim plugins...')
    sb.run('vim -esn -c PluginInstall -c q', shell=True)


def install_shfmt():
    from dotfile import execute_cmd
    execute_cmd('go get mvdan.cc/sh/v3/cmd/shfmt@latest')


@requires_admin
def install_go():
    from dotfile import download_file, execute_cmd
    import os.path

    go_url = 'https://go.dev/dl/go1.17.3.linux-amd64.tar.gz'
    go_archive = os.path.join(tmpdir, os.path.basename(go_url))

    download_file(go_url, go_archive)
    logger.info('Extracting go files...')
    execute_cmd(f'sudo tar -C /usr/local -xzf {go_archive}')
    os.makedirs(os.path.join(wsl.HOME, '.go'), exist_ok=True)

    logger.info('Registering go command...')
    execute_cmd(f'sudo update-alternatives --install "/usr/bin/go" "go" "/usr/local/go/bin/go" 0 > /dev/null')
    execute_cmd(f'sudo update-alternatives --set go /usr/local/go/bin/go > /dev/null')


if __name__ == '__main__':
    from dotfile import create_folders
    from shutil import rmtree

    logger.info('Running WSL recipe...', True)
    tmpdir = tempfile.mkdtemp(prefix='wsl_recipe')

    try:
        create_folders(folders)
        logger.info('Finished creating folders!', True)

        wsl.make_links(links)
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

        wsl.install('go', install_go)
        wsl.install('shfmt', install_shfmt)
        wsl.install('bat', install_bat)
        wsl.install('rustup', install_rust)
        wsl.install('batman', install_bat_extras, alias='bat-extras')
        wsl.install('n', install_n)
        logger.info('Finished installing packages!', True)
    finally:
        rmtree(tmpdir)
