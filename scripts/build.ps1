# Build script for ORC package (PowerShell)

Write-Host "🧹 Cleaning previous builds..." -ForegroundColor Cyan
Remove-Item -Path "dist", "build", "*.egg-info" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`n📦 Installing build tools..." -ForegroundColor Cyan
python -m pip install --upgrade build twine

Write-Host "`n📦 Building package..." -ForegroundColor Cyan
python -m build

if (Test-Path "dist") {
    Write-Host "`n✅ Checking package with twine..." -ForegroundColor Cyan
    python -m twine check dist/*
    
    Write-Host "`n📊 Build Summary:" -ForegroundColor Green
    Get-ChildItem "dist" | Format-Table Name, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB,2)}} -AutoSize
    
    Write-Host "`n✅ Build complete! Package is ready for PyPI.`n" -ForegroundColor Green
    Write-Host "To publish to TestPyPI:" -ForegroundColor Yellow
    Write-Host "  python -m twine upload --repository testpypi dist/*`n"
    Write-Host "To publish to PyPI:" -ForegroundColor Yellow
    Write-Host "  python -m twine upload dist/*`n"
} else {
    Write-Host "`n❌ Build failed - no dist folder created" -ForegroundColor Red
    exit 1
}
