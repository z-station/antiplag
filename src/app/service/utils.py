import os
import uuid
from app.service.enums import Lang
from app.config import TEMP_DIR


class PlagFile:

    """ Описывает файлы, используемые детектором плагиата SIM для
    проверки исходного кода задач на наличие в нем плагиата. """

    def __init__(self, code: str, lang: str):
        if lang == Lang.CPP:
            self.filename = f'{uuid.uuid4()}.cpp'
        elif lang == Lang.JAVA:
            self.filename = f'{uuid.uuid4()}.java'
        elif lang == Lang.PASCAL:
            self.filename = f'{uuid.uuid4()}.pas'
        self.filepath = os.path.join(TEMP_DIR, self.filename)
        with open(self.filepath, 'w') as file:
            file.write(code)
            file.close()

    def remove(self):
        os.remove(self.filepath)
