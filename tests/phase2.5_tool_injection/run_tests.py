#!/usr/bin/env python3
"""Test runner for Phase 2.5 tool injection tests."""

import argparse
import subprocess
import sys
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False, parallel=False):
    """Run the specified tests."""
    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    # Add test directory
    test_dir = Path(__file__).parent
    cmd.append(str(test_dir))

    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    # Add coverage
    if coverage:
        cmd.extend(["--cov=agenthub", "--cov-report=html", "--cov-report=term"])

    # Add parallel execution
    if parallel:
        cmd.extend(["-n", "auto"])

    # Filter by test type
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "performance":
        cmd.extend(["-m", "performance"])
    elif test_type == "mcp":
        cmd.extend(["-m", "mcp"])
    elif test_type == "concurrent":
        cmd.extend(["-m", "concurrent"])
    elif test_type == "slow":
        cmd.extend(["-m", "slow"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])

    # Add test discovery
    cmd.extend(["--tb=short", "--strict-markers"])

    print(f"Running tests: {' '.join(cmd)}")
    print("=" * 60)

    # Run tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent)
    return result.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run Phase 2.5 tool injection tests")
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=[
            "all",
            "unit",
            "integration",
            "performance",
            "mcp",
            "concurrent",
            "slow",
            "fast",
        ],
        help="Type of tests to run",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "-c", "--coverage", action="store_true", help="Run with coverage reporting"
    )
    parser.add_argument(
        "-p", "--parallel", action="store_true", help="Run tests in parallel"
    )

    args = parser.parse_args()

    # Check if pytest is available
    try:
        subprocess.run(
            ["python", "-m", "pytest", "--version"], capture_output=True, check=True
        )
    except subprocess.CalledProcessError:
        print("Error: pytest is not installed. Please install it with:")
        print("pip install pytest pytest-cov pytest-xdist")
        sys.exit(1)

    # Check if coverage is requested but not available
    if args.coverage:
        try:
            subprocess.run(
                ["python", "-m", "pytest", "--help"], capture_output=True, check=True
            )
        except subprocess.CalledProcessError:
            print("Error: pytest-cov is not installed. Please install it with:")
            print("pip install pytest-cov")
            sys.exit(1)

    # Check if parallel is requested but not available
    if args.parallel:
        try:
            subprocess.run(
                ["python", "-m", "pytest", "--help"], capture_output=True, check=True
            )
        except subprocess.CalledProcessError:
            print("Error: pytest-xdist is not installed. Please install it with:")
            print("pip install pytest-xdist")
            sys.exit(1)

    # Run tests
    exit_code = run_tests(
        test_type=args.test_type,
        verbose=args.verbose,
        coverage=args.coverage,
        parallel=args.parallel,
    )

    if exit_code == 0:
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
    else:
        print("\n" + "=" * 60)
        print("❌ Some tests failed!")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
