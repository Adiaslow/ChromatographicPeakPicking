import numpy as np

from ..peak_picking.building_block import BuildingBlock
from ..peak_picking.chromatogram import Chromatogram
from ..peak_picking.process_sequence_count_chromatogram_data import process_chromatography_data
from ..peak_picking.sgppm import SimpleGaussianPeakPickingModel

def test_sgppm_single_compound():
    data = "945.00:105;71, 3045.00:2;2, 2385.00:4;3, 2235.00:6;4, 2745.00:3;2, 2895.00:4;2, 1995.00:7;6, 885.00:72;38, 1695.00:6;5, 2685.00:2;2, 3315.00:16;3, 3390.00:3;1, 3510.00:4;2, 2295.00:7;6, 1365.00:8;8, 1425.00:40;27, 3105.00:5;4, 1305.00:40;28, 2145.00:4;3, 1875.00:6;6, 975.00:52;39, 915.00:190;128, 1455.00:22;14, 1725.00:5;4, 1635.00:14;8, 2355.00:2;2, 825.00:77;45, 2085.00:9;6, 1215.00:220;140, 3255.00:9;4, 3075.00:3;1, 3225.00:13;4, 3165.00:4;2, 2715.00:5;3, 735.00:33;21, 645.00:26;21, 2265.00:11;6, 2055.00:1;1, 2565.00:3;3, 1065.00:221;158, 1605.00:12;10, 2445.00:3;3, 1935.00:8;6, 2775.00:4;2, 1905.00:6;4, 1545.00:9;8, 2655.00:4;3, 2805.00:8;4, 855.00:27;21, 1125.00:148;100, 1035.00:191;134, 1665.00:11;8, 2865.00:6;4, 1095.00:279;182, 765.00:28;18, 3015.00:2;2, 1275.00:91;68, 1815.00:8;6, 2205.00:16;7, 3450.00:6;2, 1155.00:98;73, 675.00:23;17, 795.00:51;34, 3195.00:3;2, 2505.00:5;5, 2535.00:1;1, 615.00:30;18, 1755.00:4;3, 1515.00:16;12, 1485.00:12;11, 1245.00:248;162, 2475.00:10;6, 1575.00:28;16, 2115.00:4;3, 705.00:23;8, 1005.00:118;76, 2325.00:2;1, 1185.00:86;60, 2625.00:2;1, 1335.00:23;18, 1395.00:29;23, 2175.00:2;1, 3570.00:4;2, 2985.00:1;1, 1785.00:9;8, 2595.00:5;3, 2955.00:3;1, 2025.00:7;5, 1965.00:9;6, 3135.00:9;1, 2415.00:7;4, 2835.00:4;2, 3345.00:1;1, 3285.00:5;1, 1845.00:6;5"

    data = data.replace(";", ":")


    # Replace semicolons with colons to standardize separators
    data = data.replace(";", ":")

    # Get sorted times and intensities
    times, intensities = process_chromatography_data(data)

    # Create the numpy arrays
    times_array = times
    intensities_array = intensities
    building_blocks = ['DVal', 'DβHomoleu', 'DβHomoleu']

    print(f"Building Blocks: {building_blocks}")

    building_blocks = [
        BuildingBlock(name=building_blocks[0]),
        BuildingBlock(name=building_blocks[1]),
        BuildingBlock(name=building_blocks[2])
    ]

    _chromatogram = Chromatogram(
        x=times_array,
        y=intensities_array,
        building_blocks=building_blocks,
    )


    peak_picking_model = SimpleGaussianPeakPickingModel()

    _chromtogram = peak_picking_model.pick_peaks(chromatograms=_chromatogram)

    return _chromatogram
