from typing import Dict, Type
from src.chromatographicpeakpicking.core.protocols.configurable import Configurable
from src.chromatographicpeakpicking.core.types.config import BaseConfig
from src.chromatographicpeakpicking.core.types.validation import ValidationResult

class ConfigManager:
    def __init__(self):
        self.components: Dict[str, Configurable] = {}

    def register_component(self, name: str, component: Configurable):
        self.components[name] = component

    def configure_component(self, name: str, config: BaseConfig) -> ValidationResult:
        component = self.components.get(name)
        if component:
            return component.configure(config)
        else:
            return ValidationResult(is_valid=False, messages=[f"Component '{name}' not found."])

    def get_component_metadata(self, name: str):
        component = self.components.get(name)
        if component:
            return component.get_metadata()
        else:
            return None
