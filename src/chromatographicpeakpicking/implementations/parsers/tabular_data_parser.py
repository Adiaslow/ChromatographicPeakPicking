from dataclasses import dataclass, field
import pandas as pd
from pandas import DataFrame
from configs.tabular_data_parser_config import TabularDataParserConfig
from data_parsers.Idata_parser import IDataParser

@dataclass
class TabularDataParser(IDataParser[TabularDataParserConfig]):
    config: TabularDataParserConfig = field(default_factory=TabularDataParserConfig)

    def parse_data(
        self,
        input_path: str
    ) -> DataFrame:
        raw_df = self._get_raw_dataframe(input_path)
        return self._clean_dataframe(raw_df)

    def _get_raw_dataframe(
        self,
        input_path: str
    ) -> DataFrame:
        if input_path is None:
            raise ValueError("Input path is None")
        if not isinstance(input_path, str):
            raise ValueError("Input path must be a string")

        if input_path.endswith('.csv'):
            return pd.DataFrame(pd.read_csv(input_path))
        elif input_path.endswith('.xlsx'):
            # Using explicit sheet name that worked in previous code
            return pd.read_excel(input_path, sheet_name='Sheet1')

        raise ValueError("Input file must be a CSV or Excel file")

    def _clean_dataframe(self, raw_df: DataFrame) -> DataFrame:
        building_block_columns = list(self.config.building_block_columns.values())
        columns = [
            self.config.lid_column,
            self.config.common_name_column,
            self.config.scaffold_column,
            self.config.smiles_column,
            self.config.raw_data_column,
            *building_block_columns,
        ]
        # Get only the columns we need
        clean_df = raw_df[columns]
        clean_df = clean_df[clean_df['lid'] == self.config.lid_to_process]

        # Rename columns
        column_mappings = {
            self.config.lid_column: 'LID',
            self.config.common_name_column: 'Name',
            self.config.scaffold_column: 'Scaffold',
            self.config.smiles_column: 'SMILES',
            self.config.raw_data_column: 'All Datapoints'
        }

        # Rename the base columns
        clean_df.rename(columns=column_mappings, inplace=True)

        # Rename building block columns
        for i, column in enumerate(building_block_columns):
            clean_df.rename(columns={column: f'Building Block {i + 1}'}, inplace=True)

        # Add column for retention time
        clean_df['Retention Time'] = None
        return clean_df
