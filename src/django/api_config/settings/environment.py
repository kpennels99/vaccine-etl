"""
Execution environment related settings.

The environment variable reader (env)  is instantiated in this module and then
imported into the other settings definition files.
"""
import os

import environ


env = environ.Env(DEBUG=(bool, False))

CURRENT_PATH = environ.Path(__file__) - 1
SITE_ROOT = CURRENT_PATH - 2
env_file = SITE_ROOT(".env")

if os.path.exists(env_file):
    environ.Env.read_env(env_file=env_file)
else:
    print("No env file found")
