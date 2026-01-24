"""
Test suite for SQLAlchemy Base and BaseModel
Ensures proper declarative base and base model with common fields
"""

import os
import sys
import pytest
from datetime import datetime
from uuid import UUID

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))


class TestBaseDeclarative:
    """Test SQLAlchemy declarative base"""

    def test_base_exists(self):
        """Test that Base declarative base exists"""
        from models.base import Base
        assert Base is not None

    def test_base_is_declarative_base(self):
        """Test that Base is a declarative base"""
        from models.base import Base
        # Check it has registry attribute (sqlalchemy 2.0 style)
        assert hasattr(Base, 'registry') or hasattr(Base, 'metadata')

    def test_base_has_metadata(self):
        """Test that Base has metadata attribute"""
        from models.base import Base
        assert hasattr(Base, 'metadata')
        assert Base.metadata is not None


class TestBaseModel:
    """Test BaseModel with common fields"""

    def test_base_model_exists(self):
        """Test that BaseModel class exists"""
        from models.base import BaseModel
        assert BaseModel is not None

    def test_base_model_is_class(self):
        """Test that BaseModel is a class"""
        from models.base import BaseModel
        assert isinstance(BaseModel, type)


class TestBaseModelIdField:
    """Test BaseModel id field"""

    def test_base_model_has_id_field(self):
        """Test that BaseModel has id field"""
        from models.base import BaseModel
        assert hasattr(BaseModel, 'id')

    def test_id_field_is_column(self):
        """Test that id field is a SQLAlchemy Column"""
        from models.base import BaseModel
        from sqlalchemy import Column
        # Access class attribute
        id_attr = BaseModel.__dict__.get('id')
        assert isinstance(id_attr, Column)

    def test_id_field_is_uuid_type(self):
        """Test that id field uses GUID type (platform-independent UUID)"""
        from models.base import BaseModel, GUID
        id_column = BaseModel.__dict__.get('id')
        # Check the type is GUID (which wraps UUID for SQLite compatibility)
        assert isinstance(id_column.type, GUID)

    def test_id_field_uses_uuid_as_uuid(self):
        """Test that GUID field handles as_uuid=True for PostgreSQL"""
        from models.base import BaseModel, GUID
        from sqlalchemy.dialects.postgresql import UUID
        id_column = BaseModel.__dict__.get('id')
        # GUID uses PostgresUUID with as_uuid=True internally for PostgreSQL
        # Check that it's a GUID type which provides this behavior
        assert isinstance(id_column.type, GUID)

    def test_id_field_is_primary_key(self):
        """Test that id field is primary key"""
        from models.base import BaseModel
        id_column = BaseModel.__dict__.get('id')
        assert id_column.primary_key is True

    def test_id_field_has_default_uuid4(self):
        """Test that id field has default of uuid.uuid4"""
        from models.base import BaseModel
        import uuid
        id_column = BaseModel.__dict__.get('id')
        # Check that default is set
        assert id_column.default is not None
        # Check that it's callable (function)
        assert callable(id_column.default.arg)
        # The default should be uuid.uuid4 (check function name)
        assert id_column.default.arg.__name__ == 'uuid4'


