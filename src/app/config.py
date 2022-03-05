# TODO лишний импорт
import os
from os import environ as env
from tempfile import gettempdir

# TODO название переменной не очень отражает ее цель
SANDBOX_DIR = env.get('SANDBOX_DIR', gettempdir())
