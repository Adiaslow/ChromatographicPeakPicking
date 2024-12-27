# Python Codebase Summary

Generated on: 2024-12-27 06:43:20

## Summary Statistics
- Total Python files: 124
- Total functions: 269

---


## Root Directory


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

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


## Directory: chromatographicpeakpicking/visualization


### __init__.py
**File Statistics:**
- Total lines: 6
- Non-empty lines: 4
- Number of functions: 0

**File Description:**
Initialization module for visualization components.

---


## Directory: chromatographicpeakpicking/visualization/renderers


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/visualization/exporters


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
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


## Directory: chromatographicpeakpicking/pipeline


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### error_handling.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### result.py
**File Statistics:**
- Total lines: 39
- Non-empty lines: 33
- Number of functions: 0

---

### stage.py
**File Statistics:**
- Total lines: 51
- Non-empty lines: 42
- Number of functions: 5

**Functions:**
```python
def __init__
def execute
def validate
def error_handler
def config
```
---


## Directory: chromatographicpeakpicking/pipeline/builders


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### pipeline_builder.py
**File Statistics:**
- Total lines: 48
- Non-empty lines: 40
- Number of functions: 2

**Functions:**
```python
def process
def _notify_observers
```
---


## Directory: chromatographicpeakpicking/pipeline/commands


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### baseline_command.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### detection_command.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/pipeline/observers


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### progress_observer.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/analyzers


### __init__.py
**File Statistics:**
- Total lines: 8
- Non-empty lines: 6
- Number of functions: 0

---

### chromatogram_analyzer.py
**File Statistics:**
- Total lines: 302
- Non-empty lines: 240
- Number of functions: 15

