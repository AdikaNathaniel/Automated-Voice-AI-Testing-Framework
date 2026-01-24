"""
Centralized role definitions for RBAC.

Endpoint Role Requirements
==========================

This module defines the roles used throughout the application and documents
the access requirements for each API endpoint.

Role Capabilities
-----------------

SUPER_ADMIN:
    - Platform-level administrator
    - Can create and manage organizations
    - Access to admin console only
    - Cannot access individual organization data directly

ORG_ADMIN:
    - Organization-level administrator
    - Full access to all endpoints within their organization
    - Can create, update, delete all resources in their organization
    - Can manage organization settings and configurations
    - Can access resources across the entire organization

QA_LEAD:
    - Can create, update, delete test resources
    - Can manage test runs, test cases, test suites
    - Can assign defects and manage workflows
    - Can access resources across the entire tenant

VALIDATOR:
    - Can claim and submit validation tasks
    - Can release validation tasks
    - Read-only access to most resources
    - Limited to human_validation endpoints for mutations

VIEWER:
    - Read-only access to all resources
    - Cannot create, update, or delete anything
    - Can view test_runs, test_cases, test_suites, defects, etc.

Endpoint Role Matrix
--------------------

test_runs Endpoints:
    - POST /test-runs (create): org_admin, qa_lead
    - GET /test-runs (list): any authenticated user
    - GET /test-runs/{id} (get): any authenticated user
    - PUT /test-runs/{id}/cancel: org_admin, qa_lead
    - POST /test-runs/{id}/retry: org_admin, qa_lead
    - GET /test-runs/{id}/executions: any authenticated user

test_cases Endpoints:
    - POST /test-cases (create): org_admin, qa_lead
    - GET /test-cases (list): any authenticated user
    - GET /test-cases/{id} (get): any authenticated user
    - PUT /test-cases/{id} (update): org_admin, qa_lead
    - DELETE /test-cases/{id} (delete): org_admin, qa_lead
    - POST /test-cases/{id}/duplicate: org_admin, qa_lead
    - GET /test-cases/{id}/history: any authenticated user
    - GET /test-cases/{id}/versions: any authenticated user
    - POST /test-cases/{id}/versions/{n}/rollback: org_admin, qa_lead

test_suites Endpoints:
    - POST /test-suites (create): org_admin, qa_lead
    - GET /test-suites (list): any authenticated user
    - GET /test-suites/{id} (get): any authenticated user
    - PUT /test-suites/{id} (update): org_admin, qa_lead
    - DELETE /test-suites/{id} (delete): org_admin, qa_lead

defects Endpoints:
    - POST /defects (create): org_admin, qa_lead
    - GET /defects (list): any authenticated user
    - GET /defects/{id} (get): any authenticated user
    - PATCH /defects/{id} (update): org_admin, qa_lead
    - POST /defects/{id}/assign: org_admin, qa_lead
    - POST /defects/{id}/resolve: org_admin, qa_lead

scenarios Endpoints:
    - POST /scenarios (create): org_admin, qa_lead
    - GET /scenarios (list): any authenticated user
    - GET /scenarios/{id} (get): any authenticated user
    - PUT /scenarios/{id} (update): org_admin, qa_lead
    - DELETE /scenarios/{id} (delete): org_admin, qa_lead
    - POST /scenarios/{id}/execute: org_admin, qa_lead

edge_cases Endpoints:
    - POST /edge-cases (create): org_admin, qa_lead
    - GET /edge-cases (list): any authenticated user
    - GET /edge-cases/{id} (get): any authenticated user
    - PUT /edge-cases/{id} (update): org_admin, qa_lead
    - POST /edge-cases/{id}/categorize: org_admin, qa_lead
    - DELETE /edge-cases/{id} (delete): org_admin, qa_lead

human_validation Endpoints:
    - GET /human-validation/tasks (list): any authenticated user
    - POST /human-validation/tasks/{id}/claim: org_org_admin, qa_lead, validator
    - POST /human-validation/tasks/{id}/submit: org_org_admin, qa_lead, validator
    - POST /human-validation/tasks/{id}/release: org_org_admin, qa_lead, validator

knowledge_base Endpoints:
    - POST /knowledge-base (create): org_admin, qa_lead
    - GET /knowledge-base (list): any authenticated user
    - GET /knowledge-base/{id} (get): any authenticated user
    - PUT /knowledge-base/{id} (update): org_admin, qa_lead
    - DELETE /knowledge-base/{id} (delete): org_admin, qa_lead

configurations Endpoints:
    - POST /configurations (create): org_admin, qa_lead
    - GET /configurations (list): any authenticated user
    - GET /configurations/{id} (get): any authenticated user
    - PUT /configurations/{id} (update): org_admin, qa_lead
    - DELETE /configurations/{id} (delete): org_admin, qa_lead

regressions Endpoints:
    - GET /regressions (list): any authenticated user
    - POST /regressions/{id}/baseline: org_admin, qa_lead
    - GET /regressions/{id}/comparison: any authenticated user
"""

from __future__ import annotations

from enum import Enum
from typing import FrozenSet


class Role(str, Enum):
    """Supported roles for the pilot deployment."""

    SUPER_ADMIN = "super_admin"  # Can create/manage organizations
    ORG_ADMIN = "org_admin"  # Organization-level admin
    QA_LEAD = "qa_lead"
    VALIDATOR = "validator"
    VIEWER = "viewer"


ALL_ROLES: FrozenSet[str] = frozenset(role.value for role in Role)
"""Convenience set of all role values."""


DEFAULT_ROLE: Role = Role.VIEWER
"""Default role assigned to new accounts when none is specified."""