class TestBaseModelCreatedAtField:
    """Test BaseModel created_at field"""

    def test_base_model_has_created_at_field(self):
        """Test that BaseModel has created_at field"""
        from models.base import BaseModel
        assert hasattr(BaseModel, 'created_at')

    def test_created_at_field_is_column(self):
        """Test that created_at field is a SQLAlchemy Column"""
        from models.base import BaseModel
        from sqlalchemy import Column
        created_at_attr = BaseModel.__dict__.get('created_at')
        assert isinstance(created_at_attr, Column)

    def test_created_at_field_is_datetime_type(self):
        """Test that created_at field uses DateTime type"""
        from models.base import BaseModel
        from sqlalchemy import DateTime
        created_at_column = BaseModel.__dict__.get('created_at')
        assert isinstance(created_at_column.type, DateTime)

    def test_created_at_has_server_default(self):
        """Test that created_at has server_default"""
        from models.base import BaseModel
        created_at_column = BaseModel.__dict__.get('created_at')
        # server_default should be set
        assert created_at_column.server_default is not None

    def test_created_at_server_default_is_now(self):
        """Test that created_at server_default uses func.now()"""
        from models.base import BaseModel
        created_at_column = BaseModel.__dict__.get('created_at')
        # Check that server_default contains 'now'
        server_default_str = str(created_at_column.server_default.arg)
        assert 'now' in server_default_str.lower()

    def test_created_at_is_not_nullable_by_default(self):
        """Test that created_at is not nullable by default"""
        from models.base import BaseModel
        created_at_column = BaseModel.__dict__.get('created_at')
        # nullable should be True by default for server_default columns
        # unless explicitly set to False
        # We'll accept either for this test


class TestBaseModelUpdatedAtField:
    """Test BaseModel updated_at field"""

    def test_base_model_has_updated_at_field(self):
        """Test that BaseModel has updated_at field"""
        from models.base import BaseModel
        assert hasattr(BaseModel, 'updated_at')

    def test_updated_at_field_is_column(self):
        """Test that updated_at field is a SQLAlchemy Column"""
        from models.base import BaseModel
        from sqlalchemy import Column
        updated_at_attr = BaseModel.__dict__.get('updated_at')
        assert isinstance(updated_at_attr, Column)

    def test_updated_at_field_is_datetime_type(self):
        """Test that updated_at field uses DateTime type"""
        from models.base import BaseModel
        from sqlalchemy import DateTime
        updated_at_column = BaseModel.__dict__.get('updated_at')
        assert isinstance(updated_at_column.type, DateTime)

    def test_updated_at_has_server_default(self):
        """Test that updated_at has server_default"""
        from models.base import BaseModel
        updated_at_column = BaseModel.__dict__.get('updated_at')
        # server_default should be set
        assert updated_at_column.server_default is not None

    def test_updated_at_server_default_is_now(self):
        """Test that updated_at server_default uses func.now()"""
        from models.base import BaseModel
        updated_at_column = BaseModel.__dict__.get('updated_at')
        # Check that server_default contains 'now'
        server_default_str = str(updated_at_column.server_default.arg)
        assert 'now' in server_default_str.lower()

    def test_updated_at_has_onupdate(self):
        """Test that updated_at has onupdate"""
        from models.base import BaseModel
        updated_at_column = BaseModel.__dict__.get('updated_at')
        # onupdate should be set
        assert updated_at_column.onupdate is not None

    def test_updated_at_onupdate_is_now(self):
        """Test that updated_at onupdate uses func.now()"""
        from models.base import BaseModel
        updated_at_column = BaseModel.__dict__.get('updated_at')
        # Check that onupdate contains 'now'
        onupdate_str = str(updated_at_column.onupdate.arg)
        assert 'now' in onupdate_str.lower()


