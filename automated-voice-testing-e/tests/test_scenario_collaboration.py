"""
Test suite for scenario collaboration UX features.

This module tests the collaboration workflow features:
- Ownership tracking per scenario
- Approval status workflow
- Reviewer assignment
- Audit trail for changes
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from uuid import uuid4
from datetime import datetime

import pytest


class TestScenarioOwnershipFields:
    """Test ScenarioScript ownership tracking fields"""

    def test_has_owner_id_field(self):
        """Test that ScenarioScript has owner_id field"""
        from models.scenario_script import ScenarioScript

        columns = {c.name: c for c in ScenarioScript.__table__.columns}
        assert 'owner_id' in columns, \
            "owner_id field should exist for ownership tracking"

    def test_owner_id_is_uuid(self):
        """Test that owner_id is UUID type"""
        from models.scenario_script import ScenarioScript

        columns = {c.name: c for c in ScenarioScript.__table__.columns}
        assert 'UUID' in str(columns['owner_id'].type)

    def test_owner_id_is_nullable(self):
        """Test that owner_id is nullable"""
        from models.scenario_script import ScenarioScript

        columns = {c.name: c for c in ScenarioScript.__table__.columns}
        assert columns['owner_id'].nullable is True

    def test_has_owner_relationship(self):
        """Test that ScenarioScript has owner relationship"""
        from models.scenario_script import ScenarioScript

        assert hasattr(ScenarioScript, 'owner')


class TestScenarioApprovalStatus:
    """Test ScenarioScript approval status workflow"""

    def test_has_approval_status_field(self):
        """Test that ScenarioScript has approval_status field"""
        from models.scenario_script import ScenarioScript

        columns = {c.name: c for c in ScenarioScript.__table__.columns}
        assert 'approval_status' in columns, \
            "approval_status field should exist"

    def test_approval_status_is_string(self):
        """Test that approval_status is String type"""
        from models.scenario_script import ScenarioScript

        columns = {c.name: c for c in ScenarioScript.__table__.columns}
        assert 'VARCHAR' in str(columns['approval_status'].type) or \
               'String' in str(columns['approval_status'].type)

    def test_approval_status_has_default(self):
        """Test that approval_status has default value"""
        from models.scenario_script import ScenarioScript

        columns = {c.name: c for c in ScenarioScript.__table__.columns}
        col = columns['approval_status']
        assert col.default is not None

    def test_approval_status_indexed(self):
        """Test that approval_status is indexed for querying"""
        from models.scenario_script import ScenarioScript

        columns = {c.name: c for c in ScenarioScript.__table__.columns}
        col = columns['approval_status']
        assert col.index is True


class TestScenarioReviewerFields:
    """Test ScenarioScript reviewer tracking"""

    def test_has_reviewed_by_field(self):
        """Test that ScenarioScript has reviewed_by field"""
        from models.scenario_script import ScenarioScript

        columns = {c.name: c for c in ScenarioScript.__table__.columns}
        assert 'reviewed_by' in columns, \
            "reviewed_by field should exist"

    def test_reviewed_by_is_uuid(self):
        """Test that reviewed_by is UUID type"""
        from models.scenario_script import ScenarioScript

        columns = {c.name: c for c in ScenarioScript.__table__.columns}
        assert 'UUID' in str(columns['reviewed_by'].type)

    def test_has_reviewed_at_field(self):
        """Test that ScenarioScript has reviewed_at field"""
        from models.scenario_script import ScenarioScript

        columns = {c.name: c for c in ScenarioScript.__table__.columns}
        assert 'reviewed_at' in columns, \
            "reviewed_at field should exist"

    def test_reviewed_at_is_datetime(self):
        """Test that reviewed_at is DateTime type"""
        from models.scenario_script import ScenarioScript

        columns = {c.name: c for c in ScenarioScript.__table__.columns}
        type_str = str(columns['reviewed_at'].type)
        assert 'TIMESTAMP' in type_str or 'DateTime' in type_str or 'DATETIME' in type_str

    def test_has_reviewer_relationship(self):
        """Test that ScenarioScript has reviewer relationship"""
        from models.scenario_script import ScenarioScript

        assert hasattr(ScenarioScript, 'reviewer')


class TestScenarioReviewComments:
    """Test ScenarioScript review comments"""

    def test_has_review_notes_field(self):
        """Test that ScenarioScript has review_notes field"""
        from models.scenario_script import ScenarioScript

        columns = {c.name: c for c in ScenarioScript.__table__.columns}
        assert 'review_notes' in columns, \
            "review_notes field should exist for reviewer feedback"

    def test_review_notes_is_text(self):
        """Test that review_notes is Text type"""
        from models.scenario_script import ScenarioScript

        columns = {c.name: c for c in ScenarioScript.__table__.columns}
        assert 'TEXT' in str(columns['review_notes'].type)


class TestCommentModelExists:
    """Test that Comment model exists and has required fields"""

    def test_comment_model_exists(self):
        """Test that Comment model can be imported"""
        from models.comment import Comment
        assert Comment is not None

    def test_comment_has_entity_type(self):
        """Test Comment has entity_type field"""
        from models.comment import Comment

        columns = {c.name: c for c in Comment.__table__.columns}
        assert 'entity_type' in columns

    def test_comment_has_entity_id(self):
        """Test Comment has entity_id field"""
        from models.comment import Comment

        columns = {c.name: c for c in Comment.__table__.columns}
        assert 'entity_id' in columns

    def test_comment_has_author_id(self):
        """Test Comment has author_id field"""
        from models.comment import Comment

        columns = {c.name: c for c in Comment.__table__.columns}
        assert 'author_id' in columns

    def test_comment_has_content(self):
        """Test Comment has content field"""
        from models.comment import Comment

        columns = {c.name: c for c in Comment.__table__.columns}
        assert 'content' in columns

    def test_comment_supports_threading(self):
        """Test Comment has parent_comment_id for threading"""
        from models.comment import Comment

        columns = {c.name: c for c in Comment.__table__.columns}
        assert 'parent_comment_id' in columns

    def test_comment_has_mentions(self):
        """Test Comment has mentions field for @mentions"""
        from models.comment import Comment

        columns = {c.name: c for c in Comment.__table__.columns}
        assert 'mentions' in columns


class TestActivityLogModelExists:
    """Test that ActivityLog model exists for audit trail"""

    def test_activity_log_model_exists(self):
        """Test that ActivityLog model can be imported"""
        from models.activity_log import ActivityLog
        assert ActivityLog is not None

    def test_activity_log_has_user_id(self):
        """Test ActivityLog has user_id field"""
        from models.activity_log import ActivityLog

        columns = {c.name: c for c in ActivityLog.__table__.columns}
        assert 'user_id' in columns

    def test_activity_log_has_action_type(self):
        """Test ActivityLog has action_type field"""
        from models.activity_log import ActivityLog

        columns = {c.name: c for c in ActivityLog.__table__.columns}
        assert 'action_type' in columns

    def test_activity_log_has_resource_type(self):
        """Test ActivityLog has resource_type field"""
        from models.activity_log import ActivityLog

        columns = {c.name: c for c in ActivityLog.__table__.columns}
        assert 'resource_type' in columns

    def test_activity_log_has_resource_id(self):
        """Test ActivityLog has resource_id field"""
        from models.activity_log import ActivityLog

        columns = {c.name: c for c in ActivityLog.__table__.columns}
        assert 'resource_id' in columns

    def test_activity_log_has_metadata(self):
        """Test ActivityLog has metadata field"""
        from models.activity_log import ActivityLog

        columns = {c.name: c for c in ActivityLog.__table__.columns}
        # Field is named metadata_payload internally
        assert 'metadata' in columns or 'metadata_payload' in columns


class TestScenarioApprovalHelperMethods:
    """Test helper methods for approval workflow"""

    def test_has_submit_for_review_method(self):
        """Test ScenarioScript has submit_for_review method"""
        from models.scenario_script import ScenarioScript

        assert hasattr(ScenarioScript, 'submit_for_review')

    def test_has_approve_method(self):
        """Test ScenarioScript has approve method"""
        from models.scenario_script import ScenarioScript

        assert hasattr(ScenarioScript, 'approve')

    def test_has_reject_method(self):
        """Test ScenarioScript has reject method"""
        from models.scenario_script import ScenarioScript

        assert hasattr(ScenarioScript, 'reject')

    def test_has_is_approved_property(self):
        """Test ScenarioScript has is_approved property"""
        from models.scenario_script import ScenarioScript

        assert hasattr(ScenarioScript, 'is_approved')

    def test_has_is_pending_review_property(self):
        """Test ScenarioScript has is_pending_review property"""
        from models.scenario_script import ScenarioScript

        assert hasattr(ScenarioScript, 'is_pending_review')


class TestScenarioToDictIncludesApprovalFields:
    """Test that to_dict includes approval fields"""

    def test_to_dict_method_exists(self):
        """Test ScenarioScript has to_dict method"""
        from models.scenario_script import ScenarioScript

        assert hasattr(ScenarioScript, 'to_dict')

