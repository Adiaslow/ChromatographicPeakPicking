# src/chromatographicpeakpicking/config/global_config.py
from dataclasses import dataclass, field

@dataclass
class GlobalConfig:
    debug: bool = field(default=False)
    # Add other global configuration parameters as needed

    def __post_init__(self):
        # Initialize any other config settings here if needed
        pass
