from abc import ABC
from dataclasses import dataclass

@dataclass
class IConfig(ABC):
    """Abstract class for configuration objects."""
    pass
