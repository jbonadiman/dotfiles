import os
import os.path
import shutil
import tempfile

from dotfile import Apt
from dotfile import Dpkg
from dotfile import Ubuntu
from dotfile import \
    create_folder, \
    make_link, \
    download_installer, \
    git_clone, \
    install, \
    cmd_as_bool, \
    execute_cmd, \
    abs_path

apt = Apt()
dpkg = Dpkg()

print('Installing essential packages...')
tmpdir = tempfile.mkdtemp(prefix='wsl_recipe')

# TODO: read from file
apt_pcks = (
    'httpie',
    'clang',
    'exa',
    'make'
)

folders = (
    '~/.local/bin'
)

links = {
    '~/.vimrc': 'vimrc',
    '~/.zshrc': 'zshrc',
    '~/.zshenv': 'zshenv',
    '~/.docker_service.zsh': 'docker_service.zsh'
}


def install_bat_fn() -> None:
    bat_url = r'https://github.com/sharkdp/bat/releases/download/v0.18.3/bat_0.18.3_amd64.deb'
    bat_deb_path = os.path.join(tmpdir, 'bat_0.18.3_amd64.deb')
    download_installer(bat_url, bat_deb_path)
    dpkg.install_packages(bat_deb_path)


def install_rust_fn() -> None:
    rust_installer = os.path.join(tmpdir, 'rust_installer.sh')
    download_installer(r'https://sh.rustup.rs', rust_installer)
    Ubuntu.execute_sh(rust_installer, ['--', '-y'])


def install_bat_extras_fn() -> None:
    bat_extras_dir = os.path.join(tmpdir, 'bat-extras')
    git_clone('https://github.com/eth-p/bat-extras', bat_extras_dir)
    Ubuntu.execute_bash(os.path.join(bat_extras_dir, 'build.sh'), ['--install'], sudo=True)


def install_n_fn() -> None:
    n_installer = os.path.join(tmpdir, 'n_install')
    download_installer(r'https://git.io/n-install', n_installer)
    os.chmod(n_installer, 0o755)
    Ubuntu.execute_bash(n_installer, ['-y'])


def setup_login_shell():
    default_shell = 'zsh'

    if cmd_as_bool(f'echo $SHELL | grep --quiet "{default_shell}"'):
        print(f'Login shell is already {default_shell}, skipping...')
    else:
        print(f'Changing login shell to {default_shell}...')
        execute_cmd(f'sudo usermod --shell $(which {default_shell}) $(whoami)')


def setup_locales():
    should_be_installed = (
        'pt_BR',
        'pt_BR.utf8'
    )

    must_install = []

    print("Setting up locales...")

    import locale
    for localization in should_be_installed:
        try:
            locale.setlocale(locale.LC_ALL, localization)
            print(f"Locale '{localization}' is already installed, skipping...")
        except locale.Error:
            must_install.append(localization)

    if len(must_install) > 0:
        print('Installing missing locales...')
        execute_cmd(f'sudo locale-gen {" ".join(must_install)}; sudo update-locale')
        print('Done!')

    locale.setlocale(locale.LC_ALL, '')


def setup_vundle():
    vundle_path = abs_path('~/.vim/bundle/Vundle.vim')
    if os.path.isdir(vundle_path):
        print('Vundle already installed, skipping...')
    else:
        print('Installing Vundle...')
        git_clone('https://github.com/VundleVim/Vundle.vim.git', vundle_path)
        print('Done!')


if __name__ == '__main__':
    try:
        list(map(create_folder, folders))

        for symlink, original in links.items():
            make_link(original, symlink)

        setup_login_shell()

        exa_repo = 'spvkgn/exa'
        if apt.is_repository_added(exa_repo):
            print('exa repository already added, skipping...')
        else:
            print('Adding exa repository to apt...')
            apt.add_repository(exa_repo)
            apt.update()

        print('Installing apt packages...')
        apt.install_packages(*apt_pcks)

        install('bat', install_bat_fn)
        install('rustup', install_rust_fn)
        install('batman', install_bat_extras_fn, alias='bat-extras')
        install('n', install_n_fn)

        setup_locales()
        setup_vundle()
    finally:
        shutil.rmtree(tmpdir)
