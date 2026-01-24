"""
Edge case template configuration tests.

Ensures `backend/config/edge_case_templates.yaml` defines a well-structured
set of templates that downstream services can rely on for pre-populating
edge case records.
"""

from pathlib import Path
from typing import Dict, Iterable, Mapping

import yaml


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "edge_case_templates.yaml"

REQUIRED_TEMPLATE_IDS = {
    "timeout-external-service-latency": {
        "category": "timeout",
        "severity": "high",
        "default_tags": {"timeout", "external-service"},
    },
    "ambiguity-slot-resolution": {
        "category": "ambiguity",
        "severity": "medium",
        "default_tags": {"ambiguity", "nlp"},
    },
    "context-loss-long-dialogue": {
        "category": "context_loss",
        "severity": "high",
        "default_tags": {"context-loss", "conversation"},
    },
}

REQUIRED_KEYS = {
    "id",
    "title",
    "description",
    "category",
    "severity",
    "default_tags",
    "signals",
    "playbook",
    "sample_scenario",
}


def _assert_tags_include(actual: Iterable[str], expected: Iterable[str]) -> None:
    actual_set = {tag.strip().lower() for tag in actual}
    expected_set = {tag.strip().lower() for tag in expected}
    missing = expected_set - actual_set
    assert not missing, f"Expected tags {sorted(missing)} to be present; got {sorted(actual_set)}"


def test_edge_case_templates_config_structure() -> None:
    """The edge case template configuration must exist and expose required structure."""
    assert CONFIG_PATH.exists(), "edge_case_templates.yaml should exist under backend/config"

    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        data: Mapping[str, object] = yaml.safe_load(handle)

    assert isinstance(data, Mapping), "Configuration should load into a mapping/dict"
    assert "templates" in data, "Configuration must expose a 'templates' key"

    templates = data["templates"]
    assert isinstance(templates, list), "'templates' should be defined as a list"
    assert templates, "'templates' list should not be empty"

    by_id: Dict[str, Mapping[str, object]] = {}
    for template in templates:
        assert isinstance(template, Mapping), "Each template must be a mapping/dict"
        assert REQUIRED_KEYS.issubset(template.keys()), f"Template keys missing in {template.get('id')}"

        template_id = template["id"]
        assert template_id not in by_id, f"Duplicate template id detected: {template_id}"
        by_id[template_id] = template

        assert isinstance(template["default_tags"], list) and template["default_tags"], (
            f"default_tags must be a non-empty list for template {template_id}"
        )
        assert isinstance(template["signals"], list) and template["signals"], (
            f"signals must be a non-empty list for template {template_id}"
        )

        playbook = template["playbook"]
        assert isinstance(playbook, Mapping), f"playbook must be a mapping for template {template_id}"
        assert isinstance(playbook.get("owner"), str) and playbook["owner"], (
            f"playbook.owner must be a non-empty string for template {template_id}"
        )
        steps = playbook.get("steps")
        assert isinstance(steps, list) and steps, f"playbook.steps must be a non-empty list for {template_id}"
        assert all(isinstance(step, str) and step for step in steps), (
            f"playbook.steps must only contain non-empty strings for {template_id}"
        )

        sample = template["sample_scenario"]
        assert isinstance(sample, Mapping), f"sample_scenario must be a mapping for template {template_id}"
        assert isinstance(sample.get("context"), str) and sample["context"], (
            f"sample_scenario.context must be a non-empty string for {template_id}"
        )
        transcript = sample.get("transcript")
        assert isinstance(transcript, list) and transcript, (
            f"sample_scenario.transcript must be a non-empty list for {template_id}"
        )
        for turn in transcript:
            assert isinstance(turn, Mapping), (
                f"Each sample_scenario transcript entry must be a mapping for {template_id}"
            )
            assert {"user", "assistant"}.issubset(turn.keys()), (
                f"Transcript entries must include 'user' and 'assistant' keys for {template_id}"
            )

    # Ensure required templates exist with expected metadata
    for template_id, expectations in REQUIRED_TEMPLATE_IDS.items():
        assert template_id in by_id, f"Missing required template id '{template_id}'"
        template = by_id[template_id]
        for field, expected_value in expectations.items():
            if field == "default_tags":
                _assert_tags_include(template[field], expected_value)
            else:
                assert template[field] == expected_value, (
                    f"{template_id} field '{field}' expected '{expected_value}' "
                    f"but got '{template[field]}'"
                )
