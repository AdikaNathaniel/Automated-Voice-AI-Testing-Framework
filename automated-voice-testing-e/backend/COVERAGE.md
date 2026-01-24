# Code Coverage Guide

This document explains how to use code coverage in the Voice AI Testing Framework.

## Overview

We use **pytest-cov** (a pytest plugin for coverage.py) to measure code coverage. Coverage helps identify which parts of the codebase are tested and which are not, ensuring high code quality and test thoroughness.

## Quick Start

### Run tests with coverage (default)

Coverage is automatically generated when running tests:

```bash
# Run all tests with coverage (generates all reports)
../venv/bin/pytest

# Run specific test file with coverage
../venv/bin/pytest tests/test_soundhound.py

# Run tests without coverage (faster)
../venv/bin/pytest --no-cov
```

### View coverage reports

Coverage reports are generated in multiple formats:

1. **Terminal Report**: Displayed after test execution
2. **HTML Report**: Open `htmlcov/index.html` in a browser
3. **XML Report**: `coverage.xml` (for CI/CD integration)

## Configuration Files

### pytest.ini

Coverage is configured in `pytest.ini`:

```ini
[pytest]
addopts =
    --cov=.                              # Measure coverage
    --cov-report=term-missing:skip-covered  # Terminal report
    --cov-report=html                    # HTML report
    --cov-report=xml                     # XML report
    --cov-branch                         # Branch coverage
```

### .coveragerc

Detailed coverage settings in `.coveragerc`:

- **What to measure**: All source files except tests, migrations, etc.
- **Branch coverage**: Enabled (measures if/else branches)
- **Exclusions**: Test files, venv, alembic, __pycache__, etc.
- **Report format**: HTML, XML, terminal

## Coverage Commands

### Basic Commands

```bash
# Run all tests with coverage
../venv/bin/pytest

# Run tests without coverage (faster)
../venv/bin/pytest --no-cov

# Run tests with minimal coverage output
../venv/bin/pytest --cov-report=term

# Run tests and show only missing lines
../venv/bin/pytest --cov-report=term-missing
```

### Targeted Coverage

```bash
# Coverage for specific package
../venv/bin/pytest --cov=api tests/

# Coverage for specific module
../venv/bin/pytest --cov=integrations/houndify tests/test_soundhound.py

# Coverage with minimum threshold (fail if below)
../venv/bin/pytest --cov --cov-fail-under=80
```

### Report Formats

```bash
# Generate only HTML report
../venv/bin/pytest --cov-report=html --cov-report=

# Generate only XML report (for CI/CD)
../venv/bin/pytest --cov-report=xml --cov-report=

# Generate only terminal report
../venv/bin/pytest --cov-report=term

# Skip files with 100% coverage in terminal
../venv/bin/pytest --cov-report=term-missing:skip-covered
```

## Understanding Coverage Reports

### Terminal Report

```
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
api/main.py                       34     10    71%   15-25, 40-45
api/routes/test_cases.py         106      5    95%   120-125
validators/intent_validator.py    50      5    90%   265-269
------------------------------------------------------------
TOTAL                           4836   4342    10%
```

- **Stmts**: Total statements in file
- **Miss**: Statements not covered by tests
- **Cover**: Coverage percentage
- **Missing**: Line numbers not covered

### HTML Report

1. Open `htmlcov/index.html` in browser
2. Click on files to see detailed line-by-line coverage
3. Red lines = not covered
4. Green lines = covered
5. Yellow lines = partially covered (branches)

### Branch Coverage

Branch coverage measures whether all code paths are tested:

```python
# Requires 2 tests: one where condition is True, one where False
if condition:
    do_something()  # Branch 1
else:
    do_something_else()  # Branch 2
```

## Coverage Targets

### Current Status

- **Overall Coverage**: ~10% (early development)
- **Target**: >80% for production

### Per-Component Targets

- **API Routes**: >90%
- **Services**: >85%
- **Validators**: >90%
- **Models**: >95%
- **Integrations**: >80%

### Excluded from Coverage

These files are excluded (see `.coveragerc`):

- Test files (`tests/`, `test_*.py`)
- Database migrations (`alembic/`)
- Virtual environments (`venv/`, `.venv/`)
- Python cache (`__pycache__/`, `*.pyc`)
- Configuration files (`conftest.py`, `setup.py`)
- Development artifacts (`*/build/`, `*/dist/`)

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run tests with coverage
  run: |
    pytest --cov --cov-report=xml

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
    fail_ci_if_error: true
```

### GitLab CI Example

```yaml
test:
  script:
    - pytest --cov --cov-report=xml --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## Best Practices

### Writing Tests for Coverage

1. **Test all branches**: Ensure if/else, try/except are covered
2. **Test edge cases**: Empty inputs, None values, extremes
3. **Test error paths**: Exceptions, validation failures
4. **Test success paths**: Normal operation, happy paths

### Improving Coverage

```bash
# 1. Find uncovered code
../venv/bin/pytest --cov-report=term-missing

# 2. Look at HTML report for details
open htmlcov/index.html

# 3. Write tests for missing lines
# 4. Re-run to verify improvement
../venv/bin/pytest --cov
```

### Coverage Exceptions

Some code should be excluded from coverage:

```python
# Use pragma: no cover for debugging code
def debug_only():  # pragma: no cover
    print("Debug information")

# Abstract methods (already excluded)
@abstractmethod
def must_override(self):
    raise NotImplementedError

# Type checking imports (already excluded)
if TYPE_CHECKING:
    from .models import User
```

## Troubleshooting

### Coverage not showing

```bash
# Ensure pytest-cov is installed
../venv/bin/pip list | grep cov

# Check configuration
cat pytest.ini
cat .coveragerc
```

### HTML report not updating

```bash
# Clear old coverage data
rm -rf .coverage htmlcov/

# Re-run tests
../venv/bin/pytest
```

### Coverage too low

```bash
# Find files with low coverage
../venv/bin/pytest --cov-report=term | grep -E "[0-5][0-9]%"

# Focus on one module
../venv/bin/pytest --cov=api/routes tests/test_routes.py
```

## Advanced Usage

### Coverage Contexts

Track which tests cover which code:

```bash
# Enable contexts
../venv/bin/pytest --cov --cov-context=test

# View in HTML report (shows which tests cover each line)
```

### Parallel Coverage

For parallel test execution:

```bash
# Run tests in parallel (requires pytest-xdist)
../venv/bin/pytest -n auto --cov

# Combine coverage data
coverage combine

# Generate reports
coverage report
coverage html
```

### Coverage Diff

Compare coverage between branches:

```bash
# Generate coverage on main branch
git checkout main
../venv/bin/pytest --cov
cp .coverage .coverage.main

# Generate coverage on feature branch
git checkout feature-branch
../venv/bin/pytest --cov

# Compare
coverage report --data-file=.coverage > coverage.feature
coverage report --data-file=.coverage.main > coverage.main
diff coverage.main coverage.feature
```

## Resources

- **pytest-cov documentation**: https://pytest-cov.readthedocs.io/
- **coverage.py documentation**: https://coverage.readthedocs.io/
- **Coverage best practices**: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html

## Summary

- Coverage is **automatically enabled** when running pytest
- Reports are generated in **3 formats**: terminal, HTML, XML
- Target coverage: **>80%** for production
- Use `.coveragerc` to **configure** what's measured
- Use HTML reports to **visualize** missing coverage
- Use `--cov-fail-under` in CI/CD to **enforce** coverage standards
