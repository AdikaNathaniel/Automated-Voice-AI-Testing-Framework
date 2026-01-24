# Settings Manager Guide

## Overview

The `SettingsManager` service provides a centralized, consistent way to manage application settings with a 3-tier hierarchy:

```
1. Organization Setting (tenant-specific override)
   ↓ (if not set)
2. Global Default (system-wide default)
   ↓ (if not set)
3. .env Default (application fallback)
```

## Benefits

✅ **Single source of truth** - All settings resolution in one place
✅ **Consistent hierarchy** - Same resolution order everywhere
✅ **Easy maintenance** - Change hierarchy logic once, applies everywhere
✅ **Transparent source tracking** - Know where each value came from
✅ **Type-safe defaults** - Proper type conversion from .env

## Basic Usage

### Import the Service

```python
from services.settings_manager import SettingsManager, get_setting
```

### Option 1: Use the Manager Class

```python
from sqlalchemy.ext.asyncio import AsyncSession
from services.settings_manager import SettingsManager

async def my_function(db: AsyncSession, tenant_id: UUID):
    manager = SettingsManager(db)

    # Get a specific setting
    lookback_days = await manager.get_pattern_analysis_setting(
        key="lookback_days_recent",
        tenant_id=tenant_id,
        default=7
    )

    # Get all settings with hierarchy applied
    all_settings = await manager.get_all_settings(
        setting_type="pattern_analysis",
        tenant_id=tenant_id,
        include_source=True  # Shows where each value came from
    )
```

### Option 2: Use the Convenience Function

```python
from services.settings_manager import get_setting

async def my_function(db: AsyncSession, tenant_id: UUID):
    lookback_days = await get_setting(
        db=db,
        key="lookback_days_recent",
        setting_type="pattern_analysis",
        tenant_id=tenant_id,
        default=7
    )
```

## Examples

### Example 1: Pattern Analysis Task

**Before (hardcoded):**
```python
async def analyze_patterns(db: AsyncSession, tenant_id: UUID):
    # Hardcoded values
    lookback_days = 7
    min_pattern_size = 3
    similarity_threshold = 0.85

    # Analysis logic...
```

**After (using SettingsManager):**
```python
from services.settings_manager import SettingsManager

async def analyze_patterns(db: AsyncSession, tenant_id: UUID):
    manager = SettingsManager(db)

    # Values respect org overrides → global defaults → .env
    lookback_days = await manager.get_pattern_analysis_setting(
        "lookback_days_recent", tenant_id, default=7
    )
    min_pattern_size = await manager.get_pattern_analysis_setting(
        "min_pattern_size", tenant_id, default=3
    )
    similarity_threshold = await manager.get_pattern_analysis_setting(
        "similarity_threshold", tenant_id, default=0.85
    )

    # Analysis logic...
```

### Example 2: API Endpoint

**Before:**
```python
@router.get("/config")
async def get_config(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db)
):
    # Directly query organization config
    config = await db.execute(
        select(PatternAnalysisConfig).where(
            PatternAnalysisConfig.tenant_id == current_user.tenant_id
        )
    )
    org_config = config.scalar_one_or_none()

    # Manual fallback logic
    lookback_days = org_config.lookback_days_recent if org_config else 7

    return {"lookback_days": lookback_days}
```

**After:**
```python
from services.settings_manager import get_setting

@router.get("/config")
async def get_config(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user_with_db)
):
    # Automatic hierarchy resolution
    lookback_days = await get_setting(
        db, "lookback_days_recent", "pattern_analysis",
        current_user.tenant_id, default=7
    )

    return {"lookback_days": lookback_days}
```

### Example 3: Get All Settings with Source Tracking

```python
manager = SettingsManager(db)

all_settings = await manager.get_all_settings(
    setting_type="pattern_analysis",
    tenant_id=tenant_id,
    include_source=True
)

# Result:
{
    "lookback_days_recent": {
        "value": 14,
        "source": "org_override"  # Org set custom value
    },
    "min_pattern_size": {
        "value": 3,
        "source": "env_default"  # Using .env default
    },
    "similarity_threshold": {
        "value": 0.9,
        "source": "global_default"  # Using system-wide default
    },
    ...
}
```

## Hierarchy Explained

### 1. Organization Setting (Highest Priority)

**Storage**: Database table with `tenant_id`
**Example**: `pattern_analysis_configs` table
**Who sets it**: Organization admins
**Purpose**: Organization-specific overrides

```python
# Organization "Acme Corp" sets custom values
lookback_days_recent = 14  # Override default of 7
min_pattern_size = 5       # Override default of 3
```

### 2. Global Default (Medium Priority)

**Storage**: Special database row (tenant_id = NULL) or global_defaults table
**Who sets it**: Super admins
**Purpose**: System-wide defaults for all organizations

**Note**: Currently not fully implemented - falls through to .env defaults.
**TODO**: Implement global_defaults table.

### 3. .env Default (Lowest Priority)

