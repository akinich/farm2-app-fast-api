# ⚡ GitHub Actions - Quick Start (2 Minutes)

## 🎯 What You're Setting Up

**Automatic testing** that runs in GitHub's cloud whenever you push code.

---

## 📋 Setup Steps

### Step 1: Add Secrets (1 minute)

1. Go to your GitHub repo: `https://github.com/akinich/farm2-app-fast-api`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these 2 secrets:

```
Name: JWT_SECRET_KEY
Value: (copy from your Render environment variables)

Name: JWT_REFRESH_SECRET_KEY
Value: (copy from your Render environment variables)
```

**Don't have these?** They're in your Render dashboard under "Environment" tab.

**Or use these test values:**
```
JWT_SECRET_KEY: test_jwt_secret_key_for_github_actions_12345
JWT_REFRESH_SECRET_KEY: test_refresh_secret_key_for_github_actions_67890
```

---

### Step 2: Push the Workflow File (30 seconds)

```bash
git add .github/
git commit -m "Add GitHub Actions CI/CD"
git push origin main
```

---

### Step 3: Verify It Works (30 seconds)

1. Go to your GitHub repo
2. Click **Actions** tab (top menu)
3. You should see a workflow run starting! 🎉

---

## ✅ What Happens Now?

### Every time you (or Claude) push code:

1. **Tests run automatically** (takes ~3-5 minutes)
2. **You see results** in the Actions tab
3. **Pull requests show status:**
   - ✅ Green checkmark = Safe to merge
   - ❌ Red X = Fix bugs first

---

## 🎯 Your New Workflow

**Old way:**
```
Push code → Render deploys → Hope it works 🤞
```

**New way:**
```
Push code → Tests run → ✅ Pass → Merge → Deploy → Confident! 😎
```

---

## 🔧 Where Are the Secrets?

### Find your JWT secrets on Render:

1. Go to `https://dashboard.render.com`
2. Select your backend service
3. Click **Environment** (left sidebar)
4. Look for:
   - `JWT_SECRET_KEY`
   - `JWT_REFRESH_SECRET_KEY`
5. Copy the values

**If not there:** Use the test values from Step 1 above.

---

## 📊 Reading Results

### In the Actions Tab:

**Green checkmark ✅**
```
✅ All checks passed
```
→ All 134 tests passed! Safe to merge.

**Red X ❌**
```
❌ Some checks failed
```
→ Click "Details" to see which test failed.

---

## 🐛 Common Issues

### "Secrets not found"
→ Go back to Settings → Secrets and add them

### "Tests are taking too long"
→ Normal! First run takes ~5 minutes (GitHub installs everything)

### "Can't see Actions tab"
→ Make sure workflow file is pushed to main branch

---

## 💡 Pro Tips

1. **Check Actions tab** after pushing
2. **Look for green checkmark** before merging PRs
3. **Read test output** if something fails
4. **Branch protection** (optional): Settings → Branches → Require status checks

---

## 🆘 Need Help?

Read the full guide: `.github/GITHUB_ACTIONS_SETUP.md`

Or check workflow logs in the Actions tab.

---

**That's it! You're done! 🎉**

Now tests run automatically every time you push code. No local setup needed!
