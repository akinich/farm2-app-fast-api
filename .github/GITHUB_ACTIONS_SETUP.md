# 🤖 GitHub Actions CI/CD Setup Guide

## Overview

This guide explains how GitHub Actions automatically tests your code **before** it reaches production.

**What it does:**
- ✅ Runs 134 tests automatically when you push code
- ✅ Tests run in GitHub's cloud (no local setup needed)
- ✅ Blocks merging if tests fail
- ✅ Shows green checkmark ✅ or red X ❌ on pull requests

---

## 🚀 Quick Start (3 Steps)

### Step 1: Add GitHub Secrets (2 minutes)

GitHub Secrets store sensitive information securely.

**How to add secrets:**

1. Go to your GitHub repository
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret**
5. Add these 2 secrets:

| Secret Name | Value | Where to Find It |
|------------|-------|------------------|
| `JWT_SECRET_KEY` | Your JWT secret | From your Render environment variables or `.env.example` |
| `JWT_REFRESH_SECRET_KEY` | Your JWT refresh secret | From your Render environment variables or `.env.example` |

**Example:**
```
Secret name: JWT_SECRET_KEY
Secret value: your_actual_jwt_secret_key_here_123456789
```

**✅ Click "Add secret"** for each one.

---

### Step 2: Push the Workflow File

The workflow file is already created at `.github/workflows/test.yml`

Just commit and push it:

```bash
git add .github/workflows/test.yml
git commit -m "Add GitHub Actions CI/CD for automated testing"
git push origin main
```

---

### Step 3: Watch It Work! 🎉

**Next time you push to a branch:**

1. Go to your GitHub repository
2. Click the **Actions** tab
3. You'll see tests running automatically! ⚡

**On Pull Requests:**
- Green checkmark ✅ = Tests passed, safe to merge
- Red X ❌ = Tests failed, fix before merging

---

## 📋 How It Works

### What Triggers Tests?

Tests run automatically when:

1. **You create a pull request to main**
   ```
   Feature branch → PR to main → Tests run ✅
   ```

