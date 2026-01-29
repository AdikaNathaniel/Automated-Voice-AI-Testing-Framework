# Role-Based Access Control (RBAC) - Privilege Specification

## Overview

The Automated Voice AI Testing Framework implements a 5-tier role-based access control system. Each role has specific privileges that determine what actions a user can perform within the platform. All roles are scoped by tenant (organization) unless otherwise noted.

---

## Roles Summary

| Role | Description |
|------|-------------|
| **super_admin** | Platform-level administrator with unrestricted access across all organizations |
| **org_admin** | Organization administrator with full control within their own organization |
| **qa_lead** | Quality assurance lead who can create and manage test resources |
| **validator** | Can claim and submit validation tasks for test result review |
| **viewer** | Read-only access to all resources within their organization |

---

## Detailed Privileges by Role

### 1. Super Admin (`super_admin`)

**Scope:** Platform-wide (all organizations)

| Category | Privilege | Allowed |
|----------|-----------|:-------:|
| **Authentication** | Login / Logout | Yes |
| **Authentication** | Refresh tokens | Yes |
| **User Management** | Register new users | Yes |
| **User Management** | View all users | Yes |
| **User Management** | Update any user | Yes |
| **User Management** | Delete any user | Yes |
| **User Management** | Assign any role | Yes |
| **Organization** | Create organizations | Yes |
| **Organization** | View all organizations | Yes |
| **Organization** | Manage any organization | Yes |
| **Scenarios** | Create scenarios | Yes |
| **Scenarios** | View all scenarios | Yes |
| **Scenarios** | Edit any scenario | Yes |
| **Scenarios** | Delete any scenario | Yes |
| **Scenarios** | Approve/reject scenarios | Yes |
| **Scenarios** | Self-approve own scenarios | Yes |
| **Test Execution** | Execute tests | Yes |
| **Test Execution** | View all executions | Yes |
| **Test Execution** | Cancel executions | Yes |
| **Validation** | Claim validation tasks | Yes |
| **Validation** | Submit validation results | Yes |
| **Validation** | Override validations | Yes |
| **Audio** | Upload audio files | Yes |
| **Audio** | Apply noise profiles | Yes |
| **Audio** | Delete audio files | Yes |
| **Configuration** | Manage LLM providers | Yes |
| **Configuration** | Manage integrations | Yes |
| **Configuration** | View system settings | Yes |
| **Reports** | View all reports | Yes |
| **Reports** | Export data | Yes |

---

### 2. Organization Admin (`org_admin`)

**Scope:** Own organization only

| Category | Privilege | Allowed |
|----------|-----------|:-------:|
| **Authentication** | Login / Logout | Yes |
| **Authentication** | Refresh tokens | Yes |
| **User Management** | Register users in own org | Yes |
| **User Management** | View users in own org | Yes |
| **User Management** | Update users in own org | Yes |
| **User Management** | Delete users in own org | Yes |
| **User Management** | Assign roles (except super_admin) | Yes |
| **Organization** | Create organizations | No |
| **Organization** | View own organization | Yes |
| **Organization** | Manage own organization | Yes |
| **Scenarios** | Create scenarios | Yes |
| **Scenarios** | View org scenarios | Yes |
| **Scenarios** | Edit org scenarios | Yes |
| **Scenarios** | Delete org scenarios | Yes |
| **Scenarios** | Approve/reject scenarios | Yes |
| **Scenarios** | Self-approve own scenarios | Yes |
| **Test Execution** | Execute tests | Yes |
| **Test Execution** | View org executions | Yes |
| **Test Execution** | Cancel executions | Yes |
| **Validation** | Claim validation tasks | Yes |
| **Validation** | Submit validation results | Yes |
| **Validation** | Override validations | Yes |
| **Audio** | Upload audio files | Yes |
| **Audio** | Apply noise profiles | Yes |
| **Audio** | Delete audio files | Yes |
| **Configuration** | Manage LLM providers | Yes |
| **Configuration** | Manage integrations | Yes |
| **Configuration** | View system settings | Yes |
| **Reports** | View org reports | Yes |
| **Reports** | Export data | Yes |

---

### 3. QA Lead (`qa_lead`)

**Scope:** Own organization only

