# Git Branching Strategy

## Overview

This document outlines the Git branching strategy and workflow for the Automated Voice AI Testing Framework project. We follow a modified Git Flow model optimized for continuous integration and deployment, ensuring code quality through branch protection rules and mandatory code reviews.

The branching strategy is designed to:
- Support parallel development of multiple features
- Maintain a stable main branch for production releases
- Enable quick hotfixes for production issues
- Integrate seamlessly with CI/CD pipelines
- Enforce code quality through automated testing and reviews

---

## Branching Model

Our branching model consists of the following primary branches:

### Permanent Branches

#### `main` Branch
- **Purpose**: Production-ready code
- **Stability**: Always deployable
- **Protection**: Highest level of protection
- **Deployment**: Automatically deploys to production
- **Merge Source**: Only from `release/*` or `hotfix/*` branches

#### `develop` Branch
- **Purpose**: Integration branch for features
- **Stability**: Should always be in a working state
- **Protection**: High level of protection
- **Deployment**: Automatically deploys to staging environment
- **Merge Source**: From `feature/*` branches

### Temporary Branches

#### `feature/*` Branches
- **Purpose**: Development of new features or enhancements
- **Naming Convention**: `feature/TASK-XXX-brief-description`
- **Base Branch**: `develop`
- **Merge Target**: `develop`
- **Lifetime**: Created for feature development, deleted after merge
- **Examples**:
  - `feature/TASK-001-user-authentication`
  - `feature/TASK-023-dashboard-analytics`
  - `feature/add-export-functionality`

#### `hotfix/*` Branches
- **Purpose**: Critical bug fixes for production
- **Naming Convention**: `hotfix/brief-description` or `hotfix/issue-number`
- **Base Branch**: `main`
- **Merge Target**: Both `main` and `develop`
- **Lifetime**: Created for urgent fixes, deleted after merge
- **Examples**:
  - `hotfix/api-timeout-error`
  - `hotfix/security-vulnerability`

#### `release/*` Branches
- **Purpose**: Preparation for production release
- **Naming Convention**: `release/v1.2.3` (semantic versioning)
- **Base Branch**: `develop`
- **Merge Target**: Both `main` and `develop`
- **Lifetime**: Created for release preparation, deleted after merge
- **Activities**: Version bumping, final testing, documentation updates

---

## Branch Types

### 1. Main Branch (`main`)

The `main` branch represents the official release history. All commits on `main` should be tagged with a version number following semantic versioning (e.g., v1.0.0, v1.2.3).

**Branch Protection Rules:**
- Require pull request reviews before merging (minimum 2 approvals)
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Include administrators in restrictions
- Require linear history (no merge commits, use squash or rebase)
- Require signed commits
- Do not allow force pushes
- Do not allow deletions

**CI/CD Integration:**
- All tests must pass (unit, integration, end-to-end)
- Code coverage must be >= 80%
- Security scans must pass (no critical/high vulnerabilities)
- Performance tests must pass
- Automated deployment to production environment

### 2. Develop Branch (`develop`)

The `develop` branch serves as an integration branch for features. It contains the latest delivered development changes for the next release.

**Branch Protection Rules:**
- Require pull request reviews before merging (minimum 1 approval)
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Do not allow force pushes
- Do not allow deletions

**CI/CD Integration:**
- All tests must pass
- Code coverage must be >= 75%
- Linting checks must pass
- Automated deployment to staging environment

### 3. Feature Branches (`feature/*`)

Feature branches are used to develop new features or enhancements. Each feature should be developed in its own branch.

**Workflow:**
1. Create branch from `develop`
2. Develop feature with TDD approach (tests first, then implementation)
3. Commit regularly with clear, conventional commit messages
4. Push to remote repository
5. Create pull request when feature is complete
6. Address code review feedback
7. Merge into `develop` after approval

**Requirements:**
- All tests must pass locally before creating PR
- Follow TDD approach (write tests first)
- Update documentation as needed
- Add/update integration tests if applicable

### 4. Hotfix Branches (`hotfix/*`)

Hotfix branches are used for critical bug fixes that need to be deployed to production immediately.

**Workflow:**
1. Create branch from `main`
2. Fix the bug with tests to prevent regression
3. Update version number (patch increment)
4. Create pull request
5. After approval, merge into both `main` and `develop`
6. Tag the release on `main`
7. Deploy to production

