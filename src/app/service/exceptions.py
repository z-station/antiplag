# TODO до тех пор пока нет эксцепшнов которые ты обрабатываешь
#  в сервисе лучше удалить этот неиспользуемый код
from typing import Optional, Any
from app.service import messages


class ServiceException(Exception):

    default_message = None

    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Any] = None
    ):
        self.message = message or self.default_message
        self.details = details
        super().__init__(self.message)