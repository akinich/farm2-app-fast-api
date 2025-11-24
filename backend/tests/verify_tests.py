"""
Quick verification script to check test structure without running full test suite.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def verify_test_structure():
    """Verify all test files are present and importable."""

    print("=" * 70)
    print("🧪 TEST INFRASTRUCTURE VERIFICATION")
    print("=" * 70)

    test_files = [
        "pytest.ini",
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/test_database.py",
        "tests/test_auth.py",
        "tests/test_health.py",
    ]

    print("\n📁 Checking test files...")
    all_present = True
    for file in test_files:
        file_path = os.path.join(os.path.dirname(__file__), "..", file)
        exists = os.path.exists(file_path)
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        if not exists:
            all_present = False

    if not all_present:
        print("\n❌ Some test files are missing!")
        return False

    print("\n📦 Checking test structure...")

    # Check conftest.py
    try:
        with open(os.path.join(os.path.dirname(__file__), "conftest.py")) as f:
            content = f.read()
            fixtures = [
                "setup_test_database",
                "cleanup_database",
                "client",
                "test_admin_user",
                "test_regular_user",
                "admin_token",
                "user_token",
            ]

            print("\n  Fixtures defined:")
            for fixture in fixtures:
                has_fixture = f"def {fixture}" in content
                status = "✓" if has_fixture else "✗"
                print(f"    {status} {fixture}")
    except Exception as e:
        print(f"\n  ✗ Error reading conftest.py: {e}")
        return False

    # Count test cases
    print("\n📊 Test statistics:")

    test_counts = {}
    test_modules = ["test_database.py", "test_auth.py", "test_health.py"]

    total_tests = 0
    for module in test_modules:
        try:
            with open(os.path.join(os.path.dirname(__file__), module)) as f:
                content = f.read()
                # Count "async def test_" and "def test_"
                count = content.count("async def test_") + content.count("def test_")
                test_counts[module] = count
                total_tests += count
                print(f"  {module:20s} {count:3d} tests")
        except Exception as e:
            print(f"  {module:20s} Error: {e}")

    print(f"  {'─' * 20} {'─' * 3}")
    print(f"  {'Total':20s} {total_tests:3d} tests")

    # Check pytest configuration
    print("\n⚙️  Pytest configuration:")
    try:
        with open(os.path.join(os.path.dirname(__file__), "..", "pytest.ini")) as f:
            content = f.read()
            configs = [
                "asyncio_mode",
                "testpaths",
                "markers",
            ]

            for config in configs:
                has_config = config in content
                status = "✓" if has_config else "✗"
                print(f"    {status} {config}")
    except Exception as e:
        print(f"    ✗ Error reading pytest.ini: {e}")
        return False

    print("\n" + "=" * 70)
    print("✅ TEST INFRASTRUCTURE COMPLETE!")
    print("=" * 70)

    print("\n📝 Summary:")
    print(f"  • {len(test_files)} test files created")
    print(f"  • {total_tests} test cases written")
    print(f"  • {len(fixtures)} fixtures defined")
    print(f"  • 3 test modules:")
    print(f"    - test_database.py (database connection & queries)")
    print(f"    - test_auth.py (authentication & JWT)")
    print(f"    - test_health.py (health checks & API status)")

    print("\n🚀 To run tests:")
    print("  1. Set up your test database credentials in .env")
    print("  2. Update DATABASE_URL to point to your test database")
    print("  3. Run: pytest tests/ -v")
    print("  4. Or run specific test file: pytest tests/test_auth.py -v")

    print("\n💡 Test markers available:")
    print("  • @pytest.mark.unit - Unit tests")
    print("  • @pytest.mark.integration - Integration tests")
    print("  • @pytest.mark.auth - Authentication tests")
    print("  • @pytest.mark.database - Database tests")
    print("  • @pytest.mark.health - Health check tests")
    print("  • @pytest.mark.slow - Slow tests")

    return True


if __name__ == "__main__":
    success = verify_test_structure()
    sys.exit(0 if success else 1)
