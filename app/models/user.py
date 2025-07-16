"""
User and authentication domain models for the agentic integration platform.

This module defines models for user management, roles, permissions,
and authentication/authorization functionality.
"""

import enum
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, Enum, ForeignKey, String, Text, Boolean, Table
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin, AuditMixin, MetadataMixin


# Association tables for many-to-many relationships
user_roles = Table(
    "user_roles",
    BaseModel.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True),
)

role_permissions = Table(
    "role_permissions", 
    BaseModel.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id"), primary_key=True),
)


class UserStatus(enum.Enum):
    """User account status."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    ARCHIVED = "archived"


class PermissionScope(enum.Enum):
    """Permission scope levels."""
    
    GLOBAL = "global"          # System-wide permissions
    ORGANIZATION = "organization"  # Organization-level permissions
    PROJECT = "project"        # Project-level permissions
    RESOURCE = "resource"      # Specific resource permissions


class User(BaseModel, TimestampMixin, AuditMixin, MetadataMixin):
    """
    User model for authentication and authorization.
    
    Stores user account information, authentication credentials,
    and relationships to roles and permissions.
    """
    
    __tablename__ = "users"
    
    # Basic Information
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Authentication
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Status
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus),
        default=UserStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Profile Information
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    timezone: Mapped[Optional[str]] = mapped_column(String(50))
    language: Mapped[str] = mapped_column(String(10), default="en")
    
    # Security
    last_login_at: Mapped[Optional[datetime]] = mapped_column()
    password_changed_at: Mapped[Optional[datetime]] = mapped_column()
    failed_login_attempts: Mapped[int] = mapped_column(default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column()
    
    # API Access
    api_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    api_key_created_at: Mapped[Optional[datetime]] = mapped_column()
    
    # Organization Context
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        index=True
    )
    
    # Preferences
    preferences: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', status={self.status.value})>"
    
    def has_permission(self, permission_name: str, scope: PermissionScope = PermissionScope.GLOBAL) -> bool:
        """Check if user has a specific permission."""
        for role in self.roles:
            if role.has_permission(permission_name, scope):
                return True
        return False
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)
    
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.has_role("admin")
    
    def is_locked(self) -> bool:
        """Check if user account is locked."""
        return self.locked_until is not None and self.locked_until > datetime.now(timezone.utc)
    
    def can_login(self) -> bool:
        """Check if user can log in."""
        return (
            self.is_active and
            self.is_verified and
            self.status == UserStatus.ACTIVE and
            not self.is_locked()
        )
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences."""
        return self.preferences or {}
    
    def set_preference(self, key: str, value: Any) -> None:
        """Set a user preference."""
        prefs = self.get_preferences()
        prefs[key] = value
        self.preferences = prefs
    
    def record_login(self) -> None:
        """Record successful login."""
        self.last_login_at = datetime.utcnow()
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def record_failed_login(self) -> None:
        """Record failed login attempt."""
        self.failed_login_attempts += 1
        # Lock account after 5 failed attempts for 30 minutes
        if self.failed_login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)


class Role(BaseModel, TimestampMixin, AuditMixin, MetadataMixin):
    """
    Role model for role-based access control.
    
    Defines roles that can be assigned to users, with associated
    permissions and scope restrictions.
    """
    
    __tablename__ = "roles"
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Configuration
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Scope
    scope: Mapped[PermissionScope] = mapped_column(
        Enum(PermissionScope),
        default=PermissionScope.GLOBAL,
        nullable=False
    )
    
    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles"
    )
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles"
    )
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}', scope={self.scope.value})>"
    
    def has_permission(self, permission_name: str, scope: PermissionScope = PermissionScope.GLOBAL) -> bool:
        """Check if role has a specific permission."""
        for permission in self.permissions:
            if permission.name == permission_name and permission.scope == scope:
                return True
        return False
    
    def add_permission(self, permission: "Permission") -> None:
        """Add permission to role."""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission: "Permission") -> None:
        """Remove permission from role."""
        if permission in self.permissions:
            self.permissions.remove(permission)


class Permission(BaseModel, TimestampMixin, MetadataMixin):
    """
    Permission model for fine-grained access control.
    
    Defines specific permissions that can be granted to roles,
    with scope and resource restrictions.
    """
    
    __tablename__ = "permissions"
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Scope and Resource
    scope: Mapped[PermissionScope] = mapped_column(
        Enum(PermissionScope),
        default=PermissionScope.GLOBAL,
        nullable=False,
        index=True
    )
    resource_type: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Configuration
    is_system_permission: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions"
    )
    
    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name='{self.name}', scope={self.scope.value})>"
    
    @classmethod
    def create_system_permissions(cls) -> List["Permission"]:
        """Create default system permissions."""
        permissions = [
            # Integration permissions
            cls(name="integration.create", display_name="Create Integrations"),
            cls(name="integration.read", display_name="Read Integrations"),
            cls(name="integration.update", display_name="Update Integrations"),
            cls(name="integration.delete", display_name="Delete Integrations"),
            cls(name="integration.deploy", display_name="Deploy Integrations"),
            cls(name="integration.execute", display_name="Execute Integrations"),
            
            # Knowledge graph permissions
            cls(name="knowledge.read", display_name="Read Knowledge Graph"),
            cls(name="knowledge.write", display_name="Write Knowledge Graph"),
            cls(name="knowledge.admin", display_name="Administer Knowledge Graph"),
            
            # AI service permissions
            cls(name="ai.use", display_name="Use AI Services"),
            cls(name="ai.configure", display_name="Configure AI Models"),
            
            # System permissions
            cls(name="system.admin", display_name="System Administration"),
            cls(name="user.manage", display_name="Manage Users"),
            cls(name="role.manage", display_name="Manage Roles"),
        ]
        
        for permission in permissions:
            permission.is_system_permission = True
        
        return permissions
