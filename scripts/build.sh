#!/bin/bash
# Build script for ORC package

set -e

echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

echo "📦 Building package..."
python -m build

echo "✅ Checking package with twine..."
python -m twine check dist/*

echo ""
echo "📊 Build Summary:"
ls -lh dist/

echo ""
echo "✅ Build complete! Package is ready for PyPI."
echo ""
echo "To publish to TestPyPI:"
echo "  python -m twine upload --repository testpypi dist/*"
echo ""
echo "To publish to PyPI:"
echo "  python -m twine upload dist/*"
