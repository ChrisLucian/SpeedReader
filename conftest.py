# Present so pytest adds the repository root to sys.path, making the
# Core package importable from tests without installing the project.
# The side-effect lock plugin is registered here (not via `-p`) so coverage is
# already running when it loads.
pytest_plugins = ["testsupport.locks"]
