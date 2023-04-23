import abc
import json
import os
from typing import Optional

from logger import log


log = log.getChild(__name__)


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        pass

    @abc.abstractmethod
    def check_or_create(self) -> None:
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def check_or_create(self) -> None:
        try:
            with open(self.file_path, 'r') as f:
                pass
        except FileNotFoundError:
            log.info(f'State .json file not found by path <workdir>/{self.file_path}')
            log.info(f'Creating empty <workdir>/{self.file_path}')
            with open(self.file_path, 'w') as f:
                pass

    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        self.check_or_create()
        with open(self.file_path, 'w+') as fp:
            json.dump(state, fp)

    def retrieve_state(self) -> dict | None:
        """Загрузить состояние локально из постоянного хранилища"""
        self.check_or_create()
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'r') as f:
                file_data = f.read()
                if not file_data:
                    return {}
                try:
                    return json.loads(file_data)
                except Exception:
                    return
