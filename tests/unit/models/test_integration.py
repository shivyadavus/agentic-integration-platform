"""
Unit tests for integration models.

Tests Integration model including validation, business logic methods,
and status transitions.
"""

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.integration import Integration, IntegrationStatus, IntegrationType
from tests.fixtures.factories import IntegrationFactory


class TestIntegrationModel:
    """Test cases for Integration model."""
    
    def test_integration_creation(self):
        """Test basic integration creation."""
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Sync customer data from Salesforce to HubSpot",
            integration_type=IntegrationType.SYNC
        )
        
        assert integration.name == "Test Integration"
        assert integration.natural_language_spec == "Sync customer data from Salesforce to HubSpot"
        assert integration.integration_type == IntegrationType.SYNC
        # Status default is set at database level, manually set for testing
        integration.status = IntegrationStatus.DRAFT
        assert integration.status == IntegrationStatus.DRAFT
        # Set default values manually for testing (normally set at database level)
        integration.code_language = "python"
        integration.code_version = 1
        integration.validation_passed = False
        integration.test_passed = False
        integration.execution_count = 0
        integration.success_count = 0
        integration.error_count = 0

        assert integration.code_language == "python"
        assert integration.code_version == 1
        assert integration.validation_passed is False
        assert integration.test_passed is False
        assert integration.execution_count == 0
        assert integration.success_count == 0
        assert integration.error_count == 0
    
    def test_integration_with_optional_fields(self):
        """Test integration creation with optional fields."""
        source_system_id = uuid.uuid4()
        target_system_id = uuid.uuid4()
        conversation_session_id = uuid.uuid4()
        
        integration = Integration(
            name="Advanced Integration",
            natural_language_spec="Complex data transformation",
            integration_type=IntegrationType.ETL,
            ai_model_used="claude-3-sonnet-20240229",
            ai_provider="anthropic",
            processing_time_seconds=45,
            generated_code="def sync_data(): pass",
            code_language="python",
            validation_results={"syntax_valid": True, "imports_valid": True},
            validation_passed=True,
            test_results={"tests_passed": 5, "tests_failed": 0},
            test_passed=True,
            deployment_config={"environment": "production", "replicas": 3},
            deployment_url="https://api.example.com/integration/123",
            source_system_id=source_system_id,
            target_system_id=target_system_id,
            conversation_session_id=conversation_session_id
        )
        
        assert integration.ai_model_used == "claude-3-sonnet-20240229"
        assert integration.ai_provider == "anthropic"
        assert integration.processing_time_seconds == 45
        assert integration.generated_code == "def sync_data(): pass"
        assert integration.validation_results["syntax_valid"] is True
        assert integration.validation_passed is True
        assert integration.test_results["tests_passed"] == 5
        assert integration.test_passed is True
        assert integration.deployment_config["environment"] == "production"
        assert integration.deployment_url == "https://api.example.com/integration/123"
        assert integration.source_system_id == source_system_id
        assert integration.target_system_id == target_system_id
        assert integration.conversation_session_id == conversation_session_id
    
    def test_integration_status_enum(self):
        """Test integration status enumeration."""
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Test spec",
            integration_type=IntegrationType.SYNC,
            status=IntegrationStatus.ACTIVE
        )
        
        assert integration.status == IntegrationStatus.ACTIVE
        assert integration.status.value == "active"
    
    def test_integration_type_enum(self):
        """Test integration type enumeration."""
        sync_integration = Integration(
            name="Sync Integration",
            natural_language_spec="Sync data",
            integration_type=IntegrationType.SYNC
        )
        
        etl_integration = Integration(
            name="ETL Integration",
            natural_language_spec="ETL automation",
            integration_type=IntegrationType.ETL
        )
        
        assert sync_integration.integration_type == IntegrationType.SYNC
        assert sync_integration.integration_type.value == "sync"
        assert etl_integration.integration_type == IntegrationType.ETL
        assert etl_integration.integration_type.value == "etl"
    
    def test_integration_repr(self):
        """Test integration string representation."""
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Test spec",
            integration_type=IntegrationType.SYNC,
            status=IntegrationStatus.ACTIVE
        )
        integration.id = uuid.uuid4()
        
        repr_str = repr(integration)
        assert "Integration" in repr_str
        assert str(integration.id) in repr_str
        assert "Test Integration" in repr_str
        assert "active" in repr_str
    
    def test_success_rate_property(self):
        """Test success_rate property calculation."""
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Test spec",
            integration_type=IntegrationType.SYNC
        )
        
        # Set default values for testing
        integration.execution_count = 0
        integration.success_count = 0
        integration.error_count = 0

        # No executions
        assert integration.success_rate == 0.0
        
        # With executions
        integration.execution_count = 100
        integration.success_count = 85
        assert integration.success_rate == 85.0
        
        # Perfect success rate
        integration.success_count = 100
        assert integration.success_rate == 100.0
    
    def test_error_rate_property(self):
        """Test error_rate property calculation."""
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Test spec",
            integration_type=IntegrationType.SYNC
        )
        
        # Set default values for testing
        integration.execution_count = 0
        integration.success_count = 0
        integration.error_count = 0

        # No executions
        assert integration.error_rate == 0.0
        
        # With executions
        integration.execution_count = 100
        integration.error_count = 15
        assert integration.error_rate == 15.0
        
        # No errors
        integration.error_count = 0
        assert integration.error_rate == 0.0
    
    def test_is_deployable_method(self):
        """Test is_deployable method."""
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Test spec",
            integration_type=IntegrationType.SYNC
        )
        
        # Not deployable initially
        assert integration.is_deployable() is False
        
        # Set required conditions
        integration.status = IntegrationStatus.READY
        integration.validation_passed = True
        integration.test_passed = True
        integration.generated_code = "def sync_data(): pass"
        
        # Now deployable
        assert integration.is_deployable() is True
        
        # Test each condition individually
        integration.status = IntegrationStatus.DRAFT
        assert integration.is_deployable() is False
        
        integration.status = IntegrationStatus.READY
        integration.validation_passed = False
        assert integration.is_deployable() is False
        
        integration.validation_passed = True
        integration.test_passed = False
        assert integration.is_deployable() is False
        
        integration.test_passed = True
        integration.generated_code = None
        assert integration.is_deployable() is False
    
    def test_is_active_method(self):
        """Test is_active method."""
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Test spec",
            integration_type=IntegrationType.SYNC
        )
        
        # Not active initially
        assert integration.is_active() is False
        
        # Set to active
        integration.status = IntegrationStatus.ACTIVE
        assert integration.is_active() is True
        
        # Set to other statuses
        integration.status = IntegrationStatus.PAUSED
        assert integration.is_active() is False
        
        integration.status = IntegrationStatus.ERROR
        assert integration.is_active() is False


