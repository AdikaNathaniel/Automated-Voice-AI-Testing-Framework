"""
Organization Service

Handles organization management including:
- Creating organizations (super_admin only)
- Managing organization members
- Organization settings

The multi-tenancy model:
- Users with is_organization_owner=True represent organizations
- Their user.id becomes the tenant_id for all organization members
- Regular users can have their tenant_id set to an org owner's id
- Individual users (tenant_id=None) use their own id as effective tenant
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


logger = logging.getLogger(__name__)


class OrganizationService:
    """Service for managing organizations and their members."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_organization(
        self,
        name: str,
        admin_email: str,
        admin_username: str,
        admin_password: str,
        admin_full_name: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> User:
        """Create a new organization.

        Creates a User record that represents the organization.
        This user's id becomes the tenant_id for all org members.

        Args:
            name: Organization name
            admin_email: Email for the organization admin account
            admin_username: Username for the organization admin account
            admin_password: Password for the organization admin account
            admin_full_name: Optional full name for the admin
            settings: Optional organization settings

        Returns:
            User: The created organization owner user

        Note:
            Only super_admin users should be able to call this.
            Authorization is handled at the route level.
        """
        from api.auth.password import hash_password

        org_user = User(
            email=admin_email,
            username=admin_username,
            password_hash=hash_password(admin_password),
            full_name=admin_full_name or name,
            role="org_admin",
            is_active=True,
            is_organization_owner=True,
            organization_name=name,
            organization_settings=settings or {},
            tenant_id=None,  # Org owners don't have a tenant_id
        )

        self.db.add(org_user)
        await self.db.flush()
        await self.db.refresh(org_user)

        logger.info(f"Created organization '{name}' with ID {org_user.id}")
        return org_user

    async def get_organization(self, org_id: UUID) -> Optional[User]:
        """Get an organization by its ID.

        Args:
            org_id: The organization's user ID

        Returns:
            User if found and is an organization owner, None otherwise
        """
        result = await self.db.execute(
            select(User).where(
                User.id == org_id,
                User.is_organization_owner == True  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def get_organization_by_name(self, name: str) -> Optional[User]:
        """Get an organization by its name.

        Args:
            name: Organization name

        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(
            select(User).where(
                User.organization_name == name,
                User.is_organization_owner == True  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def list_organizations(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[User], int]:
        """List all organizations.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of organization users, total count)
        """
        # Get total count
        count_result = await self.db.execute(
            select(func.count()).where(
                User.is_organization_owner == True  # noqa: E712
            )
        )
        total = count_result.scalar() or 0

        # Get organizations
        result = await self.db.execute(
            select(User)
            .where(User.is_organization_owner == True)  # noqa: E712
            .order_by(User.organization_name)
            .offset(skip)
            .limit(limit)
        )
        orgs = list(result.scalars().all())

        return orgs, total

    async def update_organization(
        self,
        org_id: UUID,
        name: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[User]:
        """Update an organization's details.

        Args:
            org_id: Organization ID
            name: New organization name
            settings: New settings (merged with existing)
            is_active: Whether the organization is active

        Returns:
            Updated User or None if not found
        """
        org = await self.get_organization(org_id)
        if not org:
            return None

        if name is not None:
            org.organization_name = name

        if settings is not None:
            current_settings = org.organization_settings or {}
            current_settings.update(settings)
            org.organization_settings = current_settings

        if is_active is not None:
            org.is_active = is_active

        await self.db.flush()
        await self.db.refresh(org)

        logger.info(f"Updated organization {org_id}")
        return org

    async def add_member(
        self,
        org_id: UUID,
        user_id: UUID,
        role: str = "user",
    ) -> Optional[User]:
        """Add a user to an organization.

        Sets the user's tenant_id to the organization's id.

        Args:
            org_id: Organization ID
            user_id: User ID to add
            role: Role to assign within the organization

        Returns:
            Updated User or None if org/user not found
        """
        # Verify org exists
        org = await self.get_organization(org_id)
        if not org:
            logger.warning(f"Organization {org_id} not found")
            return None

        # Get the user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            logger.warning(f"User {user_id} not found")
            return None

        # Don't allow adding org owners to other orgs
        if user.is_organization_owner:
            logger.warning(f"Cannot add organization owner {user_id} to another org")
            return None

        # Set the tenant_id
        user.tenant_id = org_id
        user.role = role

        await self.db.flush()
        await self.db.refresh(user)

        logger.info(f"Added user {user_id} to organization {org_id}")
        return user

    async def remove_member(self, org_id: UUID, user_id: UUID) -> Optional[User]:
        """Remove a user from an organization.

        Clears the user's tenant_id.

        Args:
            org_id: Organization ID
            user_id: User ID to remove

        Returns:
            Updated User or None if not found/not a member
        """
        result = await self.db.execute(
            select(User).where(
                User.id == user_id,
                User.tenant_id == org_id
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            return None

        user.tenant_id = None
        user.role = "user"  # Reset to default role

        await self.db.flush()
        await self.db.refresh(user)

        logger.info(f"Removed user {user_id} from organization {org_id}")
        return user

    async def list_members(
        self,
        org_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[User], int]:
        """List all members of an organization.

        Args:
            org_id: Organization ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of member users, total count)
        """
        # Verify org exists
        org = await self.get_organization(org_id)
        if not org:
            return [], 0

        # Get total count
        count_result = await self.db.execute(
            select(func.count()).where(User.tenant_id == org_id)
        )
        total = count_result.scalar() or 0

        # Get members
        result = await self.db.execute(
            select(User)
            .where(User.tenant_id == org_id)
            .order_by(User.username)
            .offset(skip)
            .limit(limit)
        )
        members = list(result.scalars().all())

        return members, total

    async def get_member_count(self, org_id: UUID) -> int:
        """Get the number of members in an organization.

        Args:
            org_id: Organization ID

        Returns:
            Number of members
        """
        result = await self.db.execute(
            select(func.count()).where(User.tenant_id == org_id)
        )
        return result.scalar() or 0

    async def transfer_ownership(
        self,
        org_id: UUID,
        new_owner_id: UUID,
    ) -> Optional[User]:
        """Transfer organization ownership to another member.

        The current org owner becomes a regular admin member.
        The new owner gets is_organization_owner=True.

        Args:
            org_id: Organization ID
            new_owner_id: User ID of the new owner

        Returns:
            New owner User or None if not possible
        """
        org = await self.get_organization(org_id)
        if not org:
            return None

        # Get new owner (must be a member)
        result = await self.db.execute(
            select(User).where(
                User.id == new_owner_id,
                User.tenant_id == org_id
            )
        )
        new_owner = result.scalar_one_or_none()
        if not new_owner:
            logger.warning(f"User {new_owner_id} is not a member of org {org_id}")
            return None

        # Transfer ownership
        # 1. Demote current owner
        org.is_organization_owner = False
        org.tenant_id = org_id  # Becomes a member of their own org
        org.role = "org_admin"

        # 2. Promote new owner
        new_owner.is_organization_owner = True
        new_owner.organization_name = org.organization_name
        new_owner.organization_settings = org.organization_settings
        new_owner.tenant_id = None  # Org owners don't have tenant_id

        # 3. Update all members to point to new owner
        await self.db.execute(
            User.__table__.update()
            .where(User.tenant_id == org_id)
            .values(tenant_id=new_owner_id)
        )

        await self.db.flush()
        await self.db.refresh(new_owner)

        logger.info(f"Transferred ownership of org {org_id} to {new_owner_id}")
        return new_owner

    async def delete_organization(self, org_id: UUID) -> bool:
        """Delete an organization.

        All members will have their tenant_id cleared.
        The organization owner user record is NOT deleted.

        Args:
            org_id: Organization ID

        Returns:
            True if deleted, False if not found
        """
        org = await self.get_organization(org_id)
        if not org:
            return False

        # Clear tenant_id from all members
        await self.db.execute(
            User.__table__.update()
            .where(User.tenant_id == org_id)
            .values(tenant_id=None)
        )

        # Mark org as inactive rather than deleting
        org.is_active = False
        org.is_organization_owner = False

        await self.db.flush()

        logger.info(f"Deleted organization {org_id}")
        return True