2. **Claude pushes to a claude/* branch**
   ```
   Claude fixes code → Push to claude/fix-bug → Tests run ✅
   ```

3. **You manually trigger tests**
   - Go to Actions tab → Select workflow → Run workflow

---

### What Happens During a Test Run?

```
1. 📥 GitHub checks out your code
2. 🐍 Sets up Python 3.11
3. 📦 Installs dependencies (FastAPI, pytest, etc.)
4. 🗄️ Starts PostgreSQL database (temporary, just for tests)
5. ⚙️ Creates test .env file
6. 🔄 Runs database migrations
7. 🧪 Runs all 134 tests
8. ✅ Reports results (pass/fail)
```

**Total time:** ~3-5 minutes

---

### The Test Database

**Good news:** You don't need to set up a test database!

GitHub Actions automatically:
- Spins up a PostgreSQL container
- Creates the `farm_test` database
- Runs your migrations
- Tears it down after tests finish

**Cost:** $0 (GitHub Actions is free for public repos, 2000 minutes/month for private repos)

---

## 🎯 Your New Workflow

### Before GitHub Actions:
```
You → Push code → Render deploys → Users see bugs 😱
```

### After GitHub Actions:
```
You → Push to branch → GitHub runs tests
  ↓
✅ Tests pass → Create PR → Merge → Render deploys → Happy users! 😊
  ↓
❌ Tests fail → Fix bugs → Push again → Tests pass → Then merge
```

---

## 🔍 Reading Test Results

### Green Checkmark ✅

```
✅ All checks have passed
1 successful check
```

**What this means:**
- All 134 tests passed
- Safe to merge to main
- Code won't break production

---

### Red X ❌

```
❌ Some checks were not successful
1 failing check
```

**What to do:**
1. Click **Details** next to the red X
2. Scroll down to see which tests failed
3. Fix the failing tests
4. Push your fix
5. Tests run automatically again

**Example failure:**
```
FAILED tests/test_auth.py::TestLogin::test_login_with_valid_credentials
AssertionError: assert 401 == 200
```

This tells you:
- **File:** `test_auth.py`
- **Test:** `test_login_with_valid_credentials`
- **Problem:** Expected status 200, got 401 (unauthorized)

---

## ⚙️ Configuration Details

### Workflow File Location

```
.github/workflows/test.yml
```

This file tells GitHub Actions what to do.

---

### When Tests Run

Defined in the workflow file:

```yaml
on:
  pull_request:
    branches: [main]      # Run on PRs to main
  push:
    branches:
      - 'claude/**'       # Run on claude/* branches
  workflow_dispatch:      # Allow manual runs
```

**You can customize this!**

For example, to run on ALL branches:
```yaml
on:
  push:
    branches: ['**']
```

---

### Secrets Used

| Secret | Purpose | Required? |
|--------|---------|-----------|
| `JWT_SECRET_KEY` | Sign JWT tokens in tests | Optional* |
| `JWT_REFRESH_SECRET_KEY` | Sign refresh tokens | Optional* |

*If not provided, defaults to test values (works fine for testing)

**Note:** The test database credentials are hardcoded in the workflow (username: `postgres`, password: `postgres`) because it's a temporary database that only exists during the test run.

---

## 🛡️ Branch Protection (Optional)

Want to **force tests to pass** before merging?

### Setup Branch Protection:

1. Go to **Settings** → **Branches**
2. Click **Add rule**
3. Branch name pattern: `main`
4. Check ✅ **Require status checks to pass before merging**
5. Select: **Test Suite**
6. Click **Create**

**Now:**
- ❌ You **cannot** merge if tests fail
- ✅ You **must** fix failing tests first

---

## 📊 Viewing Test History

1. Go to **Actions** tab
2. See all test runs (past and present)
3. Click any run to see details
4. See which tests passed/failed

**Useful for:**
- Debugging flaky tests
- Seeing what broke when
- Tracking test performance

---

## 🐛 Troubleshooting

### "Secrets not found"

**Problem:** Tests can't find JWT_SECRET_KEY

**Solution:** Add secrets in Settings → Secrets and variables → Actions

---

### "Database connection failed"

**Problem:** Tests can't connect to database

**Solution:** This shouldn't happen because GitHub Actions provides the database automatically. If it does:
1. Check the workflow logs
2. Ensure PostgreSQL service is running
3. Check DATABASE_URL in the workflow file

---

### "Tests timeout"

**Problem:** Tests take too long (>10 minutes)

**Solution:**
- Increase timeout in workflow file: `timeout-minutes: 20`
- Or optimize slow tests

---

### "Import errors"

**Problem:** `ModuleNotFoundError: No module named 'app'`

**Solution:** Check that `working-directory: backend` is set in test step

---

## 🎓 Understanding the Workflow File

### Key Sections:

#### 1. Triggers
```yaml
on:
  pull_request:
    branches: [main]
```
**When** tests run

#### 2. Services
```yaml
services:
  postgres:
    image: postgres:15
```
**Database** for tests (temporary)

#### 3. Steps
```yaml
steps:
  - name: Run tests
    run: pytest tests/ -v
```
**What** tests do

---

## 💡 Tips & Best Practices

### 1. **Check Status Before Merging**

Always look for the green checkmark ✅ before merging:

```
✅ All checks have passed
```

### 2. **Fix Failing Tests Quickly**

Red X ❌ means something broke. Fix it before merging:
- Click "Details" to see which test failed
- Fix the code
- Push again (tests re-run automatically)

### 3. **Use Draft PRs for WIP**

Creating a PR but not ready to merge? Mark it as **Draft**:
- Tests still run
- But prevents accidental merging

### 4. **Review Test Output**

Even if tests pass, review the output:
- Warnings might indicate issues
- Deprecation notices need attention

### 5. **Keep Tests Fast**

If tests take >5 minutes, consider:
- Adding markers to skip slow tests in CI
- Optimizing database queries in tests
- Running fewer tests in CI (only critical ones)

---

## 🚀 Advanced Features

### Run Specific Tests Only

Edit workflow to run only specific markers:

```yaml
- name: Run critical tests only
  run: pytest tests/ -m "auth or database" -v
```

### Add Test Coverage Reports

Install coverage and update workflow:

```yaml
- name: Run tests with coverage
  run: |
    pip install pytest-cov
    pytest tests/ --cov=app --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### Slack/Email Notifications

Get notified when tests fail:

```yaml
- name: Slack notification
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 📈 Next Steps

### After Setup:

1. ✅ **Test it works**
   - Push a small change to a branch
   - Watch tests run in Actions tab
   - Verify green checkmark appears

2. ✅ **Add branch protection** (optional)
   - Prevent merging if tests fail
   - Forces everyone to fix bugs first

3. ✅ **Add more tests** (Priority 2 & 3)
   - Tickets module tests
   - Webhooks tests
   - Email queue tests

4. ✅ **Monitor regularly**
   - Check Actions tab weekly
   - Fix flaky tests
   - Keep tests fast

---

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [PostgreSQL in GitHub Actions](https://docs.github.com/en/actions/using-containerized-services/creating-postgresql-service-containers)

---

## ✅ Verification Checklist

After setting up GitHub Actions, verify:

- [ ] GitHub Secrets are added (JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY)
- [ ] Workflow file is in `.github/workflows/test.yml`
- [ ] File is committed and pushed to main
- [ ] Can see "Actions" tab in GitHub repository
- [ ] Tests run when you push to a branch
- [ ] Green checkmark ✅ appears on pull requests

---

## 🆘 Need Help?

If something isn't working:

1. Check the **Actions** tab in GitHub
2. Click on the failed run
3. Expand the failing step
4. Read the error message
5. Common issues are in the Troubleshooting section above

---

**Version:** 1.0.0
**Last Updated:** 2025-11-24
**Status:** Ready to use! 🚀