**Requirements:**
- Must include regression tests
- Must be reviewed by at least 2 team members
- Must pass all CI/CD checks
- Should be deployed as soon as possible

### 5. Release Branches (`release/*`)

Release branches support preparation of a new production release, allowing for last-minute bug fixes and release preparation.

**Workflow:**
1. Create branch from `develop` when ready for release
2. Update version numbers
3. Fix release-specific bugs
4. Update CHANGELOG.md
5. Final testing and validation
6. Merge into both `main` and `develop`
7. Tag the release on `main`

---

## Branch Protection Rules

### Main Branch Protection

```yaml
Branch: main
Protection Rules:
  - Required pull request reviews: 2
  - Dismiss stale pull request approvals: true
  - Require review from code owners: true
  - Required status checks:
      - continuous-integration/pytest
      - continuous-integration/frontend-tests
      - security/dependency-scan
      - security/code-scan
      - code-quality/coverage
      - code-quality/linting
  - Require branches to be up to date: true
  - Include administrators: true
  - Restrict pushes: true
  - Allow force pushes: false
  - Allow deletions: false
  - Require signed commits: true
  - Require linear history: true
```

### Develop Branch Protection

```yaml
Branch: develop
Protection Rules:
  - Required pull request reviews: 1
  - Dismiss stale pull request approvals: true
  - Required status checks:
      - continuous-integration/pytest
      - continuous-integration/frontend-tests
      - code-quality/linting
  - Require branches to be up to date: true
  - Allow force pushes: false
  - Allow deletions: false
```

---

## Git Workflow

### Standard Feature Development Workflow

```bash
# 1. Ensure develop is up to date
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/TASK-XXX-feature-name

# 3. Develop with TDD approach
# - Write tests first (Red phase)
pytest tests/test_new_feature.py  # Should fail

# - Implement feature (Green phase)
# Write code...
pytest tests/test_new_feature.py  # Should pass

# - Refactor if needed (Refactor phase)
# Improve code quality while keeping tests passing

# 4. Commit changes with conventional commits
git add .
git commit -m "feat(module): add new feature description

- Detailed change 1
- Detailed change 2

Closes #123"

# 5. Push to remote
git push origin feature/TASK-XXX-feature-name

# 6. Create pull request on GitHub/GitLab
# 7. Wait for code review and approval
# 8. Address review feedback if needed
# 9. Merge into develop after approval
```

### Hotfix Workflow

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug-fix

# 2. Fix the bug and add regression tests
# Write tests to prevent regression
pytest tests/test_bug_fix.py

# 3. Commit the fix
git add .
git commit -m "fix: resolve critical production bug

Fixes #456"

# 4. Push and create pull request
git push origin hotfix/critical-bug-fix

# 5. After approval, merge into both main and develop
git checkout main
git merge --no-ff hotfix/critical-bug-fix
git tag -a v1.2.1 -m "Hotfix release 1.2.1"
git push origin main --tags

git checkout develop
git merge --no-ff hotfix/critical-bug-fix
git push origin develop

# 6. Delete hotfix branch
git branch -d hotfix/critical-bug-fix
git push origin --delete hotfix/critical-bug-fix
```

### Release Workflow

```bash
# 1. Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.3.0

# 2. Update version numbers
# - Update package.json
# - Update version in __init__.py
# - Update CHANGELOG.md

# 3. Commit release preparation
git add .
git commit -m "chore(release): prepare version 1.3.0"

# 4. Final testing and bug fixes on release branch
# Make only release-specific fixes (no new features)

# 5. Push and create pull request
git push origin release/v1.3.0

# 6. After approval, merge into main and develop
git checkout main
git merge --no-ff release/v1.3.0
git tag -a v1.3.0 -m "Release version 1.3.0"
git push origin main --tags

git checkout develop
git merge --no-ff release/v1.3.0
git push origin develop