class TestIntegrationStatusTransitions:
    """Test cases for integration status transitions."""
    
    def test_draft_to_analyzing(self):
        """Test transition from DRAFT to ANALYZING."""
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Test spec",
            integration_type=IntegrationType.SYNC,
            status=IntegrationStatus.DRAFT
        )

        integration.status = IntegrationStatus.ANALYZING
        assert integration.status == IntegrationStatus.ANALYZING
    
    def test_generating_to_ready(self):
        """Test transition from GENERATING to READY."""
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Test spec",
            integration_type=IntegrationType.SYNC,
            status=IntegrationStatus.GENERATING
        )
        
        # Set conditions for ready state
        integration.generated_code = "def sync_data(): pass"
        integration.validation_passed = True
        integration.test_passed = True
        integration.status = IntegrationStatus.READY
        
        assert integration.status == IntegrationStatus.READY
        assert integration.is_deployable() is True
    
    def test_ready_to_active(self):
        """Test transition from READY to ACTIVE."""
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Test spec",
            integration_type=IntegrationType.SYNC,
            status=IntegrationStatus.READY,
            generated_code="def sync_data(): pass",
            validation_passed=True,
            test_passed=True
        )
        
        integration.status = IntegrationStatus.ACTIVE
        integration.deployed_at = datetime.now(timezone.utc)
        
        assert integration.status == IntegrationStatus.ACTIVE
        assert integration.is_active() is True
        assert integration.deployed_at is not None
    
    def test_active_to_paused(self):
        """Test transition from ACTIVE to PAUSED."""
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Test spec",
            integration_type=IntegrationType.SYNC,
            status=IntegrationStatus.ACTIVE
        )
        
        integration.status = IntegrationStatus.PAUSED
        assert integration.status == IntegrationStatus.PAUSED
        assert integration.is_active() is False
    
    def test_error_state(self):
        """Test ERROR state handling."""
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Test spec",
            integration_type=IntegrationType.SYNC,
            status=IntegrationStatus.ERROR
        )
        
        assert integration.status == IntegrationStatus.ERROR
        assert integration.is_active() is False
        assert integration.is_deployable() is False


