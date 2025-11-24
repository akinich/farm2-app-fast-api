# 🚀 Test Commands Cheatsheet

Quick reference for running tests in the Farm Management System.

---

## Basic Commands

```bash
# Run all tests
pytest tests/ -v

# Run all tests (short output)
pytest tests/

# Run with detailed output
pytest tests/ -vv

# Run quietly (only show failures)
pytest tests/ -q
```

---

## Run Specific Tests

```bash
# Run single test file
pytest tests/test_auth.py -v

# Run single test class
pytest tests/test_auth.py::TestLogin -v

# Run single test method
pytest tests/test_auth.py::TestLogin::test_login_with_valid_credentials -v

# Run tests matching name pattern
pytest tests/ -k "login" -v

# Run tests matching multiple patterns
pytest tests/ -k "login or health" -v
```

---

## Run by Marker

```bash
# Authentication tests only
pytest tests/ -m auth -v

# Database tests only
pytest tests/ -m database -v

# Health check tests only
pytest tests/ -m health -v

# Integration tests only
pytest tests/ -m integration -v

# Skip slow tests
pytest tests/ -m "not slow" -v

# Multiple markers (AND)
pytest tests/ -m "auth and integration" -v

# Multiple markers (OR)
pytest tests/ -m "auth or database" -v
```

---

## Debugging

```bash
# Stop on first failure
pytest tests/ -x

# Stop after N failures
pytest tests/ --maxfail=3

# Show print statements
pytest tests/ -s

# Show local variables on failure
pytest tests/ -l

# Full error traceback
pytest tests/ --tb=long

# Short error traceback
pytest tests/ --tb=short

# No traceback
pytest tests/ --tb=no

# Drop into debugger on failure
pytest tests/ --pdb
```

---

## Re-running Tests

```bash
# Run only failed tests from last run
pytest tests/ --lf

# Run failed tests first, then others
pytest tests/ --ff

# Show test durations (slowest 10)
pytest tests/ --durations=10

# Show all test durations
pytest tests/ --durations=0
```

---

## Coverage

```bash
# Run with coverage
pytest tests/ --cov=app

# Coverage with HTML report
pytest tests/ --cov=app --cov-report=html

# Coverage with terminal report
pytest tests/ --cov=app --cov-report=term

# Coverage for specific module
pytest tests/ --cov=app.auth --cov-report=html

# Coverage with missing lines
pytest tests/ --cov=app --cov-report=term-missing
```

---

## Output Control

```bash
# Verbose (show test names)
pytest tests/ -v

# Very verbose (show parameters)
pytest tests/ -vv

# Quiet (minimal output)
pytest tests/ -q

# No header/summary
pytest tests/ --no-header

# Show slowest N tests
pytest tests/ --durations=5

# Show captured output on failure
pytest tests/ --capture=no
```

---

## Warnings

```bash
# Show all warnings
pytest tests/ -W all

# Ignore warnings
pytest tests/ --disable-warnings

# Treat warnings as errors
pytest tests/ -W error

# Show specific warning type
pytest tests/ -W ignore::DeprecationWarning
```

---

## Test Selection

```bash
# Run first N tests
pytest tests/ --maxfail=5 --tb=line

# Run tests in random order
pytest tests/ --random-order

# Run tests in reverse order
pytest tests/ --reverse

# Run specific percentage of tests
pytest tests/ --random-order-bucket=class
```

---

## Parallel Execution

```bash
# Install pytest-xdist first
pip install pytest-xdist

# Run tests in parallel (auto detect CPUs)
pytest tests/ -n auto

# Run tests on 4 CPUs
pytest tests/ -n 4

# Distribute by test file
pytest tests/ -n auto --dist=loadfile

# Distribute by test class
pytest tests/ -n auto --dist=loadscope
```

---

## Common Workflows

### Quick Check (Fast Tests Only)

```bash
pytest tests/ -m "not slow" -q
```

### Full Test Suite with Coverage

```bash
pytest tests/ -v --cov=app --cov-report=html --durations=10
```

### Debug Single Failing Test

```bash
pytest tests/test_auth.py::TestLogin::test_login_with_valid_credentials -vv -s --tb=long
```

### Run Failed Tests Only

```bash
pytest tests/ --lf -v
```

### Integration Tests Only

```bash
pytest tests/ -m integration -v
```

### Watch Mode (re-run on file change)

```bash
# Install pytest-watch first
pip install pytest-watch

# Run in watch mode
ptw tests/ -- -v
```

---

## CI/CD Commands

### GitHub Actions

```bash
# Run with XML output for CI
pytest tests/ --junitxml=test-results.xml

# Run with coverage for CI
pytest tests/ --cov=app --cov-report=xml --junitxml=test-results.xml
```

### Docker

```bash
# Run tests in Docker container
docker run -v $(pwd):/app -w /app python:3.11 pytest tests/ -v

# Run with coverage in Docker
docker run -v $(pwd):/app -w /app python:3.11 sh -c "pip install -r requirements.txt && pytest tests/ --cov=app"
```

---

## Environment Variables

```bash
# Use test database
DATABASE_URL=postgresql://localhost/farm_test pytest tests/

# Set log level for tests
LOG_LEVEL=DEBUG pytest tests/ -v

# Run with specific environment
APP_ENV=test pytest tests/
```

---

## Verification

```bash
# Verify test infrastructure
python tests/verify_tests.py

# List all tests (don't run)
pytest tests/ --collect-only

# Show available markers
pytest tests/ --markers

# Show available fixtures
pytest tests/ --fixtures

# Show test configuration
pytest tests/ --version
```

---

## Performance

```bash
# Profile test execution
pytest tests/ --profile

# Profile with SVG output
pytest tests/ --profile-svg

# Benchmark tests
pip install pytest-benchmark
pytest tests/ --benchmark-only
```

---

## Useful Combinations

### Development (fast feedback)

```bash
pytest tests/ -x -v --tb=short -m "not slow"
```

### Pre-commit (comprehensive)

```bash
pytest tests/ -v --cov=app --cov-report=term-missing --durations=5
```

### CI/CD (full suite)

```bash
pytest tests/ -v --cov=app --cov-report=xml --junitxml=test-results.xml --maxfail=10
```

### Debugging (detailed)

```bash
pytest tests/test_auth.py -vv -s --tb=long --showlocals --pdb
```

---

## Tips & Tricks

1. **Use `.pytest_cache` for faster reruns**
   ```bash
   pytest tests/ --lf  # Rerun last failed
   ```

2. **Show which tests will run without running them**
   ```bash
   pytest tests/ --collect-only
   ```

3. **Run tests matching multiple patterns**
   ```bash
   pytest tests/ -k "login or logout or password"
   ```

4. **Get test count by marker**
   ```bash
   pytest tests/ -m auth --collect-only -q | wc -l
   ```

5. **Create custom markers in pytest.ini**
   ```ini
   [pytest]
   markers =
       smoke: Quick smoke tests
       regression: Regression tests
   ```

---

**Quick Reference:**

| Command | Description |
|---------|-------------|
| `-v` | Verbose output |
| `-s` | Show print statements |
| `-x` | Stop on first failure |
| `-k PATTERN` | Run tests matching pattern |
| `-m MARKER` | Run tests with marker |
| `--lf` | Run last failed tests |
| `--cov=app` | Run with coverage |
| `--pdb` | Drop into debugger on failure |

---

**Version:** 1.0.0
**Last Updated:** 2025-11-24