# 7. Delete release branch
git branch -d release/v1.3.0
git push origin --delete release/v1.3.0
```

---

## Naming Conventions

### Branch Names

Follow these naming conventions for consistency:

**Feature Branches:**
- Format: `feature/TASK-XXX-brief-description`
- Use lowercase with hyphens
- Start with TASK ID from TODOS.md if applicable
- Keep description brief but clear
- Examples:
  - `feature/TASK-006-initialize-dependencies`
  - `feature/add-user-authentication`
  - `feature/dashboard-performance-improvements`

**Hotfix Branches:**
- Format: `hotfix/brief-description` or `hotfix/issue-XXX`
- Use lowercase with hyphens
- Be specific about the fix
- Examples:
  - `hotfix/api-timeout-error`
  - `hotfix/security-vulnerability-CVE-2024-1234`
  - `hotfix/database-connection-pool`

**Release Branches:**
- Format: `release/vX.Y.Z`
- Use semantic versioning
- Examples:
  - `release/v1.0.0`
  - `release/v1.2.3`
  - `release/v2.0.0-beta.1`

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, semicolons, etc.)
- `refactor`: Code refactoring without changing functionality
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates
- `perf`: Performance improvements
- `ci`: CI/CD configuration changes

**Examples:**

```bash
# Feature
git commit -m "feat(api): add user authentication endpoint

- Implement JWT token generation
- Add login/logout endpoints
- Include refresh token mechanism

Closes #123"

# Bug fix
git commit -m "fix(validation): resolve edge case in test execution

The validation service was failing on empty responses.
This fix adds proper null checking.

Fixes #456"

# Documentation
git commit -m "docs(readme): update installation instructions"

# Testing
git commit -m "test(api): add integration tests for user endpoints"

# Refactoring
git commit -m "refactor(services): extract common validation logic"
```

---

## Code Review Process

All code changes must go through code review before merging to protected branches.

### Pull Request Requirements

1. **Title**: Clear, descriptive title following commit message format
2. **Description**:
   - Summary of changes
   - Link to related issues/tasks
   - Testing performed
   - Screenshots (if UI changes)
3. **Tests**: All tests must pass
4. **Code Coverage**: Must maintain or improve coverage
5. **Documentation**: Update relevant documentation
6. **Commits**: Use conventional commit messages

### Review Guidelines

**For Reviewers:**
- Review within 24 hours of PR creation
- Check code quality, readability, and maintainability
- Verify tests cover edge cases
- Ensure documentation is updated
- Test the changes locally if significant
- Provide constructive feedback
- Approve only when all concerns are addressed

**For Authors:**
- Respond to feedback within 24 hours
- Address all review comments
- Re-request review after making changes
- Keep PRs focused and reasonably sized
- Provide context in PR description

### Approval Requirements

- **Main branch**: 2 approvals required (including 1 from code owner)
- **Develop branch**: 1 approval required
- **Feature branches**: No restrictions (but PRs to develop need approval)

---

## Testing Requirements

All branches must meet testing requirements before merging.

### Test Categories

1. **Unit Tests**: Test individual functions/methods in isolation
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete user workflows
4. **Performance Tests**: Validate performance requirements
5. **Security Tests**: Check for vulnerabilities

### Coverage Requirements

- **Main branch**: >= 80% code coverage
- **Develop branch**: >= 75% code coverage
- **Feature branches**: Must not decrease overall coverage

### CI/CD Checks

All branches automatically run:
- Backend tests (`pytest`)
- Frontend tests (`npm test`)
- Linting checks (`ruff`, `eslint`)
- Type checking (`mypy`, `tsc`)
- Security scans (dependency vulnerabilities, code security)
- Code coverage analysis

---

## Merge Strategies

### Squash and Merge (Default for Feature Branches)

Used when merging feature branches into `develop`:
- Combines all commits into a single commit
- Creates a clean, linear history
- Preserves pull request reference

```bash
# Automatically done by GitHub/GitLab when selecting "Squash and Merge"
git checkout develop
git merge --squash feature/TASK-XXX-feature-name
git commit -m "feat: feature description (#PR-number)"
```

### Merge with No Fast-Forward (For Releases and Hotfixes)

Used when merging release/hotfix branches into `main`:
- Preserves branch history
- Creates a merge commit
- Makes it clear what came from where

```bash
git checkout main
git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "Release 1.2.0"
```

### Rebase (For Keeping Feature Branches Updated)

Used to update feature branches with latest develop changes:

```bash
git checkout feature/TASK-XXX-feature-name
git rebase develop

# If conflicts occur:
# 1. Resolve conflicts in files
# 2. git add <resolved-files>
# 3. git rebase --continue

