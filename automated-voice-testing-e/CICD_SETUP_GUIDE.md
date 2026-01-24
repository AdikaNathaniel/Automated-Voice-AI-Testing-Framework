# CI/CD Integration - Complete Setup Guide

**Time Required**: 10-15 minutes
**User Required**: Organization Admin (org_admin role)

---

## 🎯 **What You'll Achieve**

Automatically run your voice AI test suites when you push code to GitHub. For example:
- Push to `main` → Run full production test suite
- Push to `staging` → Run smoke tests
- Open pull request → Skip (or run if you want)

---

## Part 1: Setup in Your App (5 minutes)

### Step 1: Navigate to CI/CD Dashboard

1. **Log in** as an **org_admin** user
   - Only org_admin users can access CI/CD integration
   - Other roles (qa_lead, validator, viewer) will see "Access Denied"

2. **Go to** `/cicd` in your browser
   - Or click **"CI/CD Integration"** in the sidebar (if visible)

3. You'll see two tabs:
   - **Test Runs**: History of automated runs (empty for now)
   - **Configuration**: Where we'll set everything up

---

### Step 2: Click "Configuration" Tab

You'll see three provider sections: **GitHub**, **GitLab**, **Jenkins**

We'll configure **GitHub** (the process is similar for others)

---

### Step 3: Configure GitHub Provider

Click the **GitHub** card to expand settings.

#### 3.1 Copy Your Webhook URL

At the top, you'll see your unique webhook URL:
```
https://your-domain.com/api/v1/webhooks/ci-cd
```

**IMPORTANT**: Copy this URL - you'll need it in GitHub (Step 4)

---

#### 3.2 Choose Test Suite

**Test Suite Selection**:
- Click the dropdown: "Select test suite"
- Choose which suite to run (e.g., "Production Test Suite", "Smoke Tests")
- This suite will run whenever the webhook fires

**Scenario Selection** (optional):
- Leave empty to run ALL scenarios in the suite
- Or select specific scenarios if you only want to test certain features

---

#### 3.3 Generate Webhook Secret

**Why?** This proves webhooks are actually from GitHub, not an attacker.

1. Generate a secure random string:
   ```bash
   # On Mac/Linux:
   openssl rand -hex 32

   # Example output:
   a7f8e3c9d2b1f4e6a8c7d9e1f3b5a2c4d6e8f1a3b5c7d9e2f4a6b8c1d3e5f7a9
   ```

