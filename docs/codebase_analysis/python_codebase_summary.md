# Python Codebase Summary

Generated on: 2024-12-18 14:25:06

## Summary Statistics
- Total Python files: 63
- Total functions: 125

---


## Directory: chromatographicpeakpicking


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/configurations


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### aals_config.py
**File Statistics:**
- Total lines: 29
- Non-empty lines: 23
- Number of functions: 0

---

### chromatogram_analyzer_config.py
**File Statistics:**
- Total lines: 36
- Non-empty lines: 30
- Number of functions: 0

---

### chromatogram_visualizer_config.py
**File Statistics:**
- Total lines: 54
- Non-empty lines: 47
- Number of functions: 1

**Functions:**
```python
def __post_init__
```
---

### classic_chrome_config.py
**File Statistics:**
- Total lines: 13
- Non-empty lines: 10
- Number of functions: 0

---

### global_config.py
**File Statistics:**
- Total lines: 16
- Non-empty lines: 12
- Number of functions: 0

---

### peak_finder_config.py
**File Statistics:**
- Total lines: 40
- Non-empty lines: 32
- Number of functions: 0

---

### sgppm_config.py
**File Statistics:**
- Total lines: 32
- Non-empty lines: 28
- Number of functions: 0

---

### swm_config.py
**File Statistics:**
- Total lines: 10
- Non-empty lines: 7
- Number of functions: 0

---

### tabular_data_parser_config.py
**File Statistics:**
- Total lines: 23
- Non-empty lines: 21
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/metrics


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### chromatogram_metrics.py
**File Statistics:**
- Total lines: 45
- Non-empty lines: 35
- Number of functions: 3

**Functions:**
```python
def get_metric
def set_metric
def get_all_metrics
```
---

### peak_metrics.py
**File Statistics:**
- Total lines: 51
- Non-empty lines: 35
- Number of functions: 3

**Functions:**
```python
def get_metric
def set_metric
def get_all_metrics
```
---


## Directory: chromatographicpeakpicking/analyzers


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### chromatogram_analyzer.py
**File Statistics:**
- Total lines: 278
- Non-empty lines: 219
- Number of functions: 11

**Functions:**
```python
def __post_init__
def analyze_chromatogram
def _validate_chromatogram
def _calculate_moving_std
def _find_minimal_variation_regions
def _calculate_noise_metrics
def _calculate_baseline_metrics
def _calculate_area_metrics
def _calculate_distribution_metrics
def _calculate_quality_metrics
def __call__
```
---

### peak_analyzer.py
**File Statistics:**
- Total lines: 180
- Non-empty lines: 151
- Number of functions: 11

**Functions:**
```python
def analyze_peak
def _gaussian
def _calculate_peak_boundaries
def _calculate_gaussian_fit
def _calculate_peak_width
def _calculate_peak_area
def _calculate_peak_symmetry
def _calculate_peak_skewness
def _calculate_peak_resolution
def _calculate_peak_prominence
def _calculate_peak_score
```
---

### split_tree_analysis.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/parsers


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### tabular_data_parser.py
**File Statistics:**
- Total lines: 68
- Non-empty lines: 57
- Number of functions: 3

**Functions:**
```python
def parse_data
def _get_raw_dataframe
def _clean_dataframe
```
---


## Directory: chromatographicpeakpicking/core


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### building_block.py
**File Statistics:**
- Total lines: 15
- Non-empty lines: 11
- Number of functions: 2

**Functions:**
```python
def __eq__
def __hash__
```
---

### chromatogram.py
**File Statistics:**
- Total lines: 241
- Non-empty lines: 187
- Number of functions: 20

**Functions:**
```python
def length
def has_peaks
def add_peak
def add_peaks
def clear_peaks
def get_peaks_in_range
def _validate_chromatograms
def validate_data
def _validate_peak_times
def __getitem__
def __setitem__
def __eq__
def __ne__
def __lt__
def __le__
def __gt__
def __ge__
def __hash__
def __str__
def __repr__
```
---

### hierarchy.py
**File Statistics:**
- Total lines: 248
- Non-empty lines: 200
- Number of functions: 15

**Functions:**
```python
def count_non_null
def get_direct_descendants
def generate_descendants_with_k_elements
def generate_all_descendants
def add_sequence
def add_sequences
def get_sequences_by_level
def get_level
def get_ancestors
def get_descendants
def set_sequence_value
def set_sequence_values
def get_sequence_value
def visualize_hierarchy
def place_elements
```
---

