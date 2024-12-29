src/
└── chromatographicpeakpicking/
    ├── __init__.py
    ├── core/                          # Abstract design patterns
    │   ├── __init__.py
    │   ├── builders/
    │   │   ├── __init__.py
    │   │   └── pipeline_builder.py
    │   ├── domain/                    # Domain models
    │   │   ├── __init__.py
    │   │   ├── building_block.py
    │   │   ├── chromatogram.py
    │   │   ├── hierarchy.py
    │   │   ├── peak.py
    │   │   └── peptide.py
    │   ├── factories/
    │   │   ├── __init__.py
    │   │   ├── analyzer_factory.py
    │   │   ├── corrector_factory.py
    │   │   ├── detector_factory.py
    │   │   └── pipeline_factory.py
    │   ├── protocols/
    │   │   ├── __init__.py
    │   │   ├── analyzable.py
    │   │   ├── configurable.py
    │   │   ├── correctable.py
    │   │   ├── detectable.py
    │   │   ├── error_handler.py
    │   │   ├── observable.py
    │   │   ├── parseable.py
    │   │   ├── selectable.py
    │   │   ├── serializable.py
    │   │   ├── validatable.py
    │   │   └── visualizable.py
    │   ├── singletons/
    │   │   ├── __init__.py
    │   │   └── singleton.py
    │   ├── strategies/                # Strategy pattern for analyzers and other strategies
    │   │   ├── __init__.py
    │   │   ├── base_analyzer.py
    │   │   └── peak_analyzer.py
    │   ├── types/                     # Custom types, errors, and validation logic
    │       ├── __init__.py
    │       ├── config.py
    │       ├── errors.py
    │       └── validation.py
    ├── implementations/               # Concrete implementations for various functions
    │   ├── __init__.py
    │   ├── analyzers/                 # Concrete analyzers
    │   │   ├── __init__.py
    │   │   ├── chromatogram_analyzer.py
    │   │   ├── peak_analyzer.py
    │   │   └── split_tree_analysis.py
    │   ├── baseline_correction/       # Baseline correction algorithms
    │   │   ├── __init__.py
    │   │   ├── aals.py
    │   │   └── swm.py
    │   ├── detectors/                 # Concrete detectors
    │   │   ├── __init__.py
    │   │   └── peak_detector.py
    │   ├── peak_detection/            # Peak detection algorithms
    │   │   ├── __init__.py
    │   │   └── peak_finder.py
    │   ├── peak_selection/            # Peak selection implementations
    │   │   ├── __init__.py
    │   │   ├── Ipeak_picker.py
    │   │   ├── classic_chrome.py
    │   │   ├── hierarchical_sgppm.py
    │   │   ├── peak_finder.py
    │   │   └── sgppm.py
    │   ├── pipelines/                 # Concrete pipeline implementations
    │   │   ├── __init__.py
    │   │   ├── cc_pipeline.py
    │   │   ├── sgppm_pipeline.py
    │   │   └── hsgppm_pipeline.py
    │   ├── builders/                  # Concrete pipeline builders
    │   │   ├── __init__.py
    │   │   └── concrete_pipeline_builder.py
    │   ├── commands/                  # Command classes for pipeline stages
    │   │   ├── __init__.py
    │   │   ├── baseline_command.py
    │   │   └── detection_command.py
    │   ├── observers/                 # Observer classes for monitoring pipelines
    │   │   ├── __init__.py
    │   │   └── progress_observer.py
    │   ├── serializers/               # Concrete serializers
    │   │   ├── __init__.py
    │   │   └── peak_serializer.py
    │   ├── visualizers/               # Concrete visualizers
    │       ├── __init__.py
    │       ├── chromatogram_visualizer.py
    │       └── image_type.py
    ├── config/                        # Configuration management
    │   ├── __init__.py
    │   ├── config_manager.py
    │   └── global_config.py
    ├── io/                            # Input and output operations
    │   ├── __init__.py
    │   ├── formats/                   # Format handlers for CSV, Excel, etc.
    │   │   ├── __init__.py
    │   │   ├── csv_format.py
    │   │   ├── excel_format.py
    │   │   └── format_handler.py
    │   ├── protocols/                 # Reader and writer interfaces
    │   │   ├── __init__.py
    │   │   ├── reader.py
    │   │   └── writer.py
    │   ├── readers/                   # Data readers
    │   │   ├── __init__.py
    │   └── writers/                   # Data writers
    │       ├── __init__.py
    ├── utils/                         # Utility functions and modules
    │   ├── __init__.py
    │   ├── gaussian_curve.py
    │   └── process_sequence_count_chromatogram_data.py
    ├── visualization/                 # Visualization components
    │   ├── __init__.py
    │   ├── exporters/                 # Export visualization results
    │   │   ├── __init__.py
    │   └── renderers/                 # Render visualizations
    │       ├── __init__.py
    ├── infrastructure/                # Infrastructure-related components
    │   ├── __init__.py
    │   ├── caching/                   # Caching mechanisms
    │   │   ├── __init__.py
    │   │   └── result_cache.py
    │   ├── logging/                   # Logging mechanisms
    │   │   ├── __init__.py
    │   │   ├── analysis_logger.py
    │   │   └── performance_logger.py
    │   ├── metrics/                   # Metrics collection
    │   │   ├── __init__.py
    │   │   ├── chromatogram_metrics.py
    │   │   └── performance_metrics.py
    │   └── persistence/               # Data persistence mechanisms
    │       ├── __init__.py
    │       ├── base_repository.py
    │       ├── chromatogram_repository.py
    │       └── peak_repository.py
    ├── parsers/                       # Data parsers
    │   ├── __init__.py
    │   └── tabular_data_parser.py
