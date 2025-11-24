# 🧪 Farm Management System - Test Suite

## Overview

Comprehensive test suite for the Farm Management System FastAPI backend, covering database operations, authentication, and API endpoints.

**Test Statistics:**
- **134 total test cases**
- **3 test modules** (database, auth, health)
- **7 shared fixtures**
- **6 test markers** for organization

---

## 📁 Test Structure

```
tests/
├── README.md              # This file
├── __init__.py           # Test package marker
├── conftest.py           # Shared fixtures and test configuration
├── pytest.ini            # Pytest configuration (in parent directory)
├── verify_tests.py       # Test infrastructure verification script
├── test_database.py      # Database connection and query tests (38 tests)
├── test_auth.py          # Authentication and JWT tests (52 tests)
└── test_health.py        # Health check and API status tests (44 tests)
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pytest pytest-asyncio httpx
```

### 2. Configure Test Database

Update your `.env` file with test database credentials:

```bash
# Use a separate test database to avoid affecting production data
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/farm_test

# Test JWT secrets (different from production)
JWT_SECRET_KEY=your_test_jwt_secret_key
JWT_REFRESH_SECRET_KEY=your_test_jwt_refresh_secret_key
```

### 3. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run tests with specific marker
pytest tests/ -m auth -v

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 📦 Test Modules

### `test_database.py` (38 tests)

Tests database connection, query helpers, and transaction management.

**Test Classes:**
- `TestDatabaseConnection` - Database pool and health checks
- `TestQueryHelpers` - fetch_one, fetch_all, parameter binding
- `TestExecuteQuery` - INSERT/UPDATE/DELETE with RETURNING clauses
- `TestTransactions` - Transaction commit/rollback behavior
- `TestUtilityFunctions` - build_where_clause, paginate_query

**Example:**
```python
async def test_fetch_one_returns_dict():
    result = await fetch_one("SELECT 1 as number, 'test' as text")
    assert result["number"] == 1
    assert result["text"] == "test"
```

---

### `test_auth.py` (52 tests)

Tests authentication endpoints, JWT tokens, and password management.

**Test Classes:**
- `TestJWTTokens` - Token creation and verification
- `TestLogin` - Login endpoint (valid/invalid credentials, inactive users)
- `TestTokenRefresh` - Refresh token endpoint
- `TestLogout` - Logout and session revocation
- `TestGetCurrentUser` - Get current user endpoint
- `TestChangePassword` - Password change flow
- `TestProfile` - User profile get/update
- `TestPasswordReset` - Password reset flow