### peak.py
**File Statistics:**
- Total lines: 225
- Non-empty lines: 166
- Number of functions: 12

**Functions:**
```python
def _validate_peak_metrics
def __getitem__
def __setitem__
def __eq__
def __ne__
def __lt__
def __le__
def __gt__
def __ge__
def __hash__
def __str__
def __repr__
```
---


## Directory: chromatographicpeakpicking/core/protocols


### Ibaseline_corrector.py
**File Statistics:**
- Total lines: 90
- Non-empty lines: 67
- Number of functions: 3

**Functions:**
```python
def validate_chromatogram
def correct_baseline
def __call__
```
---

### Iconfig.py
**File Statistics:**
- Total lines: 8
- Non-empty lines: 6
- Number of functions: 0

---

### Idata_parser.py
**File Statistics:**
- Total lines: 16
- Non-empty lines: 11
- Number of functions: 1

**Functions:**
```python
def parse_data
```
---

### Imetrics.py
**File Statistics:**
- Total lines: 28
- Non-empty lines: 19
- Number of functions: 3

**Functions:**
```python
def get_metric
def set_metric
def get_all_metrics
```
---

### Ivisualizer.py
**File Statistics:**
- Total lines: 92
- Non-empty lines: 70
- Number of functions: 3

**Functions:**
```python
def visualize
def save
def __call__
```
---


## Directory: chromatographicpeakpicking/peak_selection


### Ipeak_picker.py
**File Statistics:**
- Total lines: 55
- Non-empty lines: 40
- Number of functions: 2

**Functions:**
```python
def pick_peaks
def _select_peak
```
---

### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### classic_chrome.py
**File Statistics:**
- Total lines: 152
- Non-empty lines: 118
- Number of functions: 5

**Functions:**
```python
def pick_peaks
def _prepare_chromatograms
def _find_peaks
def _select_peaks
def _build_hierarchy
```
---

### hierarchical_sgppm.py
**File Statistics:**
- Total lines: 180
- Non-empty lines: 150
- Number of functions: 4

**Functions:**
```python
def pick_peaks
def _process_level
def _apply_hierarchy_constraints
def _hierarchical_peak_selection
```
---

### peak_finder.py
**File Statistics:**
- Total lines: 178
- Non-empty lines: 152
- Number of functions: 10

**Functions:**
```python
def __post_init__
def _log_debug
def find_peaks
def _calculate_height_threshold
def _calculate_prominence_threshold
def _calculate_width_threshold
def _calculate_distance_threshold
def _calculate_window_length
def _create_peaks
def __call__
```
---

### sgppm.py
**File Statistics:**
- Total lines: 240
- Non-empty lines: 183
- Number of functions: 4

**Functions:**
```python
def __post_init__
def pick_peaks
def _fit_gaussians
def _select_peak
```
---


## Directory: chromatographicpeakpicking/visualizers


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### chromatogram_visualizer.py
**File Statistics:**
- Total lines: 160
- Non-empty lines: 148
- Number of functions: 1

**Functions:**
```python
def visualize
```
---

### image_type.py
**File Statistics:**
- Total lines: 19
- Non-empty lines: 14
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/io/writers


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### csv_writer.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### hdf5_writer.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### npz_writer.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### numpy_writer.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### pickle_writter.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### xlsx_writer.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/io/readers


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### csv_reader.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### hdf5_reader.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### npz_reader.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### numpy_reader.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### pickle_reader.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### xlsx_reader.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/io/loaders


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/utils


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### gaussian_curve.py
**File Statistics:**
- Total lines: 25
- Non-empty lines: 20
- Number of functions: 1

**Functions:**
```python
def gaussian_curve
```
---

### process_sequence_count_chromatogram_data.py
**File Statistics:**
- Total lines: 35
- Non-empty lines: 25
- Number of functions: 1

**Functions:**
```python
def process_sequence_count_chromatogram_data
```
---


## Directory: chromatographicpeakpicking/baseline_correctors


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### aals.py
**File Statistics:**
- Total lines: 88
- Non-empty lines: 68
- Number of functions: 1

**Functions:**
```python
def correct_baseline
```
---

### swm.py
**File Statistics:**
- Total lines: 144
- Non-empty lines: 110
- Number of functions: 4

**Functions:**
```python
def _validate_inputs
def _pad_signal
def _compute_baseline
def correct_baseline
```
---


## Directory: cli


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### analyze_library_sgppm.py
**File Statistics:**
- Total lines: 52
- Non-empty lines: 41
- Number of functions: 1

**Functions:**
```python
def main
```
---


## Directory: gui


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---
