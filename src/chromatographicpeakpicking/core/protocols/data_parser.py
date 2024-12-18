from abc import ABC, abstractmethod
from dataclasses import dataclass
from pandas import DataFrame

from typing import Generic, TypeVar

from . import Config

ConfigT = TypeVar('ConfigT', bound='Config')

@dataclass
class DataParser(ABC, Generic[ConfigT]):
    @abstractmethod
    def parse_data(self, input_path: str) -> DataFrame:
        raise NotImplementedError
