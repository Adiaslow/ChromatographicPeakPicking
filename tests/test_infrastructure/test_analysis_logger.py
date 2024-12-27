# tests/test_infrastructure/test_analysis_logger.py
import pytest
import tempfile
from pathlib import Path
from src.chromatographicpeakpicking.infrastructure.logging.analysis_logger import AnalysisLogger

@pytest.fixture
def temp_log_file():
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        yield Path(temp_file.name)
    temp_file.close()

def test_analysis_logger_initialization(temp_log_file):
    logger = AnalysisLogger(log_path=temp_log_file)
    assert logger is not None
    assert logger.get_session_id() is not None

def test_analysis_logger_log(temp_log_file):
    logger = AnalysisLogger(log_path=temp_log_file)
    logger.log_analysis_start({"param1": "value1"})
    logger.log_analysis_step("Step 1", {"metric1": 100})
    logger.log_analysis_end({"result": "success"})

    # Read the log file and check the contents
    with open(temp_log_file, 'r') as log_file:
        log_contents = log_file.read()
        assert "Analysis started" in log_contents
        assert "Step 1" in log_contents
        assert "Analysis completed" in log_contents
