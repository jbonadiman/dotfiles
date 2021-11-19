from dotfile import Apt
from dotfile import \
    abs_path, \
    create_folder, \
    make_link
import tempfile
import shutil

tempdir = tempfile.mkdtemp(prefix='wsl_recipe')

try:
    apt = Apt()
    

finally:
    shutil.rmtree(tempdir)
