"""
Production deployment script for ORC
"""
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional


def check_requirements():
    """Verify deployment requirements"""
    required_vars = ['ORC_SECRET_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        return False
    
    return True


def run_tests():
    """Run test suite before deployment"""
    print("🧪 Running tests...")
    result = subprocess.run(
        ["pytest", "tests/", "-v"],
        cwd=Path(__file__).parent.parent
    )
    return result.returncode == 0


def build_docker():
    """Build Docker image"""
    print("🐳 Building Docker image...")
    result = subprocess.run(
        ["docker", "build", "-t", "orc:latest", "-f", "orc/Dockerfile", "."]
    )
    return result.returncode == 0


def deploy(target: str = "local", skip_tests: bool = False):
    """
    Deploy ORC to specified target
    
    Args:
        target: Deployment target (local, docker, production)
        skip_tests: Skip test suite (not recommended)
    
    Returns:
        dict: Deployment status information
    """
    print(f"🚀 Deploying ORC to {target}...")
    
    # Pre-deployment checks
    if target == "production":
        if not check_requirements():
            sys.exit(1)
    
    if not skip_tests and not run_tests():
        print("❌ Tests failed! Aborting deployment.")
        sys.exit(1)
    
    # Deploy based on target
    if target == "docker":
        if build_docker():
            print("✅ Docker image built successfully")
            print("   Run: docker run -p 8000:8000 orc:latest")
        else:
            print("❌ Docker build failed")
            sys.exit(1)
    
    elif target == "production":
        # Add your production deployment steps
        print("⚠️  Production deployment checklist:")
        print("   1. Ensure ORC_SECRET_KEY is set in production environment")
        print("   2. Configure database path")
        print("   3. Set up reverse proxy (nginx/Apache)")
        print("   4. Enable HTTPS")
        print("   5. Configure firewall rules")
        print("\n   Recommended: Use Docker + Kubernetes or Docker Compose")
    
    else:  # local
        print("✅ Local deployment ready")
        print("   Run: orc serve")
    
    return {"deployed": target, "status": "success"}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Deploy ORC")
    parser.add_argument("target", choices=["local", "docker", "production"], 
                       default="local", nargs="?")
    parser.add_argument("--skip-tests", action="store_true",
                       help="Skip running tests before deployment")
    
    args = parser.parse_args()
    deploy(args.target, args.skip_tests)