**Storage**: Environment variables or hardcoded defaults
**Who sets it**: DevOps/deployment configuration
**Purpose**: Application-level fallback

```env
# .env file
PATTERN_ANALYSIS_LOOKBACK_RECENT=7
PATTERN_ANALYSIS_LOOKBACK_MAX=90
PATTERN_ANALYSIS_MIN_SIZE=3
PATTERN_ANALYSIS_SIMILARITY=0.85
```

## Extending for New Setting Types

To add support for a new setting type (e.g., notifications):

### 1. Add Methods to SettingsManager

```python
class SettingsManager:
    # ... existing code ...

    async def get_notification_setting(
        self,
        key: str,
        tenant_id: Optional[UUID] = None,
        default: Any = None
    ) -> Any:
        """Get notification configuration setting with hierarchy."""
        # 1. Try organization-specific
        if tenant_id:
            org_value = await self._get_org_notification_setting(tenant_id, key)
            if org_value is not None:
                return org_value

        # 2. Try global default
        global_value = await self._get_global_notification_setting(key)
        if global_value is not None:
            return global_value

        # 3. Fall back to .env
        return self._get_env_notification_default(key, default)

    async def _get_org_notification_setting(self, tenant_id, key):
        # Query notification_configs table
        ...

    async def _get_global_notification_setting(self, key):
        # Query global defaults
        ...

    def _get_env_notification_default(self, key, fallback):
        # Map to .env variables
        defaults = {
            "email_enabled": os.getenv("NOTIFICATIONS_EMAIL", "true") == "true",
            "slack_enabled": os.getenv("NOTIFICATIONS_SLACK", "false") == "true",
            ...
        }
        return defaults.get(key, fallback)
```

### 2. Update Generic Getter

```python
async def get_setting(
    self,
    key: str,
    setting_type: str = "pattern_analysis",
    tenant_id: Optional[UUID] = None,
    default: Any = None
) -> Any:
    if setting_type == "pattern_analysis":
        return await self.get_pattern_analysis_setting(key, tenant_id, default)
    elif setting_type == "notification":  # NEW
        return await self.get_notification_setting(key, tenant_id, default)
    # ... other types ...
    return default
```

## Best Practices

### ✅ DO

- **Use SettingsManager for all settings access**
  Replace direct database queries with hierarchy-aware getters

- **Provide sensible defaults**
  Always pass a `default` parameter to prevent None returns

- **Use type conversion**
  Convert .env strings to proper types (int, float, bool)

- **Document setting keys**
  Keep a registry of all supported setting keys

### ❌ DON'T

- **Don't query settings tables directly**
  Use SettingsManager to ensure hierarchy is respected

- **Don't hardcode settings**
  Use SettingsManager with defaults instead

- **Don't mix hierarchy implementations**
  Centralize all hierarchy logic in SettingsManager

## Migration Guide

### Step 1: Identify Hardcoded Settings

Search for hardcoded values that should be configurable:
```bash
grep -r "lookback.*=.*7" backend/
grep -r "min_pattern_size.*=.*3" backend/
```

### Step 2: Replace with SettingsManager

```python
# Before
def some_function():
    lookback_days = 7  # Hardcoded

# After
async def some_function(db: AsyncSession, tenant_id: UUID):
    from services.settings_manager import get_setting
    lookback_days = await get_setting(
        db, "lookback_days_recent", "pattern_analysis",
        tenant_id, default=7
    )
```

### Step 3: Test Hierarchy

```python
# Test that hierarchy works correctly
async def test_settings_hierarchy():
    manager = SettingsManager(db)

    # No org setting, should use default
    value1 = await manager.get_pattern_analysis_setting(
        "lookback_days_recent", tenant_id=org_uuid, default=7
    )
    assert value1 == 7  # Uses .env default

    # Set org override
    org_config.lookback_days_recent = 14
    await db.commit()

    # Should now use org override
    value2 = await manager.get_pattern_analysis_setting(
        "lookback_days_recent", tenant_id=org_uuid, default=7
    )
    assert value2 == 14  # Uses org override
```

## Future Enhancements

### TODO: Implement Global Defaults Table

Create a `global_defaults` table to store super-admin configured defaults:

```sql
CREATE TABLE global_defaults (
    id UUID PRIMARY KEY,
    setting_type VARCHAR(50) NOT NULL,
    setting_key VARCHAR(100) NOT NULL,
    setting_value JSONB NOT NULL,
    created_by UUID,
    updated_at TIMESTAMP,
    UNIQUE (setting_type, setting_key)
);
```

### TODO: Settings UI

Create UI for:
- **Super admin**: Manage global defaults
- **Org admin**: Override settings for their organization
- **Indicator badges**: Show which settings are using defaults vs overrides

## Support

For questions or issues with SettingsManager:
1. Check this guide first
2. Review `backend/services/settings_manager.py` implementation
3. Check existing usage in codebase
4. Consult team lead for architectural decisions