**Functions:**
```python
def __init__
def __post_init__
def configure
def get_metadata
def validate_config
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
- Total lines: 3
- Non-empty lines: 2
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

### errors.py
**File Statistics:**
- Total lines: 16
- Non-empty lines: 13
- Number of functions: 0

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

### validation.py
**File Statistics:**
- Total lines: 21
- Non-empty lines: 17
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/core/types


### __init__.py
**File Statistics:**
- Total lines: 20
- Non-empty lines: 18
- Number of functions: 0

---

### config.py
**File Statistics:**
- Total lines: 45
- Non-empty lines: 39
- Number of functions: 0

---

### errors.py
**File Statistics:**
- Total lines: 44
- Non-empty lines: 36
- Number of functions: 1

**Functions:**
```python
def __init__
```
---

### validation.py
**File Statistics:**
- Total lines: 46
- Non-empty lines: 38
- Number of functions: 2

**Functions:**
```python
def has_errors
def has_warnings
```
---


## Directory: chromatographicpeakpicking/core/factories


### __init__.py
**File Statistics:**
- Total lines: 12
- Non-empty lines: 10
- Number of functions: 0

---

### analyzer_factory.py
**File Statistics:**
- Total lines: 21
- Non-empty lines: 16
- Number of functions: 2

**Functions:**
```python
def register
def create
```
---

### corrector_factory.py
**File Statistics:**
- Total lines: 21
- Non-empty lines: 16
- Number of functions: 2

**Functions:**
```python
def register
def create
```
---

### detector_factory.py
**File Statistics:**
- Total lines: 21
- Non-empty lines: 16
- Number of functions: 2

**Functions:**
```python
def register
def create
```
---

### pipeline_factory.py
**File Statistics:**
- Total lines: 52
- Non-empty lines: 41
- Number of functions: 4

**Functions:**
```python
def register_corrector
def register_detector
def register_selector
def create_pipeline
```
---


## Directory: chromatographicpeakpicking/core/domain


### __init__.py
**File Statistics:**
- Total lines: 12
- Non-empty lines: 10
- Number of functions: 0

---

### building_block.py
**File Statistics:**
- Total lines: 42
- Non-empty lines: 35
- Number of functions: 4

**Functions:**
```python
def __post_init__
def with_metadata
def __eq__
def __hash__
```
---

### chromatogram.py
**File Statistics:**
- Total lines: 306
- Non-empty lines: 263
- Number of functions: 21

**Functions:**
```python
def __post_init__
def length
def duration
def num_peaks
def get_intensity_range
def get_time_range
def get_signal_at_time
def get_peaks_in_range
def with_peaks
def with_baseline
def with_building_blocks
def with_metadata
def get_corrected_intensity
def slice
def resample
def smooth
def normalize
def __len__
def __eq__
def __str__
def __repr__
```
---

### peak.py
**File Statistics:**
- Total lines: 163
- Non-empty lines: 140
- Number of functions: 11

**Functions:**
```python
def __post_init__
def width
def retention_time
def symmetry
def get_gaussian_fit
def with_gaussian_fit
def with_quality_metrics
def overlaps_with
def get_overlap_percentage
def __eq__
def __hash__
```
---

### peptide.py
**File Statistics:**
- Total lines: 95
- Non-empty lines: 81
- Number of functions: 11

**Functions:**
```python
def __post_init__
def length
def mass
def get_building_block_at_position
def with_retention_time
def with_peak_metrics
def with_metadata
def get_sequence_string
def __eq__
def __hash__
def __str__
```
---


## Directory: chromatographicpeakpicking/core/protocols


### __init__.py
**File Statistics:**
- Total lines: 23
- Non-empty lines: 21
- Number of functions: 0

---

### analyzable.py
**File Statistics:**
- Total lines: 18
- Non-empty lines: 14
- Number of functions: 2

**Functions:**
```python
def analyze
def validate
```
---

### configurable.py
**File Statistics:**
- Total lines: 41
- Non-empty lines: 30
- Number of functions: 3

**Functions:**
```python
def configure
def get_metadata
def validate_config
```
---

### correctable.py
**File Statistics:**
- Total lines: 15
- Non-empty lines: 11
- Number of functions: 2

**Functions:**
```python
def correct
def validate
```
---

### detectable.py
**File Statistics:**
- Total lines: 16
- Non-empty lines: 12
- Number of functions: 2

**Functions:**
```python
def detect
def validate
```
---

### error_handler.py
**File Statistics:**
- Total lines: 43
- Non-empty lines: 32
- Number of functions: 5

**Functions:**
```python
def handle_error
def set_severity_threshold
def add_error
def get_errors
def clear
```
---

### observable.py
**File Statistics:**
- Total lines: 33
- Non-empty lines: 25
- Number of functions: 4

**Functions:**
```python
def update
def add_observer
def remove_observer
def notify_observers
```
---

### parseable.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### selectable.py
**File Statistics:**
- Total lines: 15
- Non-empty lines: 11
- Number of functions: 2

**Functions:**
```python
def select
def validate
```
---

### serializable.py
**File Statistics:**
- Total lines: 15
- Non-empty lines: 11
- Number of functions: 2

**Functions:**
```python
def to_dict
def from_dict
```
---

### validatable.py
**File Statistics:**
- Total lines: 20
- Non-empty lines: 15
- Number of functions: 3

**Functions:**
```python
def __init__
def validate
def is_valid
```
---

### visualizable.py
**File Statistics:**
- Total lines: 15
- Non-empty lines: 11
- Number of functions: 2

**Functions:**
```python
def visualize
def save
```
---


## Directory: chromatographicpeakpicking/analysis


### __init__.py
**File Statistics:**
- Total lines: 6
- Non-empty lines: 4
- Number of functions: 0

**File Description:**
Initialization module for analysis components.

---


## Directory: chromatographicpeakpicking/analysis/chromatogram


### __init__.py
**File Statistics:**
- Total lines: 6
- Non-empty lines: 4
- Number of functions: 0

---

### baseline_analyzer.py
**File Statistics:**
- Total lines: 47
- Non-empty lines: 39
- Number of functions: 1

**Functions:**
```python
def __init__
```
---

### peak_detector.py
**File Statistics:**
- Total lines: 82
- Non-empty lines: 72
- Number of functions: 2

**Functions:**
```python
def __init__
def __init__
```
---


## Directory: chromatographicpeakpicking/analysis/baseline


### __init__.py
**File Statistics:**
- Total lines: 11
- Non-empty lines: 8
- Number of functions: 0

**File Description:**
Initialization module for baseline correctors.

---

### aals.py
**File Statistics:**
- Total lines: 43
- Non-empty lines: 37
- Number of functions: 2

**Functions:**
```python
def correct
def validate
```
---


## Directory: chromatographicpeakpicking/analysis/peak


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### peak_analyzer.py
**File Statistics:**
- Total lines: 140
- Non-empty lines: 119
- Number of functions: 7

**Functions:**
```python
def __init__
def __init__
def _calculate_r2
def _calculate_symmetry
def _calculate_capacity
def gaussian
def gaussian
```
---

### peak_interogrator.py
**File Statistics:**
- Total lines: 111
- Non-empty lines: 93
- Number of functions: 2

**Functions:**
```python
def __init__
def __init__
```
---


## Directory: chromatographicpeakpicking/analysis/selection


### __init__.py
**File Statistics:**
- Total lines: 2
- Non-empty lines: 1
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/analysis/protocols


### __init__.py
**File Statistics:**
- Total lines: 5
- Non-empty lines: 3
- Number of functions: 0

---

### analyzer.py
**File Statistics:**
- Total lines: 28
- Non-empty lines: 22
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/analysis/detection


### __init__.py
**File Statistics:**
- Total lines: 2
- Non-empty lines: 1
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/analysis/base


### __init__.py
**File Statistics:**
- Total lines: 6
- Non-empty lines: 4
- Number of functions: 0

---

### analysis_context.py
**File Statistics:**
- Total lines: 47
- Non-empty lines: 36
- Number of functions: 2

**Functions:**
```python
def __init__
def register_analyzer
```
---


## Directory: chromatographicpeakpicking/config


### __init__.py
**File Statistics:**
- Total lines: 6
- Non-empty lines: 4
- Number of functions: 0

**File Description:**
Initialization module for configuration components.

---

### config_manager.py
**File Statistics:**
- Total lines: 26
- Non-empty lines: 21
- Number of functions: 4

**Functions:**
```python
def __init__
def register_component
def configure_component
def get_component_metadata
```
---

### global_config.py
**File Statistics:**
- Total lines: 12
- Non-empty lines: 9
- Number of functions: 1

**Functions:**
```python
def __post_init__
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
- Total lines: 6
- Non-empty lines: 4
- Number of functions: 0

