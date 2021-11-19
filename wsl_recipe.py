from dotfile import Apt
from dotfile import \
    abs_path, \
    create_folder, \
    make_link, \
    exists
import tempfile
import shutil

# tempdir = tempfile.mkdtemp(prefix='wsl_recipe')

try:
    if exists('qualquer coisa'):
        print("Opa")
finally:
    pass
    # shutil.rmtree(tempdir)
