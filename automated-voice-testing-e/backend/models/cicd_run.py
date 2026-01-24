"""
CI/CD Run Model

Stores CI/CD pipeline run records triggered by webhooks from
GitHub, GitLab, Jenkins, etc.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
import enum

from models.base import Base


class CICDRunStatus(str, enum.Enum):
    """CI/CD run status enum."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class CICDProvider(str, enum.Enum):
    """CI/CD provider enum."""
    GITHUB = "github"
    GITLAB = "gitlab"
    JENKINS = "jenkins"


class CICDRun(Base):
    """
    CI/CD pipeline run record.

    Attributes:
        id: Unique identifier
        tenant_id: Organization tenant ID for multi-tenancy
        provider: CI/CD provider (github, gitlab, jenkins)
        pipeline_name: Name of the pipeline/workflow
        status: Current run status
        branch: Git branch name
        commit_sha: Git commit SHA
        commit_url: URL to commit on provider
        triggered_by: User/event that triggered the run
        started_at: When the run started
        completed_at: When the run completed (if finished)
        total_tests: Total number of tests
        passed_tests: Number of passed tests
        failed_tests: Number of failed tests
        raw_payload: Original webhook payload (JSON)
        event_type: Webhook event type (e.g., push, workflow_run)
    """

    __tablename__ = "cicd_runs"

    id = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    tenant_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    provider = Column(
        String(50),
        nullable=False,
        index=True,
    )
    pipeline_name = Column(
        String(255),
        nullable=False,
    )
    status = Column(
        String(50),
        nullable=False,
        default=CICDRunStatus.PENDING.value,
        index=True,
    )
    branch = Column(
        String(255),
        nullable=True,
    )
    commit_sha = Column(
        String(40),
        nullable=True,
    )
    commit_url = Column(
        String(500),
        nullable=True,
    )
    triggered_by = Column(
        String(255),
        nullable=True,
    )
    started_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    total_tests = Column(
        Integer,
        default=0,
    )
    passed_tests = Column(
        Integer,
        default=0,
    )
    failed_tests = Column(
        Integer,
        default=0,
    )
    raw_payload = Column(
        Text,
        nullable=True,
    )
    event_type = Column(
        String(100),
        nullable=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationship to tenant (organization owner)
    tenant = relationship("User", foreign_keys=[tenant_id])

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "id": str(self.id),
            "pipelineName": self.pipeline_name,
            "status": self.status,
            "branch": self.branch or "",
            "commitSha": self.commit_sha or "",
            "commitUrl": self.commit_url or "",
            "triggeredBy": self.triggered_by or "",
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "totalTests": self.total_tests,
            "passedTests": self.passed_tests,
            "failedTests": self.failed_tests,
            "provider": self.provider,
            "eventType": self.event_type,
        }

    def __repr__(self) -> str:
        return f"<CICDRun {self.id} {self.provider}/{self.pipeline_name} [{self.status}]>"
