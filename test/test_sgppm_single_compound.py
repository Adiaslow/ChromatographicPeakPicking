from ..peak_picking.building_block import BuildingBlock
from ..peak_picking.chromatogram import Chromatogram
from ..peak_picking.process_sequence_count_chromatogram_data import process_chromatography_data
from ..peak_picking.sgppm import SimpleGaussianPeakPickingModel


test_data = {
    'test_1': {
        'data': "1815.00:42;30, 3255.00:16;6, 2835.00:20;12, 3570.00:10;7, 3345.00:17;8, 3315.00:26;11, 1485.00:36;26, 675.00:255;178, 2865.00:15;7, 2115.00:30;19, 1725.00:29;23, 945.00:238;172, 1335.00:56;45, 2175.00:15;9, 2265.00:15;12, 2595.00:18;12, 2715.00:7;5, 1005.00:195;139, 1425.00:43;31, 825.00:280;189, 1905.00:18;11, 1785.00:49;31, 2775.00:32;15, 3105.00:9;8, 1665.00:32;23, 855.00:266;182, 1635.00:26;24, 2955.00:9;5, 1845.00:13;12, 1125.00:133;97, 2355.00:20;14, 2205.00:17;15, 615.00:308;230, 1275.00:135;106, 885.00:266;152, 1575.00:48;31, 2565.00:13;10, 2625.00:12;7, 2055.00:16;15, 1455.00:42;34, 1545.00:35;26, 765.00:265;178, 2235.00:16;12, 1935.00:19;15, 1515.00:30;24, 1245.00:176;126, 1695.00:31;21, 2385.00:16;12, 2325.00:19;14, 1185.00:112;84, 1755.00:21;19, 3390.00:4;3, 1155.00:159;100, 2805.00:16;8, 1095.00:106;72, 1305.00:108;81, 3450.00:4;2, 2895.00:13;9, 1395.00:32;22, 3045.00:18;6, 705.00:326;212, 1215.00:112;82, 2745.00:6;5, 2025.00:12;12, 3015.00:21;14, 1995.00:17;15, 2985.00:8;6, 915.00:159;113, 645.00:259;193, 2445.00:11;9, 2145.00:11;10, 2295.00:19;13, 1965.00:23;16, 3195.00:24;9, 3135.00:7;5, 2475.00:10;7, 3510.00:13;7, 2685.00:24;13, 1065.00:113;89, 2085.00:12;9, 1875.00:34;21, 3285.00:26;8, 2415.00:10;9, 735.00:253;169, 975.00:251;189, 3165.00:11;6, 795.00:245;163, 2925.00:15;11, 1035.00:140;97, 2655.00:11;9, 1605.00:21;19, 2505.00:22;14, 1365.00:44;33, 2535.00:17;10, 3225.00:23;13, 3075.00:8;4",
        'building_blocks': ['Leu', 'Phe', 'Val']
    },
    'test_2': {
        'data': "945.00:105;71, 3045.00:2;2, 2385.00:4;3, 2235.00:6;4, 2745.00:3;2, 2895.00:4;2, 1995.00:7;6, 885.00:72;38, 1695.00:6;5, 2685.00:2;2, 3315.00:16;3, 3390.00:3;1, 3510.00:4;2, 2295.00:7;6, 1365.00:8;8, 1425.00:40;27, 3105.00:5;4, 1305.00:40;28, 2145.00:4;3, 1875.00:6;6, 975.00:52;39, 915.00:190;128, 1455.00:22;14, 1725.00:5;4, 1635.00:14;8, 2355.00:2;2, 825.00:77;45, 2085.00:9;6, 1215.00:220;140, 3255.00:9;4, 3075.00:3;1, 3225.00:13;4, 3165.00:4;2, 2715.00:5;3, 735.00:33;21, 645.00:26;21, 2265.00:11;6, 2055.00:1;1, 2565.00:3;3, 1065.00:221;158, 1605.00:12;10, 2445.00:3;3, 1935.00:8;6, 2775.00:4;2, 1905.00:6;4, 1545.00:9;8, 2655.00:4;3, 2805.00:8;4, 855.00:27;21, 1125.00:148;100, 1035.00:191;134, 1665.00:11;8, 2865.00:6;4, 1095.00:279;182, 765.00:28;18, 3015.00:2;2, 1275.00:91;68, 1815.00:8;6, 2205.00:16;7, 3450.00:6;2, 1155.00:98;73, 675.00:23;17, 795.00:51;34, 3195.00:3;2, 2505.00:5;5, 2535.00:1;1, 615.00:30;18, 1755.00:4;3, 1515.00:16;12, 1485.00:12;11, 1245.00:248;162, 2475.00:10;6, 1575.00:28;16, 2115.00:4;3, 705.00:23;8, 1005.00:118;76, 2325.00:2;1, 1185.00:86;60, 2625.00:2;1, 1335.00:23;18, 1395.00:29;23, 2175.00:2;1, 3570.00:4;2, 2985.00:1;1, 1785.00:9;8, 2595.00:5;3, 2955.00:3;1, 2025.00:7;5, 1965.00:9;6, 3135.00:9;1, 2415.00:7;4, 2835.00:4;2, 3345.00:1;1, 3285.00:5;1, 1845.00:6;5",
        'building_blocks': ['DVal', 'DβHomoleu', 'DβHomoleu']
    },
    'test_3': {
        'data': "2145.00:111;79, 3105.00:59;36, 1695.00:70;45, 1245.00:71;51, 3510.00:75;33, 3195.00:78;36, 2625.00:169;95, 2295.00:86;63, 3450.00:73;45, 885.00:40;29, 1155.00:84;62, 1815.00:79;50, 2655.00:194;122, 1395.00:52;32, 2115.00:126;93, 2865.00:96;56, 615.00:85;62, 2895.00:64;43, 1305.00:35;27, 2955.00:74;46, 1485.00:30;22, 3285.00:124;47, 645.00:129;90, 1845.00:41;36, 3015.00:86;49, 1965.00:57;38, 2505.00:255;189, 1875.00:48;36, 1215.00:74;48, 2775.00:155;84, 1125.00:70;53, 1905.00:60;37, 1635.00:57;40, 3045.00:67;38, 1425.00:48;31, 1005.00:44;35, 2235.00:101;75, 3345.00:66;26, 1065.00:41;30, 675.00:162;114, 2415.00:148;104, 1515.00:53;33, 2265.00:72;52, 765.00:65;45, 2175.00:70;47, 3165.00:58;26, 2205.00:117;86, 3225.00:113;47, 1545.00:43;33, 1455.00:45;35, 3075.00:84;42, 2445.00:133;91, 2025.00:102;71, 735.00:80;51, 1935.00:52;39, 3255.00:125;50, 2385.00:102;78, 2475.00:195;137, 945.00:33;19, 975.00:40;31, 2745.00:98;67, 3390.00:79;34, 2565.00:313;221, 2835.00:131;70, 1995.00:65;46, 1785.00:68;53, 2325.00:88;56, 915.00:29;20, 2535.00:267;204, 2355.00:91;62, 705.00:139;87, 2805.00:128;87, 3570.00:56;32, 1335.00:41;27, 795.00:31;21, 1275.00:47;29, 1575.00:46;33, 1755.00:69;52, 2985.00:58;34, 2055.00:86;62, 855.00:53;38, 1665.00:72;50, 2085.00:117;80, 1185.00:91;71, 1095.00:33;27, 2685.00:98;78, 2715.00:89;59, 3135.00:91;45, 1035.00:50;34, 2595.00:327;207, 3315.00:96;41, 825.00:44;30, 1365.00:26;21, 1725.00:109;67, 2925.00:76;50, 1605.00:53;37",
        'building_blocks': ['Leu-LA03-Pro', 'Leu-Leu-DPro', 'DLeuMe-DLeuMe-DPro']
    }
}

def test_sgppm_single_compound():
    chroms = []
    for test in test_data.keys():
        data = test_data[test]['data']

        data = data.replace(";", ":")


        # Replace semicolons with colons to standardize separators
        data = data.replace(";", ":")

        # Get sorted times and intensities
        times, intensities = process_chromatography_data(data)

        # Create the numpy arrays
        times_array = times
        intensities_array = intensities
        building_blocks = test_data[test]['building_blocks']

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

        chroms.append(_chromatogram)

    return chroms
