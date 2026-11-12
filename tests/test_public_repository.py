"""T-SEC-AUDIT: exact synthetic exceptions cannot hide changed credentials."""

import json
import pytest

from scripts.validate_public_repository import line_digest, validate_files


def test_changed_secret_in_the_same_file_is_not_exempt(tmp_path):
    fixture = '"Authorization: ' + 'Bearer synthetic-fixture",'
    path = tmp_path / "fixture.py"
    path.write_text(fixture)
    allowed = {"fixture.py": {line_digest(fixture): ["authorization header"]}}
    assert validate_files(tmp_path, ["fixture.py"], allowed) == []
    path.write_text(fixture.replace("synthetic-fixture", "unexpected-value"))
    errors = validate_files(tmp_path, ["fixture.py"], allowed)
    assert errors == ["fixture.py:1: authorization header"]
    assert "unexpected-value" not in "".join(errors)


def test_unlisted_document_is_scanned_without_exposing_its_content(tmp_path):
    path = tmp_path / "new-notes.md"
    path.write_text("client_" + "secret=unpublished-value")
    assert validate_files(tmp_path, [path.name], {}) == ["new-notes.md:1: secret assignment"]


def test_private_reviewer_identifier_cannot_reenter_policy(tmp_path):
    path = tmp_path / "submission/reviewer-fixture.json"
    path.parent.mkdir()
    path.write_text(json.dumps({"project_id": 123}))
    assert validate_files(tmp_path, [path.relative_to(tmp_path).as_posix()], {}) == [
        "submission/reviewer-fixture.json: private reviewer identifiers are prohibited"
    ]


@pytest.mark.parametrize("encoding", ["utf-16", "utf-16-le", "utf-32"])
def test_recognized_text_in_unsupported_encoding_is_not_skipped(tmp_path, encoding):
    path = tmp_path / "notes.md"
    path.write_text("client_" + "secret=synthetic-value", encoding=encoding)
    errors = validate_files(tmp_path, [path.name], {})
    assert errors == ["notes.md: public text must use UTF-8 encoding"]
    assert "synthetic-value" not in "".join(errors)


def test_multiline_secret_is_checked_without_losing_exact_exceptions(tmp_path):
    fixture = '"Authorization: ' + 'Bearer synthetic-fixture",'
    path = tmp_path / "fixture.py"
    allowed = {path.name: {line_digest(fixture): ["authorization header"]}}
    path.write_text(fixture + "\nclient_" + "secret:\n  unpublished-value")
    assert validate_files(tmp_path, [path.name], allowed) == ["fixture.py: secret assignment"]


def test_nested_json_credentials_are_rejected_without_values(tmp_path):
    path = tmp_path / "credentials.json"
    path.write_text(json.dumps({"connection": [{"client_" + "secret": "unpublished-value"}]}))
    assert validate_files(tmp_path, [path.name], {}) == [
        "credentials.json: JSON credential value is prohibited"
    ]


def test_json_schema_and_empty_secret_values_remain_valid(tmp_path):
    path = tmp_path / "schema.json"
    path.write_text(json.dumps({"properties": {"password": {"type": "string"}}, "client_" + "secret": ""}))
    assert validate_files(tmp_path, [path.name], {}) == []
