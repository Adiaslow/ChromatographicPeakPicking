from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class BuildingBlock:
    name: Optional[str] = None
    smiles: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

    def __eq__(self, other):
        if not isinstance(other, BuildingBlock):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
