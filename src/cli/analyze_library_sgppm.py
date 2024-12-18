import argparse
import numpy as np
from tqdm import tqdm
from core.chromatogram import Chromatogram
from data_parsers.tabular_data_parser import TabularDataParser
from peak_pickers.sgppm import SGPPM
from utilities.process_sequence_count_chromatogram_data import process_sequence_count_chromatogram_data

def main():
    parser = argparse.ArgumentParser(description='Analyze library')
    parser.add_argument('input_path', type=str, help='Path to input file')
    parser.add_argument('output_path', type=str, help='Path to output file')
    args = parser.parse_args()

    data_parser = TabularDataParser()
    print(f'Parsing data from {args.input_path}')
    cleaned_data = data_parser.parse_data(args.input_path)

    peak_picker = SGPPM()
    print('Analyzing library')

    for index, row in tqdm(cleaned_data.iterrows(), total=len(cleaned_data), desc='Analyzing library', unit='compound'):
        try:
            x, y = process_sequence_count_chromatogram_data(row['All Datapoints'])
            building_blocks = data_parser.config.building_block_columns.values()

            chrom = Chromatogram(
                x=x,
                y=y,
                building_blocks=building_blocks
            )
            chrom = peak_picker.pick_peaks(chrom)

            # Safer way to handle the picked peak time
            retention_time = None
            if chrom.picked_peak is not None:
                retention_time = chrom.picked_peak['time']
                if retention_time is np.nan:
                    retention_time = None

            cleaned_data.at[index, 'Retention Time'] = retention_time

        except Exception as e:
            print(f"Error processing row {index}: {str(e)}")
            cleaned_data.at[index, 'Retention Time'] = None
            continue

    cleaned_data.to_csv(args.output_path, index=False)

if __name__ == '__main__':
    main()