2. **Copy this secret** (you'll need it twice):
   - Once for the app (next step)
   - Once for GitHub (Step 4)

3. Paste it in **"Webhook Secret"** field in the app

---

#### 3.4 Configure Branch Filters

Control which branches trigger tests:

**Enable Branch Filtering**: ✅ Check this box

**Include Branches** (optional):
```
main
staging
release/*
```
- Only these branches will trigger tests
- Use `*` for wildcards (e.g., `release/*` matches `release/v1.0`, `release/v2.0`)
- Leave empty to allow ALL branches (except excluded ones)

**Exclude Branches** (optional):
```
dev/*
feature/experimental
```
- These branches will NEVER trigger tests
- Takes precedence over include list

**Examples**:
```
✅ Scenario 1: Only production
   Include: main, production
   Exclude: (empty)
   → Tests run ONLY on main and production

✅ Scenario 2: All branches except dev
   Include: (empty)
   Exclude: dev/*, experimental
   → Tests run on everything except dev branches

✅ Scenario 3: Release branches only
   Include: release/*
   Exclude: release/experimental
   → Tests run on release/v1.0, release/v2.0, but NOT release/experimental
```

---

#### 3.5 Configure Event Filters

Control which GitHub events trigger tests:

- ☑ **Push events**: Commits pushed to repository
  - ✅ Recommended: Keep enabled
  - Use case: Test on every commit to main

- ☐ **Pull requests**: PRs opened or updated
  - ❌ Default: Disabled (can be noisy)
  - Use case: Validate PRs before merge

- ☑ **Workflow runs**: GitHub Actions completed
  - ✅ Recommended: Keep enabled
  - Use case: Run tests after CI build succeeds

- ☑ **Deployments**: Deployment events
  - ✅ Recommended: Keep enabled
  - Use case: Validate after deployment

**Common Configurations**:
```
Production Only:
  ✅ Push
  ❌ Pull requests
  ❌ Workflow runs
  ✅ Deployments

PR Validation:
  ❌ Push
  ✅ Pull requests
  ❌ Workflow runs
  ❌ Deployments

Everything:
  ✅ Push
  ✅ Pull requests
  ✅ Workflow runs
  ✅ Deployments
```

---

#### 3.6 Enable Regression Testing (Optional)

If you want to also run regression tests:

1. ☑ **Run regression tests**
2. Select which regression suite(s) to run
3. These will run IN ADDITION to your main test suite

---

#### 3.7 Save Configuration

Click **"Save Configuration"** button

You should see: ✅ "Configuration saved successfully"

---

## Part 2: Setup in GitHub (5 minutes)

### Step 4: Add Webhook to GitHub Repository

1. **Go to your GitHub repository**
   - Example: `github.com/your-org/your-repo`

2. **Click Settings** (top navigation)
   - You need admin access to the repository

3. **Click "Webhooks"** (left sidebar)

4. **Click "Add webhook"** button

---

### Step 5: Configure GitHub Webhook

You'll see a form with several fields:

#### Payload URL
```
https://your-domain.com/api/v1/webhooks/ci-cd
```
- Paste the URL you copied from Step 3.1
- Make sure it's exactly correct (no trailing spaces)

#### Content type
```
application/json
```
- Select from dropdown

#### Secret
```
a7f8e3c9d2b1f4e6a8c7d9e1f3b5a2c4d6e8f1a3b5c7d9e2f4a6b8c1d3e5f7a9
```
- Paste the webhook secret you generated in Step 3.3
- This MUST match exactly what you entered in the app

#### SSL verification
```
☑ Enable SSL verification
```
- Keep this checked for security

#### Which events?
```
☑ Let me select individual events
```
- Then check the events you enabled in Step 3.5

**Example**: If you enabled Push and Deployments in the app:
- ☑ Pushes
- ☐ Pull requests
- ☐ Releases
- ☑ Deployments
- (uncheck all others)

**Important**: The events you select here should match what you enabled in the app's Event Filters.

#### Active
```
☑ Active
```
- Make sure this is checked

---

### Step 6: Save Webhook

1. Click **"Add webhook"** button at the bottom

2. GitHub will send a test "ping" event
   - You should see a green checkmark ✅ if it succeeded
   - Or a red X ❌ if it failed

3. **If it failed**:
   - Click on the webhook
   - Check "Recent Deliveries" tab
   - Look for error messages
   - Common issues:
     - Wrong URL (typo in webhook URL)
     - Wrong secret (doesn't match app config)
     - Network error (can't reach your server)

---

## Part 3: Test It Out (5 minutes)

### Step 7: Trigger a Test Webhook

**Option 1: Manual Test from GitHub**
1. Go to your webhook settings
2. Click on your webhook
3. Scroll down to "Recent Deliveries"
4. Click "Redeliver" on the ping event
5. Check your app's logs (Step 9)

**Option 2: Make a Real Commit**
```bash
# Make a small change
echo "# Test" >> README.md

# Commit and push
git add README.md
git commit -m "Test CI/CD webhook"
git push origin main
```

---

### Step 8: Watch for Test Run

1. **Go back to your app** → `/cicd`
2. **Click "Test Runs" tab**
3. You should see a new run appear:
   - Pipeline: Your repo name
   - Branch: `main` (or whatever branch you pushed to)
   - Status: `Running` → `Success` or `Failed`
   - Triggered by: Your GitHub username

---

### Step 9: Check Logs (If Issues)

If the webhook didn't trigger:

```bash
# Watch backend logs for filter decisions
docker-compose logs -f backend | grep "CICD-FILTER"
```

**What you'll see**:

If **allowed**:
```
[CICD-FILTER] Processing webhook: Passed all filters (branch='main', event='push')
```

If **filtered out**:
```
[CICD-FILTER] Skipping webhook: Branch 'dev' filtered out by branch filter
```
or
```
[CICD-FILTER] Skipping webhook: Event type 'pull_request' filtered out by event filter
```

---

## 🔍 **Troubleshooting**

### Webhook Not Firing

**Check GitHub Delivery**:
1. GitHub → Settings → Webhooks → Click your webhook
2. "Recent Deliveries" tab
3. Look for red X marks
4. Click "Response" to see error

**Common Issues**:
- ❌ **401 Unauthorized**: Wrong webhook secret (regenerate and update both sides)
- ❌ **404 Not Found**: Wrong webhook URL (double-check the URL)
- ❌ **500 Server Error**: Backend crashed (check backend logs)
- ❌ **Timeout**: Server unreachable (firewall? domain correct?)

---

### Tests Not Running

**Scenario 1**: Webhook fires but no tests run

**Check**:
1. Backend logs: `docker-compose logs backend | grep CICD-FILTER`
2. Look for "Skipping webhook" messages
3. Common causes:
   - Branch not in include list
   - Branch in exclude list
   - Event type disabled in event filter

**Fix**: Update your filters in app's Configuration tab

---

**Scenario 2**: Webhook fires, tests run, but wrong suite

**Check**:
1. Configuration tab → GitHub → Test Suite Selection
2. Make sure correct suite is selected

**Fix**: Change test suite, save, and trigger new webhook

---

### Wrong Branch/Event Triggering

**Problem**: Tests running on branches you don't want

**Check**:
1. Configuration tab → GitHub → Branch Filters
2. Make sure "Enable Branch Filtering" is checked
3. Verify include/exclude patterns

**Example Debug**:
```
Want: Only run on main
Current: Tests running on feature/dev

Fix:
  ✅ Enable Branch Filtering
  Include: main
  Exclude: (empty)
```

---

## 📊 **Understanding Test Results**

After a test run completes:

**In the App** (`/cicd` → Test Runs tab):
- Click on any run to see details
- See which scenarios passed/failed
- View execution logs
- See commit info and who triggered it

**Future Enhancement** (not yet implemented):
- Results will also post back to GitHub
- You'll see commit status checks: ✅ or ❌
- Can block merges if voice tests fail

---

## 💡 **Best Practices**

### Start Simple
```
1. First setup: Just enable for 'main' branch, push events only
2. Test it works
3. Then expand to more branches/events
```

### Production Strategy
```
Branch Filters:
  Include: main, production
  Exclude: (empty)

Event Filters:
  ✅ Push
  ❌ Pull requests
  ❌ Workflow runs
  ✅ Deployments

Test Suite: "Production Full Suite"
Regression: Enabled with "Critical Path Tests"
```

### PR Validation Strategy
```
Branch Filters:
  Include: * (all)
  Exclude: main, production (no need, already tested on merge)

Event Filters:
  ❌ Push
  ✅ Pull requests
  ❌ Workflow runs
  ❌ Deployments

Test Suite: "Quick Smoke Tests" (fast feedback)
Regression: Disabled (save time)
```

---

## ✅ **Success Checklist**

- [ ] Logged in as org_admin
- [ ] Navigated to `/cicd` → Configuration tab
- [ ] Selected test suite
- [ ] Generated webhook secret
- [ ] Configured branch filters (if needed)
- [ ] Configured event filters
- [ ] Saved configuration
- [ ] Copied webhook URL
- [ ] Added webhook to GitHub repository
- [ ] Pasted webhook URL in GitHub
- [ ] Pasted webhook secret in GitHub
- [ ] Selected matching events in GitHub
- [ ] Saved GitHub webhook
- [ ] Saw green checkmark ✅ on webhook
- [ ] Made test commit
- [ ] Saw test run appear in app
- [ ] Tests executed successfully

---

## 🎉 **You're Done!**

Your voice AI tests now run automatically on every push to your configured branches!

Next time you push code:
1. GitHub sends webhook
2. App checks filters (branch + event)
3. If allowed → Runs your test suite
4. Results appear in Test Runs tab
5. You get instant feedback on voice AI quality