**File Description:**
Initialization module for selection algorithms.

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


## Directory: chromatographicpeakpicking/io


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/io/formats


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### csv_format.py
**File Statistics:**
- Total lines: 34
- Non-empty lines: 28
- Number of functions: 0

---

### excel_format.py
**File Statistics:**
- Total lines: 34
- Non-empty lines: 28
- Number of functions: 0

---

### format_handler.py
**File Statistics:**
- Total lines: 23
- Non-empty lines: 18
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/io/writers


### __init__.py
**File Statistics:**
- Total lines: 6
- Non-empty lines: 4
- Number of functions: 0

**File Description:**
Initialization module for writers.

---


## Directory: chromatographicpeakpicking/io/readers


### __init__.py
**File Statistics:**
- Total lines: 6
- Non-empty lines: 4
- Number of functions: 0

**File Description:**
Initialization module for readers.

---


## Directory: chromatographicpeakpicking/io/protocols


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### reader.py
**File Statistics:**
- Total lines: 15
- Non-empty lines: 11
- Number of functions: 0

---

### writer.py
**File Statistics:**
- Total lines: 15
- Non-empty lines: 11
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/utils


### __init__.py
**File Statistics:**
- Total lines: 6
- Non-empty lines: 4
- Number of functions: 0

**File Description:**
Initialization module for utility functions.

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


## Directory: chromatographicpeakpicking/peak_detection


### __init__.py
**File Statistics:**
- Total lines: 6
- Non-empty lines: 4
- Number of functions: 0

**File Description:**
Initialization module for peak detection algorithms.

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


## Directory: chromatographicpeakpicking/infrastructure


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---


## Directory: chromatographicpeakpicking/infrastructure/metrics


### __init__.py
**File Statistics:**
- Total lines: 6
- Non-empty lines: 4
- Number of functions: 0

---

### performance_metrics.py
**File Statistics:**
- Total lines: 41
- Non-empty lines: 31
- Number of functions: 4

**File Description:**
Performance metrics tracking.

**Functions:**
```python
def __init__
def start_operation
def end_operation
def get_operation_stats
```
---


## Directory: chromatographicpeakpicking/infrastructure/persistence


### __init__.py
**File Statistics:**
- Total lines: 10
- Non-empty lines: 8
- Number of functions: 0

---

### base_repository.py
**File Statistics:**
- Total lines: 40
- Non-empty lines: 31
- Number of functions: 4

**File Description:**
Base repository for persistence layer.

**Functions:**
```python
def save
def get
def get_all
def delete
```
---

### chromatogram_repository.py
**File Statistics:**
- Total lines: 46
- Non-empty lines: 35
- Number of functions: 5

**File Description:**
Repository for handling chromatogram persistence.

**Functions:**
```python
def __init__
def save
def get
def get_all
def delete
```
---

### peak_repository.py
**File Statistics:**
- Total lines: 46
- Non-empty lines: 35
- Number of functions: 5

**File Description:**
Repository for handling peak persistence.

**Functions:**
```python
def __init__
def save
def get
def get_all
def delete
```
---


## Directory: chromatographicpeakpicking/infrastructure/caching


### __init__.py
**File Statistics:**
- Total lines: 1
- Non-empty lines: 0
- Number of functions: 0

---

### result_cache.py
**File Statistics:**
- Total lines: 45
- Non-empty lines: 35
- Number of functions: 5

**File Description:**
Cache for storing analysis results.

**Functions:**
```python
def __init__
def get
def set
def invalidate
def clear
```
---


## Directory: chromatographicpeakpicking/infrastructure/logging


### __init__.py
**File Statistics:**
- Total lines: 8
- Non-empty lines: 6
- Number of functions: 0

---

### analysis_logger.py
**File Statistics:**
- Total lines: 122
- Non-empty lines: 103
- Number of functions: 9

**Functions:**
```python
def __post_init__
def log_analysis_start
def log_analysis_step
def log_analysis_end
def log_error
def log_warning
def log_performance_metrics
def log_validation_results
def get_session_id
```
---

### performance_logger.py
**File Statistics:**
- Total lines: 36
- Non-empty lines: 28
- Number of functions: 4

**File Description:**
Logger for performance metrics.

**Functions:**
```python
def __init__
def log_operation
def get_operation_history
def get_average_duration
```
---