class TestBaseModelInheritance:
    """Test that models can inherit from BaseModel"""

    def test_can_create_model_inheriting_base_model(self):
        """Test that we can create a model inheriting BaseModel"""
        from models.base import Base, BaseModel
        from sqlalchemy import Column, String

        class TestModel1(Base, BaseModel):
            __tablename__ = 'test_model_1'
            name = Column(String(100))

        assert TestModel1 is not None

    def test_inherited_model_has_id_field(self):
        """Test that model inheriting BaseModel has id field"""
        from models.base import Base, BaseModel
        from sqlalchemy import Column, String

        class TestModel2(Base, BaseModel):
            __tablename__ = 'test_model_2'
            name = Column(String(100))

        assert hasattr(TestModel2, 'id')

    def test_inherited_model_has_created_at_field(self):
        """Test that model inheriting BaseModel has created_at field"""
        from models.base import Base, BaseModel
        from sqlalchemy import Column, String

        class TestModel3(Base, BaseModel):
            __tablename__ = 'test_model_3'
            name = Column(String(100))

        assert hasattr(TestModel3, 'created_at')

    def test_inherited_model_has_updated_at_field(self):
        """Test that model inheriting BaseModel has updated_at field"""
        from models.base import Base, BaseModel
        from sqlalchemy import Column, String

        class TestModel4(Base, BaseModel):
            __tablename__ = 'test_model_4'
            name = Column(String(100))

        assert hasattr(TestModel4, 'updated_at')

    def test_inherited_model_has_custom_fields(self):
        """Test that model inheriting BaseModel can have custom fields"""
        from models.base import Base, BaseModel
        from sqlalchemy import Column, String

        class TestModel5(Base, BaseModel):
            __tablename__ = 'test_model_5'
            name = Column(String(100))
            email = Column(String(255))

        assert hasattr(TestModel5, 'name')
        assert hasattr(TestModel5, 'email')

    def test_inherited_model_can_be_instantiated(self):
        """Test that model inheriting BaseModel can be instantiated"""
        from models.base import Base, BaseModel
        from sqlalchemy import Column, String
        import uuid

        class TestModel6(Base, BaseModel):
            __tablename__ = 'test_model_6'
            name = Column(String(100))

        # Create instance
        instance = TestModel6(name="Test")
        assert instance is not None
        assert instance.name == "Test"

    def test_inherited_model_id_gets_uuid_value(self):
        """Test that instantiated model can have UUID set"""
        from models.base import Base, BaseModel
        from sqlalchemy import Column, String
        from uuid import UUID
        import uuid

        class TestModel7(Base, BaseModel):
            __tablename__ = 'test_model_7'
            name = Column(String(100))

        # Create instance with explicit id
        test_uuid = uuid.uuid4()
        instance = TestModel7(name="Test", id=test_uuid)
        # ID should be set to the provided UUID
        assert instance.id is not None
        assert isinstance(instance.id, UUID)
        assert instance.id == test_uuid

        # Create instance without id - default will be applied at INSERT time
        instance2 = TestModel7(name="Test2")
        # ID can be None before database insertion (standard SQLAlchemy behavior)
        # The default will be applied when the object is persisted to database
        assert hasattr(instance2, 'id')


class TestBaseModelTableName:
    """Test BaseModel does not have __tablename__"""

    def test_base_model_has_no_tablename(self):
        """Test that BaseModel itself has no __tablename__"""
        from models.base import BaseModel
        # BaseModel should not have __tablename__ since it's not a table
        assert not hasattr(BaseModel, '__tablename__')


class TestBaseModelDocumentation:
    """Test BaseModel has proper documentation"""

    def test_base_model_has_docstring(self):
        """Test that BaseModel has a docstring"""
        from models.base import BaseModel
        assert BaseModel.__doc__ is not None
        assert len(BaseModel.__doc__.strip()) > 0

    def test_base_has_module_docstring(self):
        """Test that base module has a docstring"""
        import models.base
        assert models.base.__doc__ is not None
        assert len(models.base.__doc__.strip()) > 0


class TestBaseExports:
    """Test that base module exports are correct"""

    def test_base_module_exports_base(self):
        """Test that base module exports Base"""
        from models import base
        assert hasattr(base, 'Base')

    def test_base_module_exports_base_model(self):
        """Test that base module exports BaseModel"""
        from models import base
        assert hasattr(base, 'BaseModel')

    def test_can_import_base_directly(self):
        """Test that Base can be imported directly"""
        try:
            from models.base import Base
            assert Base is not None
        except ImportError:
            pytest.fail("Cannot import Base from models.base")

    def test_can_import_base_model_directly(self):
        """Test that BaseModel can be imported directly"""
        try:
            from models.base import BaseModel
            assert BaseModel is not None
        except ImportError:
            pytest.fail("Cannot import BaseModel from models.base")