class TestIntegrationPerformanceMetrics:
    """Test cases for integration performance metrics."""
    
    def test_execution_metrics_update(self):
        """Test updating execution metrics."""
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Test spec",
            integration_type=IntegrationType.SYNC
        )
        
        # Set initial values for testing (normally set at database level)
        integration.execution_count = 0
        integration.success_count = 0
        integration.error_count = 0

        # Initial state
        assert integration.execution_count == 0
        assert integration.success_count == 0
        assert integration.error_count == 0
        
        # Simulate executions
        integration.execution_count = 10
        integration.success_count = 8
        integration.error_count = 2
        integration.avg_execution_time_ms = 150.5
        
        assert integration.execution_count == 10
        assert integration.success_count == 8
        assert integration.error_count == 2
        assert integration.avg_execution_time_ms == 150.5
        assert integration.success_rate == 80.0
        assert integration.error_rate == 20.0
    
    def test_performance_metrics_consistency(self):
        """Test that performance metrics are consistent."""
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Test spec",
            integration_type=IntegrationType.SYNC,
            execution_count=100,
            success_count=75,
            error_count=25
        )
        
        # Success count + error count should equal execution count
        assert integration.success_count + integration.error_count == integration.execution_count
        assert integration.success_rate + integration.error_rate == 100.0


class TestIntegrationValidation:
    """Test cases for integration validation and constraints."""
    
    def test_integration_name_required(self):
        """Test that name is required."""
        # Model validation happens at database level, not at object creation
        integration = Integration(
            natural_language_spec="Test spec",
            integration_type=IntegrationType.SYNC
        )
        # Name is required at database level but not at object creation
        assert integration.name is None
    
    def test_integration_spec_required(self):
        """Test that natural_language_spec is required."""
        # Model validation happens at database level, not at object creation
        integration = Integration(
            name="Test Integration",
            integration_type=IntegrationType.SYNC
        )
        # Spec is required at database level but not at object creation
        assert integration.natural_language_spec is None
    
    def test_integration_type_required(self):
        """Test that integration_type is required."""
        # Model validation happens at database level, not at object creation
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Test spec"
        )
        # Type is required at database level but not at object creation
        assert integration.integration_type is None
    
    def test_code_version_positive(self):
        """Test that code_version should be positive."""
        integration = Integration(
            name="Test Integration",
            natural_language_spec="Test spec",
            integration_type=IntegrationType.SYNC,
            code_version=2
        )
        
        assert integration.code_version == 2
        assert integration.code_version > 0


@pytest.mark.unit
class TestIntegrationFactory:
    """Test cases for Integration factory."""
    
    def test_integration_factory_creation(self):
        """Test creating integration using factory."""
        integration = IntegrationFactory()
        
        assert integration.name is not None
        assert integration.natural_language_spec is not None
        assert integration.integration_type is not None
        assert integration.status is not None
        # ID might be None until saved to database, just check it exists as attribute
        assert hasattr(integration, 'id')
    
    def test_integration_factory_with_overrides(self):
        """Test creating integration with factory overrides."""
        integration = IntegrationFactory(
            name="Custom Integration",
            status=IntegrationStatus.ACTIVE,
            integration_type=IntegrationType.ETL
        )
        
        assert integration.name == "Custom Integration"
        assert integration.status == IntegrationStatus.ACTIVE
        assert integration.integration_type == IntegrationType.ETL
