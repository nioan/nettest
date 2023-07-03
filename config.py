import os

import yaml
from dotenv import load_dotenv


def read_nettest_config():
    load_dotenv()
    script_dir = os.path.dirname(os.path.realpath(__file__))
    default_config_file = os.path.join(script_dir, 'nettest.conf.yaml')
    # Get the file path from the environment variable
    config_file = os.getenv('NETTEST_CONF', default_config_file)

    # Expand the user path (~) if present
    config_file = os.path.expanduser(config_file)
    if not os.path.isfile(config_file):
        print(f'Config file {config_file} not found')
        return {}

    # Read the YAML file
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    return config
