from api.auth.roles import Role, ALL_ROLES, DEFAULT_ROLE


def test_all_roles_match_expected_values():
    expected = {"admin", "qa_lead", "validator", "viewer"}
    assert ALL_ROLES == expected
    assert {role.value for role in Role} == expected


def test_default_role_is_viewer():
    assert DEFAULT_ROLE is Role.VIEWER
