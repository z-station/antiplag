import os
from os import environ as env
from tempfile import gettempdir

SANDBOX_DIR = env.get('SANDBOX_DIR', gettempdir())
