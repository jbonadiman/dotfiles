#!/usr/bin/env python3

from pathlib import Path

import yaml

from dotfile import execute_section

yaml_path = Path('./test.yaml')

with yaml_path.open('r') as file:
    yaml_content = yaml.safe_load(file)

execute_section(yaml_content['essential'])
