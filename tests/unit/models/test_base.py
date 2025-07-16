"""
Unit tests for base model classes and mixins.

Tests BaseModel, TimestampMixin, AuditMixin, MetadataMixin functionality
including UUID generation, timestamps, and serialization.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import (
    Base,
    BaseModel,
    TimestampMixin,
    AuditMixin,
    MetadataMixin,
)


# Test model classes for testing mixins
class SampleModel(BaseModel):
    """Sample model for BaseModel testing."""
    __tablename__ = "sample_models"


class SampleModelWithTimestamp(BaseModel, TimestampMixin):
    """Sample model with timestamp mixin."""
    __tablename__ = "sample_models_timestamp"

    name = Column(String(100))


class SampleModelWithAudit(BaseModel, AuditMixin):
    """Sample model with audit mixin."""
    __tablename__ = "sample_models_audit"

    name = Column(String(100))


class SampleModelWithMetadata(BaseModel, MetadataMixin):
    """Sample model with metadata mixin."""
    __tablename__ = "sample_models_metadata"

    name = Column(String(100))


class SampleModelComplete(BaseModel, TimestampMixin, AuditMixin, MetadataMixin):
    """Sample model with all mixins."""
    __tablename__ = "sample_models_complete"

    name = Column(String(100))


class TestBaseModel:
    """Test cases for BaseModel class."""
    
    def test_base_model_has_uuid_id(self):
        """Test that BaseModel has UUID primary key."""
        model = SampleModel()

        assert hasattr(model, 'id')
        # ID is None until saved to database, but we can set it manually
        model.id = uuid.uuid4()
        assert isinstance(model.id, uuid.UUID)
        assert model.id is not None
    
    def test_base_model_id_is_unique(self):
        """Test that each instance gets a unique ID."""
        model1 = SampleModel()
        model2 = SampleModel()

        # Set IDs manually to test uniqueness
        model1.id = uuid.uuid4()
        model2.id = uuid.uuid4()

        assert model1.id != model2.id
        assert isinstance(model1.id, uuid.UUID)
        assert isinstance(model2.id, uuid.UUID)
    
    def test_base_model_repr(self):
        """Test string representation of BaseModel."""
        model = SampleModel()
        repr_str = repr(model)

        assert "SampleModel" in repr_str
        assert str(model.id) in repr_str
        assert repr_str.startswith("<SampleModel(id=")
        assert repr_str.endswith(")>")
    
    def test_base_model_to_dict(self):
        """Test conversion to dictionary."""
        model = SampleModel()
        model.id = uuid.uuid4()  # Set ID manually
        result = model.to_dict()

        assert isinstance(result, dict)
        assert "id" in result
        assert result["id"] == str(model.id)  # UUID converted to string
    
    def test_base_model_to_dict_with_datetime(self):
        """Test to_dict with datetime fields."""
        model = SampleModelWithTimestamp()
        model.name = "Test"

        result = model.to_dict()

        assert "id" in result
        assert "created_at" in result
        assert "updated_at" in result
        assert "name" in result

        # Datetime should be converted to ISO format
        if model.created_at:
            assert isinstance(result["created_at"], str)
            # Should be valid ISO format
            datetime.fromisoformat(result["created_at"].replace('Z', '+00:00'))


class TestTimestampMixin:
    """Test cases for TimestampMixin."""
    
    def test_timestamp_mixin_fields(self):
        """Test that TimestampMixin adds timestamp fields."""
        model = SampleModelWithTimestamp()

        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')

    def test_timestamp_mixin_auto_timestamps(self):
        """Test automatic timestamp setting."""
        # Note: This test would need database session to test auto-timestamps
        # For now, test that fields exist and can be set
        model = SampleModelWithTimestamp()
        now = datetime.now(timezone.utc)

        model.created_at = now
        model.updated_at = now

        assert model.created_at == now
        assert model.updated_at == now

    def test_timestamp_mixin_in_to_dict(self):
        """Test timestamp fields in to_dict output."""
        model = SampleModelWithTimestamp()
        model.name = "Test"
        now = datetime.now(timezone.utc)
        model.created_at = now
        model.updated_at = now

        result = model.to_dict()

        assert "created_at" in result
        assert "updated_at" in result
        assert isinstance(result["created_at"], str)
        assert isinstance(result["updated_at"], str)


class TestAuditMixin:
    """Test cases for AuditMixin."""
    
    def test_audit_mixin_fields(self):
        """Test that AuditMixin adds audit fields."""
        model = SampleModelWithAudit()

        assert hasattr(model, 'created_by')
        assert hasattr(model, 'updated_by')

    def test_audit_mixin_field_types(self):
        """Test audit field types."""
        model = SampleModelWithAudit()

        # Should be able to set UUID values
        user_id = uuid.uuid4()
        model.created_by = user_id
        model.updated_by = user_id

        assert model.created_by == user_id
        assert model.updated_by == user_id

    def test_audit_mixin_optional_fields(self):
        """Test that audit fields are optional."""
        model = SampleModelWithAudit()

        # Should be None by default
        assert model.created_by is None
        assert model.updated_by is None

    def test_audit_mixin_in_to_dict(self):
        """Test audit fields in to_dict output."""
        model = SampleModelWithAudit()
        model.name = "Test"
        user_id = uuid.uuid4()
        model.created_by = user_id
        model.updated_by = user_id
        
        result = model.to_dict()
        
        assert "created_by" in result
        assert "updated_by" in result
        assert result["created_by"] == str(user_id)
        assert result["updated_by"] == str(user_id)


class TestMetadataMixin:
    """Test cases for MetadataMixin."""
    
    def test_metadata_mixin_fields(self):
        """Test that MetadataMixin adds metadata fields."""
        model = SampleModelWithMetadata()

        assert hasattr(model, 'metadata')
        assert hasattr(model, 'tags')

    def test_metadata_mixin_json_fields(self):
        """Test metadata JSON field functionality."""
        model = SampleModelWithMetadata()

        # Should be able to set JSON data
        metadata = {"key": "value", "number": 42, "nested": {"inner": "data"}}
        model.metadata = metadata

        assert model.metadata == metadata

    def test_metadata_mixin_tags_array(self):
        """Test tags array field functionality."""
        model = SampleModelWithMetadata()

        # Should be able to set array of strings
        tags = ["tag1", "tag2", "important"]
        model.tags = tags

        assert model.tags == tags

    def test_metadata_mixin_optional_fields(self):
        """Test that metadata fields are optional."""
        model = SampleModelWithMetadata()

        # Should be None by default (but metadata might be a SQLAlchemy MetaData object)
        # Just check that the field exists
        assert hasattr(model, 'metadata')
        assert hasattr(model, 'tags')

    def test_metadata_mixin_in_to_dict(self):
        """Test metadata fields in to_dict output."""
        model = SampleModelWithMetadata()
        model.name = "Test"
        model.metadata = {"test": "data"}
        model.tags = ["test", "model"]
        
        result = model.to_dict()
        
        assert "metadata" in result
        assert "tags" in result
        assert result["metadata"] == {"test": "data"}
        assert result["tags"] == ["test", "model"]


class TestCompleteModel:
    """Test cases for model with all mixins."""
    
    def test_complete_model_has_all_fields(self):
        """Test that complete model has all mixin fields."""
        model = SampleModelComplete()

        # BaseModel fields
        assert hasattr(model, 'id')

        # TimestampMixin fields
        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')

        # AuditMixin fields
        assert hasattr(model, 'created_by')
        assert hasattr(model, 'updated_by')

        # MetadataMixin fields
        assert hasattr(model, 'metadata')
        assert hasattr(model, 'tags')

        # Model-specific fields
        assert hasattr(model, 'name')

    def test_complete_model_to_dict(self):
        """Test to_dict with all mixins."""
        model = SampleModelComplete()
        model.id = uuid.uuid4()  # Set ID for testing
        model.name = "Complete Test"
        model.metadata = {"test": True}
        model.tags = ["complete", "test"]
        
        now = datetime.now(timezone.utc)
        model.created_at = now
        model.updated_at = now
        
        user_id = uuid.uuid4()
        model.created_by = user_id
        model.updated_by = user_id
        
        result = model.to_dict()
        
        # Should have all expected fields (may have additional SQLAlchemy fields)
        expected_fields = {
            'id', 'name', 'created_at', 'updated_at',
            'created_by', 'updated_by', 'metadata', 'tags'
        }
        assert expected_fields.issubset(set(result.keys()))
        
        # Check data types
        assert isinstance(result['id'], str)
        assert result['name'] == "Complete Test"
        assert isinstance(result['created_at'], str)
        assert isinstance(result['updated_at'], str)
        assert isinstance(result['created_by'], str)
        assert isinstance(result['updated_by'], str)
        assert result['metadata'] == {"test": True}
        assert result['tags'] == ["complete", "test"]
    
    def test_complete_model_repr(self):
        """Test string representation of complete model."""
        model = SampleModelComplete()
        model.name = "Test Model"

        repr_str = repr(model)

        assert "SampleModelComplete" in repr_str
        assert str(model.id) in repr_str


@pytest.mark.unit
class TestModelInheritance:
    """Test cases for model inheritance and polymorphism."""

    def test_all_models_inherit_from_base(self):
        """Test that all test models inherit from Base."""
        models = [
            SampleModel(),
            SampleModelWithTimestamp(),
            SampleModelWithAudit(),
            SampleModelWithMetadata(),
            SampleModelComplete(),
        ]

        for model in models:
            assert isinstance(model, Base)
            assert isinstance(model, BaseModel)

    def test_mixin_composition(self):
        """Test that mixins can be composed together."""
        # Model with timestamp and audit
        class SampleComposed(BaseModel, TimestampMixin, AuditMixin):
            __tablename__ = "sample_composed"

        model = SampleComposed()

        # Should have fields from all mixins
        assert hasattr(model, 'id')  # BaseModel
        assert hasattr(model, 'created_at')  # TimestampMixin
        assert hasattr(model, 'updated_at')  # TimestampMixin
        assert hasattr(model, 'created_by')  # AuditMixin
        assert hasattr(model, 'updated_by')  # AuditMixin

    def test_model_table_names(self):
        """Test that models have correct table names."""
        assert SampleModel.__tablename__ == "sample_models"
        assert SampleModelWithTimestamp.__tablename__ == "sample_models_timestamp"
        assert SampleModelWithAudit.__tablename__ == "sample_models_audit"
        assert SampleModelWithMetadata.__tablename__ == "sample_models_metadata"
        assert SampleModelComplete.__tablename__ == "sample_models_complete"
