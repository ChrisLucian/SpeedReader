"""Pytest configuration and shared fixtures."""
import pytest
import gc
import time


# Configure pytest to handle tkinter properly
def pytest_configure(config):
    """Configure pytest for tkinter testing."""
    # Ensure tkinter doesn't cause issues in headless environments
    import os
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'


@pytest.fixture
def app():
    """Create a SpeedReaderController instance for testing.
    
    This fixture handles proper cleanup to avoid Tcl/Tk initialization issues.
    Includes retry logic for intermittent Tcl initialization failures on Windows.
    """
    from Controllers.SpeedReaderController import SpeedReaderController
    
    # Retry logic for intermittent Tcl initialization failures
    max_retries = 3
    last_error = None
    
    for attempt in range(max_retries):
        try:
            controller = SpeedReaderController()
            controller.update()  # Process any pending events
            yield controller
            try:
                controller.destroy()
            except Exception:
                pass
            gc.collect()  # Force garbage collection to clean up Tcl resources
            return
        except Exception as e:
            last_error = e
            gc.collect()
            time.sleep(0.1 * (attempt + 1))  # Increasing delay between retries
    
    # If all retries failed, raise the last error
    raise last_error


@pytest.fixture
def frame(app):
    """Get the MainFrame from the controller."""
    return app.winfo_children()[0]
