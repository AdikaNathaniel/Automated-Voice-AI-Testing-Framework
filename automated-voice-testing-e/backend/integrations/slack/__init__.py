"""Slack integration package."""

from .client import SlackClient, SlackClientError
from .bot import SlackBot

__all__ = ["SlackClient", "SlackClientError", "SlackBot"]
