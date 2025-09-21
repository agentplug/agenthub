#!/usr/bin/env python3
"""
Test Runner for Web Tools

Runs all web tool tests including unit tests, integration tests,
and end-to-end tests.

Usage:
    python tests/builtin_tools/run_web_tests.py
"""

import sys
import subprocess
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def run_tests():
    """Run all web tool tests."""
    print("🧪 Running Web Tools Tests")
    print("=" * 50)
    
    test_files = [
        "tests/builtin_tools/web/test_web_search.py",
        "tests/builtin_tools/web/test_web_scrape.py", 
        "tests/builtin_tools/web/test_web_analysis.py",
        "tests/builtin_tools/web/test_web_tools_e2e.py"
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_file in test_files:
        print(f"\n📁 Running {test_file}...")
        
        try:
            # Run pytest for this test file
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                test_file,
                "-v",
                "--tb=short",
                "--no-header"
            ], capture_output=True, text=True, timeout=300)
            
            # Parse results
            if result.returncode == 0:
                print(f"✅ {test_file} - PASSED")
                # Count passed tests from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'PASSED' in line:
                        passed_tests += 1
                        total_tests += 1
            else:
                print(f"❌ {test_file} - FAILED")
                print(f"   Error: {result.stderr}")
                # Count failed tests from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'FAILED' in line:
                        failed_tests += 1
                        total_tests += 1
                    elif 'PASSED' in line:
                        passed_tests += 1
                        total_tests += 1
        
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file} - TIMEOUT")
            failed_tests += 1
            total_tests += 1
        except Exception as e:
            print(f"💥 {test_file} - ERROR: {e}")
            failed_tests += 1
            total_tests += 1
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success rate: {(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "No tests run")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n❌ {failed_tests} tests failed")
        return False


def run_demo():
    """Run the web tools demo."""
    print("\n🎬 Running Web Tools Demo")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable,
            "examples/tools/web_tools_demo.py"
        ], timeout=300)
        
        if result.returncode == 0:
            print("✅ Demo completed successfully!")
            return True
        else:
            print("❌ Demo failed!")
            return False
    
    except subprocess.TimeoutExpired:
        print("⏰ Demo timed out!")
        return False
    except Exception as e:
        print(f"💥 Demo error: {e}")
        return False


def main():
    """Main test runner."""
    print("🚀 AgentHub Web Tools Test Suite")
    print("=" * 60)
    
    start_time = time.time()
    
    # Run tests
    tests_passed = run_tests()
    
    # Run demo
    demo_passed = run_demo()
    
    total_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("🏁 Final Results")
    print("=" * 60)
    print(f"Tests: {'✅ PASSED' if tests_passed else '❌ FAILED'}")
    print(f"Demo: {'✅ PASSED' if demo_passed else '❌ FAILED'}")
    print(f"Total time: {total_time:.2f} seconds")
    
    if tests_passed and demo_passed:
        print("\n🎉 All tests and demo completed successfully!")
        print("Web tools are ready for production use!")
        return 0
    else:
        print("\n❌ Some tests or demo failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
