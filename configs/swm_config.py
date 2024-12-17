from dataclasses import dataclass

from configs.Iconfig import IConfig

@dataclass
class SWMConfig(IConfig):
    """Configuration for Sliding Window Minimum baseline correction."""
    window_length: int = 3
    padding_mode: str = 'edge'
