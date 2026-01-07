"""Basic tests for parser stubs."""
from orc.parsers.python_parser import PythonParser
from pathlib import Path


def test_python_parser_reads_file(tmp_path):
    p = tmp_path / "a.py"
    p.write_text("def f():\n    return 1\n")
    parser = PythonParser()
    result = parser.parse_file(p)
    assert "files" in result