**Key Tests:**
```python
async def test_login_with_valid_credentials(client, test_admin_user):
    response = await client.post("/api/v1/auth/login", json={
        "email": test_admin_user["email"],
        "password": test_admin_user["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

---

### `test_health.py` (44 tests)

Tests health check endpoints, API documentation, and error handling.

**Test Classes:**
- `TestRootEndpoint` - Root endpoint and API info
- `TestHealthCheck` - Health status and service monitoring
- `TestPingEndpoint` - Quick uptime checks
- `TestAPIDocumentation` - Swagger/ReDoc/OpenAPI schema
- `TestErrorHandling` - 404, 405, validation errors
- `TestCORS` - CORS middleware configuration
- `TestRateLimiting` - Rate limiting behavior

**Example:**
```python
async def test_health_check_returns_healthy(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

---

## 🎯 Test Fixtures

Defined in `conftest.py`:

| Fixture | Description | Returns |
|---------|-------------|---------|
| `event_loop` | Session-scoped event loop | Event loop |
| `setup_test_database` | Connects/disconnects database | None |
| `cleanup_database` | Cleans test data after each test | None |
| `client` | Async HTTP client for API testing | AsyncClient |
| `test_admin_user` | Creates test admin user | User dict |
| `test_regular_user` | Creates test regular user | User dict |
| `test_inactive_user` | Creates inactive user | User dict |
| `admin_token` | JWT token for admin user | Token string |
| `user_token` | JWT token for regular user | Token string |
| `admin_headers` | Authorization headers for admin | Headers dict |
| `user_headers` | Authorization headers for user | Headers dict |

**Usage Example:**
```python
async def test_admin_only_endpoint(client, admin_headers):
    response = await client.get(
        "/api/v1/admin/users",
        headers=admin_headers
    )
    assert response.status_code == 200
```

---

## 🏷️ Test Markers

Use markers to organize and filter tests:

```bash
# Run only authentication tests
pytest tests/ -m auth -v

# Run only database tests
pytest tests/ -m database -v

# Skip slow tests
pytest tests/ -m "not slow" -v

# Run integration tests only
pytest tests/ -m integration -v
```

**Available Markers:**
- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (require database)
- `@pytest.mark.slow` - Slow tests (>1 second)
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.database` - Database tests
- `@pytest.mark.health` - Health check tests

---

## ⚙️ Configuration

### `pytest.ini`

Located in `/backend/pytest.ini`:

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
addopts = -v --tb=short --strict-markers

markers =
    unit: Unit tests
    integration: Integration tests
    auth: Authentication tests
    database: Database tests
    health: Health check tests
    slow: Slow tests
```

### Database Cleanup

Tests automatically clean up data after each test using the `cleanup_database` fixture. The cleanup deletes:
- Login attempts
- Active sessions
- Activity logs
- Webhook deliveries
- Webhooks
- Email queue
- API keys
- Test users

**Note:** Uses `@pytest.fixture(autouse=True)` to run automatically after each test.

---

## 📊 Test Coverage

To generate test coverage reports:

```bash
# Install coverage plugin
pip install pytest-cov

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html

# View HTML report
open htmlcov/index.html
```

**Current Coverage Areas:**
- ✅ Database connection and queries
- ✅ Authentication and JWT tokens
- ✅ Login/logout flows
- ✅ Password reset and change
- ✅ User profile management
- ✅ Health checks and API status
- ✅ Error handling
- ⚠️ Tickets module (Priority 2)
- ⚠️ Webhooks (Priority 3)
- ⚠️ Email queue (Priority 3)

---

## 🐛 Debugging Tests

### Run Single Test

```bash
pytest tests/test_auth.py::TestLogin::test_login_with_valid_credentials -v
```

### Show Print Statements

```bash
pytest tests/ -v -s
```

### Stop on First Failure

```bash
pytest tests/ -v -x
```

### Run Failed Tests Only

```bash
pytest tests/ -v --lf
```

### Verbose Error Output

```bash
pytest tests/ -v --tb=long
```

---

## 💡 Best Practices

### 1. **Use Fixtures for Setup**

```python
async def test_with_user(client, test_admin_user):
    # test_admin_user is automatically created and cleaned up
    assert test_admin_user["role"] == "Admin"
```

### 2. **Use Markers for Organization**

```python
@pytest.mark.auth
@pytest.mark.integration
async def test_login_creates_session(client, test_admin_user):
    # Test code here
```

### 3. **Test Both Success and Failure Cases**

```python
async def test_login_with_valid_credentials(client, test_admin_user):
    # Test success case
    assert response.status_code == 200

async def test_login_with_wrong_password(client, test_admin_user):
    # Test failure case
    assert response.status_code == 401
```

### 4. **Use Descriptive Test Names**

```python
# Good
async def test_login_with_inactive_user_returns_403()

# Bad
async def test_login_fail()
```

### 5. **Keep Tests Independent**

Each test should be able to run in isolation. Use fixtures for setup and the `cleanup_database` fixture handles teardown.

---

## 🔧 Troubleshooting

### Database Connection Errors

```
asyncpg.exceptions.InvalidCatalogNameError: database "farm_test" does not exist
```

**Solution:** Create the test database:
```bash
createdb farm_test
```

### JWT Decode Errors

```
JWTError: Signature verification failed
```

**Solution:** Ensure `JWT_SECRET_KEY` and `JWT_REFRESH_SECRET_KEY` are set in `.env`

### Import Errors

```
ModuleNotFoundError: No module named 'app'
```

**Solution:** Run pytest from the `/backend` directory:
```bash
cd backend
pytest tests/ -v
```

### Async Fixture Errors

```
ScopeMismatch: You tried to access the function scoped fixture event_loop
```

**Solution:** Ensure `asyncio_mode = auto` is set in `pytest.ini`

---

## 📈 Next Steps

### Priority 2: Core Features (Tickets, Users, API Keys)

Add tests for:
- Tickets CRUD operations
- User management
- API key authentication
- Module permissions

### Priority 3: Advanced Features (Webhooks, Email)

Add tests for:
- Webhook delivery and retry logic
- Email queue processing
- Telegram notifications
- Settings management

### CI/CD Integration

Set up GitHub Actions to run tests automatically:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/ -v
```

---

## 📝 Writing New Tests

### Template for New Test File

```python
"""
Test module description
"""

import pytest
from httpx import AsyncClient


@pytest.mark.your_marker
class TestYourFeature:
    """Test class description."""

    async def test_something(self, client: AsyncClient):
        """Test description."""
        # Arrange
        data = {"key": "value"}

        # Act
        response = await client.post("/api/v1/endpoint", json=data)

        # Assert
        assert response.status_code == 200
        assert response.json()["key"] == "value"
```

---

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [HTTPX Test Client](https://www.python-httpx.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

## ✅ Verification

Run the verification script to check test infrastructure:

```bash
python tests/verify_tests.py
```

This will show:
- ✓ All test files present
- ✓ Fixtures defined correctly
- ✓ Test counts per module
- ✓ Pytest configuration valid

---

**Version:** 1.0.0
**Last Updated:** 2025-11-24
**Test Coverage:** Priority 1 (Foundation + Authentication) Complete
