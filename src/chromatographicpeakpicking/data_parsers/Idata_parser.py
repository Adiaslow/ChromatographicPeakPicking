from abc import ABC, abstractmethod
from dataclasses import dataclass
from pandas import DataFrame

from typing import Generic, TypeVar

from configs.Iconfig import IConfig

ConfigT = TypeVar('ConfigT', bound='IConfig')

@dataclass
class IDataParser(ABC, Generic[ConfigT]):
    @abstractmethod
    def parse_data(self, input_path: str) -> DataFrame:
        raise NotImplementedError