# Force push after rebase (feature branch only!)
git push --force-with-lease origin feature/TASK-XXX-feature-name
```

---

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/) (SemVer):

```
MAJOR.MINOR.PATCH (e.g., 1.2.3)
```

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards-compatible)
- **PATCH**: Bug fixes (backwards-compatible)

**Pre-release versions:**
- `1.0.0-alpha.1` - Alpha release
- `1.0.0-beta.2` - Beta release
- `1.0.0-rc.1` - Release candidate

### Release Checklist

- [ ] All features for release are merged to `develop`
- [ ] All tests pass on `develop`
- [ ] Create release branch from `develop`
- [ ] Update version numbers in all files
- [ ] Update CHANGELOG.md with release notes
- [ ] Run full regression test suite
- [ ] Perform security scan
- [ ] Update documentation
- [ ] Create release PR to `main`
- [ ] Get required approvals (2+ reviewers)
- [ ] Merge to `main` and tag release
- [ ] Merge back to `develop`
- [ ] Deploy to production
- [ ] Monitor production for issues
- [ ] Announce release to team

---

## Continuous Integration and Deployment

### CI/CD Pipeline

Our CI/CD pipeline automatically runs on all branches:

**On Push to Any Branch:**
1. Run linting checks
2. Run unit tests
3. Generate coverage report
4. Run security scans

**On Pull Request:**
1. All above checks
2. Run integration tests
3. Check code coverage (must not decrease)
4. Check for merge conflicts
5. Verify commit message format

**On Merge to Develop:**
1. All PR checks
2. Run end-to-end tests
3. Build Docker images
4. Deploy to staging environment
5. Run smoke tests on staging

**On Merge to Main:**
1. All develop checks
2. Run full test suite
3. Build production Docker images
4. Create release artifacts
5. Deploy to production
6. Run smoke tests on production
7. Send deployment notification

### Automated Deployments

- **Staging**: Automatic deployment on merge to `develop`
- **Production**: Automatic deployment on merge to `main` (with tag)
- **Rollback**: Available via tagged versions

---

## Best Practices

### Do's ✅

- **Commit often** with clear, descriptive messages
- **Write tests first** (TDD approach)
- **Keep PRs small** and focused (< 500 lines when possible)
- **Update documentation** with code changes
- **Rebase feature branches** to keep up with develop
- **Delete branches** after merging
- **Tag releases** with semantic versions
- **Review code thoroughly** before approval
- **Run tests locally** before pushing
- **Use meaningful branch names**

### Don'ts ❌

- **Don't commit to main/develop directly** - always use PRs
- **Don't force push** to protected branches
- **Don't merge without approval** on protected branches
- **Don't commit secrets** or credentials
- **Don't create long-lived feature branches** (merge frequently)
- **Don't skip tests** or CI checks
- **Don't merge broken code** to develop/main
- **Don't use generic commit messages** ("fix bug", "update code")
- **Don't commit commented-out code** - remove it
- **Don't ignore code review feedback**

---

## Troubleshooting

### Common Issues and Solutions

**Issue: Branch is behind develop**
```bash
git checkout feature/my-feature
git rebase develop
git push --force-with-lease
```

**Issue: Merge conflicts**
```bash
# During merge:
git status  # See conflicted files
# Edit files to resolve conflicts
git add <resolved-files>
git commit
```

**Issue: Need to undo last commit (local only)**
```bash
git reset --soft HEAD~1  # Keep changes
# or
git reset --hard HEAD~1  # Discard changes
```

**Issue: Accidentally committed to wrong branch**
```bash
# Save the commit
git cherry-pick <commit-hash>

# Switch to correct branch
git checkout correct-branch
git cherry-pick <commit-hash>

# Remove from wrong branch
git checkout wrong-branch
git reset --hard HEAD~1
```

---

## Summary

This branching strategy ensures:
- **Code Quality**: Through mandatory reviews and automated testing
- **Stability**: Protected branches with strict merge requirements
- **Collaboration**: Clear workflow for parallel development
- **Traceability**: Conventional commits and linear history
- **Reliability**: Comprehensive CI/CD integration with automated deployment
- **Maintainability**: Clean branch structure and documentation

For questions or suggestions about this branching strategy, please contact the development team or create an issue in the project repository.

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-24
**Maintained By**: Development Team
