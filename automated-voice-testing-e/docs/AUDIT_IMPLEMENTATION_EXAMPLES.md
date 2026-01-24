# Audit Trail Implementation Examples

This document provides practical examples of implementing audit logging using the `@audit_log` decorator.

## Table of Contents

1. [Basic Decorator Usage](#basic-decorator-usage)
2. [Authentication Logging](#authentication-logging)
3. [User Management Logging](#user-management-logging)
4. [Configuration Changes Logging](#configuration-changes-logging)
5. [Sensitive Data Masking](#sensitive-data-masking)
6. [Advanced Patterns](#advanced-patterns)

---

## Basic Decorator Usage

### Simple Create Operation

```python
from api.decorators.audit import audit_create

@router.post("/users")
@audit_create(
    resource_type="user",
    get_resource_id=lambda result, **kwargs: str(result.id),
    get_new_values=lambda result, **kwargs: {
        "email": result.email,
        "username": result.username,
        "role": result.role,
    },
    summary_template="User {email} created with role {role}"
)
async def create_user(
    data: UserCreate,
    request: Request,  # Required for IP/user agent
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
):
    user = User(**data.dict())
    db.add(user)
    await db.commit()
    return user
```

### Simple Update Operation

```python
from api.decorators.audit import audit_update

async def _fetch_old_user(kwargs, db):
    """Helper to fetch user before update."""
    user_id = kwargs.get("user_id")
    user = await get_user_by_id(db, user_id)
    return {
        "old_user_values": {
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
        }
    }

@router.put("/users/{user_id}")
@audit_update(
    resource_type="user",
    get_resource_id=lambda kwargs, **kw: str(kwargs["user_id"]),
    get_old_values=lambda context, **kw: context.get("old_user_values"),
    get_new_values=lambda result, **kw: {
        "email": result.email,
        "role": result.role,
        "is_active": result.is_active,
    },
    before_handler=_fetch_old_user,
    summary_template="User {email} updated"
)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
):
    user = await get_user_by_id(db, user_id)
    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    return user
```

---

## Authentication Logging

### Successful Login

```python
from api.decorators.audit import audit_log

@router.post("/login", response_model=LoginResponse)
@audit_log(
    action_type="login",
    resource_type="user",
    get_resource_id=lambda result, **kw: str(result.user.id),
    get_tenant_id=lambda result, **kw: result.user.effective_tenant_id,
    get_user_id=lambda result, **kw: result.user.id,
    get_new_values=lambda result, **kw: {
        "email": result.user.email,
        "role": result.user.role,
        "login_time": datetime.utcnow().isoformat(),
    },
    summary_template="User {email} logged in successfully",
    skip_on_failure=False  # Log failed logins too!
)
async def login(
    data: LoginRequest,
    request: Request,  # Required for IP tracking
    db: AsyncSession = Depends(get_db)
):
    # Authenticate user
    user = await authenticate_user(db, data.email, data.password)

    # Create tokens
    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(user_id=user.id)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )
```

**What gets logged**:
- ✅ Successful login: `success=True`, user info captured
- ✅ Failed login: `success=False`, error message captured
- ✅ IP address and user agent automatically captured
- ✅ Tenant ID from user's tenant

### Failed Login (Manual Approach)

For more control over failed logins:

```python
from models.audit_trail import log_audit_trail

@router.post("/login")
async def login(
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await authenticate_user(db, data.email, data.password)

        # Log successful login
        await log_audit_trail(
            db=db,
            action_type="login",
            resource_type="user",
            resource_id=str(user.id),
            tenant_id=user.effective_tenant_id,
            user_id=user.id,
            new_values={
                "email": user.email,
                "login_time": datetime.utcnow().isoformat(),
            },
            changes_summary=f"User {user.email} logged in successfully",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )

        return create_tokens(user)

    except AuthenticationError as e:
        # Log failed login attempt
        await log_audit_trail(
            db=db,
            action_type="login",
            resource_type="user",
            resource_id=data.email,  # Email only, no user ID
            tenant_id=None,  # No tenant for failed login
            user_id=None,  # No authenticated user
            new_values={
                "attempted_email": data.email,
                "failure_reason": str(e),
            },
            changes_summary=f"Failed login attempt for {data.email}",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            success=False,
            error_message=str(e),
        )

        raise HTTPException(status_code=401, detail="Invalid credentials")
```

### Logout

```python
@router.post("/logout")
@audit_log(
    action_type="logout",
    resource_type="user",
    get_resource_id=lambda kwargs, **kw: str(kwargs["current_user"].id),
    summary_template="User logged out"
)
async def logout(
    data: LogoutRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
):
    # Revoke refresh token
    refresh_token_store.revoke(data.refresh_token)
    return {"message": "Logged out successfully"}
```

### Password Reset

```python
@router.post("/reset-password")
@audit_log(
    action_type="password_reset",
    resource_type="user",
    get_resource_id=lambda kwargs, **kw: str(kwargs["user_id"]),
    summary_template="Password reset for user ID {resource_id}"
)
async def reset_password(
    user_id: UUID,
    data: PasswordResetRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_role(["super_admin"])),
):
    user = await get_user_by_id(db, user_id)
    user.password_hash = hash_password(data.new_password)
    await db.commit()
    return {"message": "Password reset successfully"}
```

---

## User Management Logging

### Role Changes (Critical!)

```python
async def _fetch_old_role(kwargs, db):
    """Capture old role before update."""
    user_id = kwargs.get("user_id")
    user = await get_user_by_id(db, user_id)
    return {
        "old_values": {
            "role": user.role,
            "permissions": get_role_permissions(user.role),
        }
    }

@router.put("/users/{user_id}/role")
@audit_log(
    action_type="update",
    resource_type="user_role",  # Specific resource type!
    get_resource_id=lambda kwargs, **kw: str(kwargs["user_id"]),
    get_old_values=lambda context, **kw: context.get("old_values"),
    get_new_values=lambda result, **kw: {
        "role": result.role,
        "permissions": get_role_permissions(result.role),
    },
    before_handler=_fetch_old_role,
    summary_template="User role changed from {old_role} to {role}",
)
async def update_user_role(
    user_id: UUID,
    data: RoleUpdateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_role(["super_admin"])),
):
    user = await get_user_by_id(db, user_id)
    old_role = user.role
    user.role = data.role
    await db.commit()

    # Include old_role in result for summary template
    result = UserResponse.model_validate(user)
    result.old_role = old_role
    return result
```

### User Deletion

```python
async def _fetch_user_for_deletion(kwargs, db):
    """Capture user data before deletion."""
    user_id = kwargs.get("user_id")
    user = await get_user_by_id(db, user_id)
    return {
        "old_values": {
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "tenant_id": str(user.tenant_id) if user.tenant_id else None,
        }
    }

@router.delete("/users/{user_id}")
@audit_log(
    action_type="delete",
    resource_type="user",
    get_resource_id=lambda kwargs, **kw: str(kwargs["user_id"]),
    get_old_values=lambda context, **kw: context.get("old_values"),
    before_handler=_fetch_user_for_deletion,
    summary_template="User {email} deleted"
)
async def delete_user(
    user_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_role(["super_admin"])),
):
    user = await get_user_by_id(db, user_id)
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted"}
```

---

## Configuration Changes Logging

### Integration Configuration with Encrypted Fields

```python
async def _fetch_old_github_config(kwargs, db):
    """Fetch old GitHub config before update."""
    tenant_id = _get_effective_tenant_id(kwargs["current_user"])
    config = await get_github_config(db, tenant_id)
    return {
        "old_config": {
            "username": config.github_username,
            "repositories": config.github_repositories,
            "auto_create_issues": config.github_auto_create_issues,
            "access_token_set": bool(config.encrypted_github_access_token),
        }
    }

@router.put("/github/config")
@audit_log(
    action_type="update",
    resource_type="integration_config",
    get_resource_id=lambda current_user, **kw: f"github_{current_user.effective_tenant_id}",
    get_old_values=lambda context, **kw: context.get("old_config"),
    get_new_values=lambda result, **kw: {
        "username": result.github_username,
        "repositories": result.github_repositories,
        "auto_create_issues": result.github_auto_create_issues,
        "access_token_changed": result.get("_token_changed", False),
    },
    before_handler=_fetch_old_github_config,
    summary_template="GitHub integration updated for {username}",
    mask_fields=["access_token"]  # Mask sensitive fields!
)
async def update_github_config(
    config_data: GitHubConfigUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
):
    tenant_id = _get_effective_tenant_id(current_user)
    config = await get_github_config(db, tenant_id)

    # Track if token was changed
    token_changed = False

    if config_data.access_token:
        config.encrypted_github_access_token = encrypt_token(config_data.access_token)
        token_changed = True

    if config_data.username:
        config.github_username = config_data.username

    await db.commit()

    # Add flag to result for audit log
    result = GitHubConfigResponse.model_validate(config)
    result._token_changed = token_changed
    return result
```

### LLM Provider Configuration

```python
@router.post("/llm-providers")
@audit_create(
    resource_type="llm_provider_config",
    get_resource_id=lambda result, **kw: str(result.id),
    get_new_values=lambda result, **kw: {
        "provider": result.provider,
        "model_name": result.model_name,
        "is_default": result.is_default,
        "is_active": result.is_active,
        "api_key_set": bool(result.encrypted_api_key),
    },
    summary_template="{provider} provider configured for {model_name}",
    mask_fields=["api_key", "encrypted_api_key"]
)
async def create_provider_config(
    data: LLMProviderConfigCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
):
    config = LLMProviderConfig(
        **data.dict(exclude={"api_key"}),
        encrypted_api_key=encrypt_token(data.api_key),
        tenant_id=current_user.effective_tenant_id
    )
    db.add(config)
    await db.commit()
    return config
```

### Pattern Analysis Configuration

```python
async def _fetch_old_pattern_config(kwargs, db):
    """Fetch old pattern analysis config."""
    tenant_id = kwargs["current_user"].effective_tenant_id
    config = await get_pattern_config(db, tenant_id)
    return {
        "old_config": {
            "similarity_threshold": config.similarity_threshold,
            "llm_confidence_threshold": config.llm_confidence_threshold,
            "defect_auto_creation_threshold": config.defect_auto_creation_threshold,
            "llm_analysis_enabled": config.llm_analysis_enabled,
        }
    }

@router.put("/pattern-analysis/config")
@audit_update(
    resource_type="pattern_analysis_config",
    get_resource_id=lambda current_user, **kw: f"pattern_config_{current_user.effective_tenant_id}",
    get_old_values=lambda context, **kw: context.get("old_config"),
    get_new_values=lambda result, **kw: {
        "similarity_threshold": result.similarity_threshold,
        "llm_confidence_threshold": result.llm_confidence_threshold,
        "defect_auto_creation_threshold": result.defect_auto_creation_threshold,
        "llm_analysis_enabled": result.llm_analysis_enabled,
    },
    before_handler=_fetch_old_pattern_config,
    summary_template="Pattern analysis config updated (thresholds changed)"
)
async def update_pattern_config(
    data: PatternAnalysisConfigUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db),
):
    tenant_id = current_user.effective_tenant_id
    config = await get_pattern_config(db, tenant_id)

    for field, value in data.dict(exclude_unset=True).items():
        setattr(config, field, value)

    await db.commit()
    return config
```

---

## Sensitive Data Masking

The decorator automatically masks sensitive fields specified in `mask_fields`:

```python
@audit_update(
    resource_type="user",
    get_old_values=lambda context, **kw: {
        "email": "user@example.com",
        "password": "supersecret123",  # Will be masked
        "api_key": "sk-1234567890abcdefghijklmnop",  # Will be masked
    },
    get_new_values=lambda result, **kw: {
        "email": "user@example.com",
        "password": "newpassword456",  # Will be masked
        "api_key": "sk-0987654321zyxwvutsrqponm",  # Will be masked
    },
    mask_fields=["password", "api_key"]  # Specify fields to mask
)
```

**Audit log will contain**:
```json
{
    "old_values": {
        "email": "user@example.com",
        "password": "***MASKED***",
        "api_key": "sk-1...onm"
    },
    "new_values": {
        "email": "user@example.com",
        "password": "***MASKED***",
        "api_key": "sk-0...onm"
    }
}
```

---

## Advanced Patterns

### Custom Tenant ID Resolution

```python
def _get_tenant_from_resource(result, **kwargs):
    """Extract tenant ID from the created resource."""
    return result.tenant_id

@audit_create(
    resource_type="test_suite",
    get_tenant_id=_get_tenant_from_resource,  # Custom tenant extraction
    ...
)
```

### Conditional Audit Logging

```python
@router.put("/users/{user_id}")
async def update_user(user_id: UUID, data: UserUpdate, ...):
    user = await get_user_by_id(db, user_id)

    # Only log if role changed (critical change)
    if data.role and data.role != user.role:
        await log_audit_trail(
            db=db,
            action_type="update",
            resource_type="user_role",
            resource_id=str(user.id),
            old_values={"role": user.role},
            new_values={"role": data.role},
            changes_summary=f"User role changed from {user.role} to {data.role}",
            ...
        )

    # Update user
    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    await db.commit()
    return user
```

### Batch Operations

```python
@router.post("/users/bulk-update")
@audit_log(
    action_type="bulk_update",
    resource_type="user",
    get_new_values=lambda result, **kw: {
        "users_updated": len(result.updated_ids),
        "updated_ids": [str(id) for id in result.updated_ids],
    },
    summary_template="Bulk updated {users_updated} users"
)
async def bulk_update_users(...):
    ...
```

### Regression Baseline Approval

```python
@router.post("/regressions/{script_id}/baseline")
@audit_log(
    action_type="approve",
    resource_type="regression_baseline",
    get_resource_id=lambda kwargs, **kw: str(kwargs["script_id"]),
    get_new_values=lambda result, **kw: {
        "version": result.version,
        "status": result.snapshot_data.get("status"),
        "metrics": result.snapshot_data.get("metrics"),
        "note": result.note,
    },
    summary_template="Regression baseline v{version} approved for script"
)
async def approve_baseline(
    script_id: UUID,
    data: BaselineApprovalRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_role(["admin", "qa_lead"])),
):
    baseline = await create_baseline(db, script_id, data, current_user.id)
    return baseline
```

---

## Summary

### Best Practices

1. **Always add `request: Request` parameter** to enable IP/user agent tracking
2. **Use `mask_fields`** for sensitive data (passwords, API keys, tokens)
3. **Provide meaningful `summary_template`** for human-readable audit logs
4. **Use `before_handler`** to capture old values for updates/deletes
5. **Log both success and failure** (set `skip_on_failure=False` for critical operations)
6. **Use specific resource types** (e.g., `user_role` instead of just `user` for role changes)
7. **Never log actual passwords or unencrypted secrets** - only log that they changed

### When to Use Manual vs Decorator

**Use Decorator**:
- ✅ Standard CRUD operations
- ✅ Configuration changes
- ✅ Automated audit logging
- ✅ Consistent patterns

**Use Manual**:
- ✅ Complex conditional logging
- ✅ Failed operations with custom error handling
- ✅ Batch operations with aggregated data
- ✅ When you need fine-grained control

### Testing

Always test audit logging:

```python
async def test_user_creation_creates_audit_trail():
    # Create user
    response = await client.post("/users", json=user_data)

    # Verify audit trail
    audit = await db.execute(
        select(AuditTrail)
        .where(AuditTrail.action_type == "create")
        .where(AuditTrail.resource_type == "user")
        .order_by(AuditTrail.created_at.desc())
        .limit(1)
    )
    audit_entry = audit.scalar_one()

    assert audit_entry.success is True
    assert audit_entry.resource_id == str(response.json()["id"])
    assert audit_entry.tenant_id == current_user.effective_tenant_id
    assert "created" in audit_entry.changes_summary.lower()
```
