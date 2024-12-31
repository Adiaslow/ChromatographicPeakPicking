from dataclasses import dataclass, field
from typing import Dict
from configs.Iconfig import IConfig

@dataclass
class TabularDataParserConfig(IConfig):
    """Configuration for data parser."""
    null_building_block: str = 'Null'
    excel_sheet: str = 'Sheet1'
    building_block_columns: Dict[str, str] = field(
        default_factory=lambda: {
            'building_block1': 'BB1 Name',
            'building_block2': 'BB2 Name',
            'building_block3': 'BB3 Name'
        }
    )
    lid_column: str = 'lid'
    lid_to_process: str = 'DEL-0045'
    scaffold_column: str = 'All Stereochem (N-->C)'
    common_name_column: str = 'Common_Name (N-->C)'
    smiles_column: str = 'enumerated_smiles'
    raw_data_column: str = 'all_datapoints'
