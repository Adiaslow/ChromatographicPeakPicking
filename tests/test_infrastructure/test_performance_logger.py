# tests/test_infrastructure/test_performance_logger.py

import pytest
from src.chromatographicpeakpicking.infrastructure.logging.performance_logger import PerformanceLogger

def test_performance_logger_initialization():
    logger = PerformanceLogger()
    assert logger is not None

def test_performance_logger_log_operation():
    logger = PerformanceLogger()
    logger.log_operation("test_operation", 1.23)
    assert len(logger.get_operation_history()) == 1
    assert logger.get_operation_history()[0] == ("test_operation", 1.23)
