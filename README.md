# Chromatography Analysis Toolkit
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
![pytest](https://github.com/Adiaslow/ChromatographicPeakPicking/actions/workflows/pytest.yml/badge.svg)
[![Pylint](https://github.com/Adiaslow/ChromatographicPeakPicking/actions/workflows/pylint.yml/badge.svg)](https://github.com/Adiaslow/ChromatographicPeakPicking/actions/workflows/pylint.yml)
[![GitHub last commit](https://img.shields.io/github/last-commit/Adiaslow/ChromatographicPeakPicking.svg)](https://github.com/Adiaslow/ChromatographicPeakPicking/commits/main)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Adiaslow/ChromatographicPeakPicking.svg)](https://github.com/Adiaslow/ChromatographicPeakPicking)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python toolkit for analyzing chromatographic data, featuring peak detection, baseline correction, and visualization capabilities as well as split-tree analysis for reaction profiling.

## Features

- **Peak Detection**: Multiple algorithms for peak picking including:
  - Classic Chrome (CC)
  - Gaussian Peak Picking Model (GPPM)
  - Hierarchical Simple Gaussian Peak Picking Model (HGPPM)

- **Baseline Correction**:
  - Asymmetric Adaptive Least Squares (AALS)
  - Sliding Window Method (SWM)
  - Configurable parameters for different chromatogram types

- **Analysis Tools**:
  - Chromatogram quality metrics
  - Peak analysis
  - Noise and baseline metrics
  - Distribution analysis

- **Visualization**:
  - Chromatogram plotting
  - Peak highlighting
  - Hierarchy visualization
  - Customizable plotting options

- **Data Handling**:
  - Tabular data parsing
  - Flexible data structures for chromatograms and peaks
  - Hierarchical data organization

- **Reaction Profiling**:
  - Split-Tree Analysis
 
## Project Structure

```
.
├── analyzers/           # Analysis modules for chromatograms and peaks
├── baseline_correctors/ # Baseline correction algorithms
├── cli/                # Command-line interface tools
├── configs/            # Configuration classes for different modules
├── core/              # Core data structures and utilities
├── data_parsers/      # Data import and parsing tools
├── metrics/           # Metric calculation modules
├── peak_pickers/      # Peak detection algorithms
├── test/              # Test suite
├── utilities/         # Helper functions and utilities
└── visualizers/       # Visualization tools
```

## Installation

## Quick Start

```python
# Example usage of peak detection
from peak_pickers.classic_chrome import pick_peaks
from data_parsers.tabular_data_parser import parse_data

# Load and parse input data
data = parse_data("your_data.csv")

# Detect peaks
peaks = pick_peaks(data)

# Analyze peaks
from analyzers.peak_analyzer import analyze_peak
peak_metrics = analyze_peak(peaks[0])

# Visualize results
from visualizers.chromatogram_visualizer import visualize
visualize(data, peaks)
```

## Configuration

The toolkit uses configuration classes for each major component. These can be found in the `configs/` directory and allow customization of:

- Peak detection parameters
- Baseline correction settings
- Visualization options
- Analysis thresholds
- Data parsing rules

## Testing

The project includes a comprehensive test suite. To run the tests:

```bash
python -m pytest test/
```
