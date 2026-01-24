"""
Jira integration package.

Provides thin async client wrappers around Jira's REST API for use across the
application. Public exports surface the Jira client and associated exception
types.
"""

from .client import JiraClient, JiraClientError

__all__ = ["JiraClient", "JiraClientError"]
