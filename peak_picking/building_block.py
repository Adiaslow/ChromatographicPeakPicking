from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class BuildingBlock:
    name: Optional[str] = None
    smiles: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