| Category | Privilege | Allowed |
|----------|-----------|:-------:|
| **Authentication** | Login / Logout | Yes |
| **Authentication** | Refresh tokens | Yes |
| **User Management** | Register users | No |
| **User Management** | View users | No |
| **User Management** | Manage users | No |
| **Organization** | Manage organization | No |
| **Scenarios** | Create scenarios | Yes |
| **Scenarios** | View org scenarios | Yes |
| **Scenarios** | Edit own scenarios | Yes |
| **Scenarios** | Delete own scenarios | Yes |
| **Scenarios** | Approve/reject scenarios | Yes |
| **Scenarios** | Self-approve own scenarios | No |
| **Test Execution** | Execute tests | Yes |
| **Test Execution** | View org executions | Yes |
| **Test Execution** | Cancel own executions | Yes |
| **Validation** | Claim validation tasks | Yes |
| **Validation** | Submit validation results | Yes |
| **Validation** | Override validations | No |
| **Audio** | Upload audio files | Yes |
| **Audio** | Apply noise profiles | Yes |
| **Audio** | Delete own audio files | Yes |
| **Configuration** | Manage LLM providers | No |
| **Configuration** | Manage integrations | No |
| **Configuration** | View system settings | Yes |
| **Reports** | View org reports | Yes |
| **Reports** | Export data | Yes |

---

### 4. Validator (`validator`)

**Scope:** Own organization only

| Category | Privilege | Allowed |
|----------|-----------|:-------:|
| **Authentication** | Login / Logout | Yes |
| **Authentication** | Refresh tokens | Yes |
| **User Management** | Any user management | No |
| **Organization** | Manage organization | No |
| **Scenarios** | Create scenarios | No |
| **Scenarios** | View org scenarios | Yes |
| **Scenarios** | Edit scenarios | No |
| **Scenarios** | Delete scenarios | No |
| **Scenarios** | Approve/reject scenarios | No |
| **Test Execution** | Execute tests | No |
| **Test Execution** | View org executions | Yes |
| **Test Execution** | Cancel executions | No |
| **Validation** | Claim validation tasks | Yes |
| **Validation** | Submit validation results | Yes |
| **Validation** | Override validations | No |
| **Audio** | Upload audio files | No |
| **Audio** | Apply noise profiles | No |
| **Audio** | Delete audio files | No |
| **Configuration** | Manage settings | No |
| **Reports** | View org reports | Yes |
| **Reports** | Export data | No |

---

### 5. Viewer (`viewer`)

**Scope:** Own organization only

| Category | Privilege | Allowed |
|----------|-----------|:-------:|
| **Authentication** | Login / Logout | Yes |
| **Authentication** | Refresh tokens | Yes |
| **User Management** | Any user management | No |
| **Organization** | Manage organization | No |
| **Scenarios** | Create scenarios | No |
| **Scenarios** | View org scenarios | Yes |
| **Scenarios** | Edit scenarios | No |
| **Scenarios** | Delete scenarios | No |
| **Scenarios** | Approve/reject scenarios | No |
| **Test Execution** | Execute tests | No |
| **Test Execution** | View org executions | Yes |
| **Test Execution** | Cancel executions | No |
| **Validation** | Claim validation tasks | No |
| **Validation** | Submit validation results | No |
| **Validation** | Override validations | No |
| **Audio** | Upload audio files | No |
| **Audio** | Apply noise profiles | No |
| **Audio** | Delete audio files | No |
| **Configuration** | Manage settings | No |
| **Reports** | View org reports | Yes |
| **Reports** | Export data | No |

---

## Quick Comparison Matrix

| Privilege | super_admin | org_admin | qa_lead | validator | viewer |
|-----------|:-----------:|:---------:|:-------:|:---------:|:------:|
| Cross-org access | Yes | No | No | No | No |
| Register users | Yes | Yes | No | No | No |
| Create scenarios | Yes | Yes | Yes | No | No |
| Edit any scenario | Yes | Yes | No | No | No |
| Delete scenarios | Yes | Yes | Own only | No | No |
| Approve scenarios | Yes | Yes | Yes | No | No |
| Execute tests | Yes | Yes | Yes | No | No |
| Claim validations | Yes | Yes | Yes | Yes | No |
| Submit validations | Yes | Yes | Yes | Yes | No |
| Upload audio | Yes | Yes | Yes | No | No |
| Apply noise | Yes | Yes | Yes | No | No |
| Manage config | Yes | Yes | No | No | No |
| View reports | Yes | Yes | Yes | Yes | Yes |
| Export data | Yes | Yes | Yes | No | No |

---

## Security Notes

1. **Tenant Isolation** - All data is scoped by organization (tenant_id). Users can only access data within their own organization, except super_admin.
2. **Ownership Checks** - For write operations, qa_lead users can only modify resources they created. Admins can modify any resource in their organization.
3. **Scenario Approval** - QA leads cannot self-approve their own scenarios to maintain quality control. Org admins can self-approve.
4. **Brute-Force Protection** - All accounts are protected with exponential backoff and lockout after 5 failed login attempts (15-minute lockout).
5. **JWT Tokens** - Access tokens expire after 30 minutes. Refresh tokens expire after 14 days with token rotation for security.

---

## Default Accounts (Development)

| Role | Email | Password |
|------|-------|----------|
| super_admin | admin@voiceai.dev | SuperAdmin123! |
| org_admin | demo@voiceai.dev | DemoAdmin123! |
