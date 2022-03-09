from os import environ as env
from tempfile import gettempdir

TEMP_DIR = env.get('TEMP_DIR', gettempdir())
