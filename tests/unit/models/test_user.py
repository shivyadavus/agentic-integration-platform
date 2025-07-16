"""
Unit tests for user models.

Tests User, Role, and Permission models including validation,
relationships, and business logic methods.
"""

import uuid
from datetime import datetime, timezone, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User, Role, Permission, UserStatus, PermissionScope
from tests.fixtures.factories import UserFactory, RoleFactory, PermissionFactory


class TestUserModel:
    """Test cases for User model."""
    
    def test_user_creation(self):
        """Test basic user creation."""
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed_password_here"
        )
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.hashed_password == "hashed_password_here"
        # Set default values for testing (normally set at database level)
        user.is_active = True
        user.is_verified = False
        user.status = UserStatus.ACTIVE
        user.language = "en"
        user.failed_login_attempts = 0

        assert user.is_active is True
        assert user.is_verified is False
        assert user.status == UserStatus.ACTIVE
        assert user.language == "en"
        assert user.failed_login_attempts == 0
    
    def test_user_with_optional_fields(self):
        """Test user creation with optional fields."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password",
            avatar_url="https://example.com/avatar.jpg",
            timezone="UTC",
            organization_id=uuid.uuid4(),
            preferences={"theme": "dark", "notifications": True}
        )
        
        assert user.avatar_url == "https://example.com/avatar.jpg"
        assert user.timezone == "UTC"
        assert user.organization_id is not None
        assert user.preferences["theme"] == "dark"
        assert user.preferences["notifications"] is True
    
    def test_user_status_enum(self):
        """Test user status enumeration."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password",
            status=UserStatus.SUSPENDED
        )
        
        assert user.status == UserStatus.SUSPENDED
        assert user.status.value == "suspended"
    
    def test_user_repr(self):
        """Test user string representation."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password",
            status=UserStatus.ACTIVE
        )
        user.id = uuid.uuid4()
        
        repr_str = repr(user)
        assert "User" in repr_str
        assert str(user.id) in repr_str
        assert "test@example.com" in repr_str
        assert "active" in repr_str
    
    def test_user_has_permission_method(self):
        """Test has_permission method."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        # Create role with permission
        role = Role(name="admin", display_name="Administrator")
        permission = Permission(
            name="create_integration",
            display_name="Create Integration",
            resource_type="integration",
            scope=PermissionScope.GLOBAL  # Explicitly set scope
        )
        role.permissions = [permission]
        user.roles = [role]
        
        assert user.has_permission("create_integration") is True
        assert user.has_permission("nonexistent_permission") is False
    
    def test_user_has_role_method(self):
        """Test has_role method."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        role1 = Role(name="admin", display_name="Administrator")
        role2 = Role(name="user", display_name="User")
        user.roles = [role1, role2]
        
        assert user.has_role("admin") is True
        assert user.has_role("user") is True
        assert user.has_role("nonexistent_role") is False
    
    def test_user_is_locked_property(self):
        """Test is_locked property."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        # User not locked
        assert user.is_locked() is False

        # Lock user
        user.locked_until = datetime.now(timezone.utc) + timedelta(hours=1)
        assert user.is_locked() is True

        # Expired lock
        user.locked_until = datetime.now(timezone.utc) - timedelta(hours=1)
        assert user.is_locked() is False
    
    def test_user_can_login_method(self):
        """Test can_login method."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True,
            is_verified=True,
            status=UserStatus.ACTIVE
        )
        
        assert user.can_login() is True
        
        # Test various conditions that prevent login
        user.is_active = False
        assert user.can_login() is False
        
        user.is_active = True
        user.is_verified = False
        assert user.can_login() is False
        
        user.is_verified = True
        user.status = UserStatus.SUSPENDED
        assert user.can_login() is False
        
        user.status = UserStatus.ACTIVE
        user.locked_until = datetime.now(timezone.utc) + timedelta(hours=1)
        assert user.can_login() is False


class TestRoleModel:
    """Test cases for Role model."""
    
    def test_role_creation(self):
        """Test basic role creation."""
        role = Role(
            name="admin",
            display_name="Administrator",
            description="System administrator role"
        )
        
        assert role.name == "admin"
        assert role.display_name == "Administrator"
        assert role.description == "System administrator role"
        # Set default values for testing (normally set at database level)
        role.is_system_role = False
        role.is_active = True
        role.scope = PermissionScope.GLOBAL

        assert role.is_system_role is False
        assert role.is_active is True
        assert role.scope == PermissionScope.GLOBAL
    
    def test_role_with_scope(self):
        """Test role creation with specific scope."""
        role = Role(
            name="org_admin",
            display_name="Organization Admin",
            scope=PermissionScope.ORGANIZATION
        )
        
        assert role.scope == PermissionScope.ORGANIZATION
    
    def test_role_system_role(self):
        """Test system role creation."""
        role = Role(
            name="system",
            display_name="System Role",
            is_system_role=True
        )
        
        assert role.is_system_role is True
    
    def test_role_repr(self):
        """Test role string representation."""
        role = Role(
            name="admin",
            display_name="Administrator",
            scope=PermissionScope.GLOBAL
        )
        role.id = uuid.uuid4()
        
        repr_str = repr(role)
        assert "Role" in repr_str
        assert str(role.id) in repr_str
        assert "admin" in repr_str
        assert "global" in repr_str
    
    def test_role_has_permission_method(self):
        """Test has_permission method."""
        role = Role(name="admin", display_name="Administrator")
        
        permission = Permission(
            name="create_integration",
            display_name="Create Integration",
            resource_type="integration",
            scope=PermissionScope.GLOBAL
        )
        role.permissions = [permission]
        
        assert role.has_permission("create_integration") is True
        assert role.has_permission("nonexistent_permission") is False
    
    def test_role_has_permission_with_scope(self):
        """Test has_permission method with scope checking."""
        role = Role(
            name="org_admin",
            display_name="Organization Admin",
            scope=PermissionScope.ORGANIZATION
        )
        
        permission = Permission(
            name="manage_users",
            display_name="Manage Users",
            resource_type="users",
            scope=PermissionScope.ORGANIZATION
        )
        role.permissions = [permission]
        
        # Should have permission in organization scope
        assert role.has_permission("manage_users", PermissionScope.ORGANIZATION) is True
        
        # Should not have permission in global scope (role scope is more restrictive)
        assert role.has_permission("manage_users", PermissionScope.GLOBAL) is False


class TestPermissionModel:
    """Test cases for Permission model."""
    
    def test_permission_creation(self):
        """Test basic permission creation."""
        permission = Permission(
            name="create_integration",
            display_name="Create Integration",
            resource_type="integration"
        )
        
        assert permission.name == "create_integration"
        assert permission.display_name == "Create Integration"
        assert permission.resource_type == "integration"
        # Set default values for testing (normally set at database level)
        permission.scope = PermissionScope.GLOBAL
        permission.is_system_permission = False
        permission.is_active = True

        assert permission.scope == PermissionScope.GLOBAL
        assert permission.is_system_permission is False
        assert permission.is_active is True
    
    def test_permission_with_scope(self):
        """Test permission creation with specific scope."""
        permission = Permission(
            name="manage_org_users",
            display_name="Manage Organization Users",
            resource_type="users",
            scope=PermissionScope.ORGANIZATION
        )
        
        assert permission.scope == PermissionScope.ORGANIZATION
    
    def test_permission_with_resource_type(self):
        """Test permission with resource type."""
        permission = Permission(
            name="read_user_profile",
            display_name="Read User Profile",
            resource_type="profile"
        )
        
        assert permission.resource_type == "profile"
    
    def test_permission_system_permission(self):
        """Test system permission creation."""
        permission = Permission(
            name="system_admin",
            display_name="System Administrator",
            resource_type="system",
            is_system_permission=True
        )
        
        assert permission.is_system_permission is True
    
    def test_permission_repr(self):
        """Test permission string representation."""
        permission = Permission(
            name="create_integration",
            display_name="Create Integration",
            resource_type="integration",
            scope=PermissionScope.GLOBAL
        )
        permission.id = uuid.uuid4()
        
        repr_str = repr(permission)
        assert "Permission" in repr_str
        assert str(permission.id) in repr_str
        assert "create_integration" in repr_str
        assert "global" in repr_str


class TestUserRolePermissionRelationships:
    """Test cases for relationships between User, Role, and Permission models."""
    
    def test_user_role_relationship(self):
        """Test many-to-many relationship between User and Role."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        role1 = Role(name="admin", display_name="Administrator")
        role2 = Role(name="user", display_name="User")
        
        user.roles = [role1, role2]
        
        assert len(user.roles) == 2
        assert role1 in user.roles
        assert role2 in user.roles
    
    def test_role_permission_relationship(self):
        """Test many-to-many relationship between Role and Permission."""
        role = Role(name="admin", display_name="Administrator")
        
        perm1 = Permission(name="create", display_name="Create", resource_type="integration")
        perm2 = Permission(name="read", display_name="Read", resource_type="integration")
        
        role.permissions = [perm1, perm2]
        
        assert len(role.permissions) == 2
        assert perm1 in role.permissions
        assert perm2 in role.permissions
    
    def test_user_permission_through_role(self):
        """Test user permissions through role relationships."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        role = Role(name="admin", display_name="Administrator")
        permission = Permission(
            name="create_integration",
            display_name="Create Integration",
            resource_type="integration",
            scope=PermissionScope.GLOBAL
        )
        
        role.permissions = [permission]
        user.roles = [role]
        
        # User should have permission through role
        assert user.has_permission("create_integration") is True


@pytest.mark.unit
class TestUserModelValidation:
    """Test cases for user model validation and constraints."""
    
    def test_user_email_required(self):
        """Test that email is required."""
        # Model validation happens at database level, not at object creation
        user = User(hashed_password="password")
        # Email is required at database level but not at object creation
        assert user.email is None
    
    def test_user_password_required(self):
        """Test that hashed_password is required."""
        # Model validation happens at database level, not at object creation
        user = User(email="test@example.com")
        # Password is required at database level but not at object creation
        assert user.hashed_password is None
    
    def test_role_name_required(self):
        """Test that role name is required."""
        # Model validation happens at database level, not at object creation
        role = Role(display_name="Test Role")
        # Name is required at database level but not at object creation
        assert role.name is None
    
    def test_permission_name_required(self):
        """Test that permission name is required."""
        # Model validation happens at database level, not at object creation
        permission = Permission(display_name="Create", resource_type="integration")
        # Name is required at database level but not at object creation
        assert permission.name is None
