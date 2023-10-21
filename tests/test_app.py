"""Simple package testing."""
from app import __version__


def test_version():
    """Test Package Version."""
    assert __version__
