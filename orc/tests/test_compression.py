"""Tests for compression pipeline (skeleton)."""
from orc.core.compressor import Compressor


def test_compressor_noop():
    c = Compressor()
    assert isinstance(c.compress_index({}), dict)
