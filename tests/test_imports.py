"""Smoke tests for the template application.

These validate that modules are importable, the config schema is well-formed,
the Tags/UI classes subclass the correct bases, and the config export entry
point runs end-to-end.
"""

import json

from pydoover.config import Schema
from pydoover.tags import Tags
from pydoover.ui import UI


def test_import_app():
    from smtp_emailer.application import SmtpEmailerApplication
    assert SmtpEmailerApplication.config_cls is not None
    assert SmtpEmailerApplication.tags_cls is not None
    assert SmtpEmailerApplication.ui_cls is not None


def test_config_schema():
    from smtp_emailer.app_config import SmtpEmailerConfig
    assert issubclass(SmtpEmailerConfig, Schema)

    schema = SmtpEmailerConfig.to_schema()
    assert isinstance(schema, dict)
    assert schema["type"] == "object"
    assert len(schema["properties"]) > 0
    assert "a_funny_message" in schema["required"]
    assert "simulator_app_key" in schema["required"]


def test_tags():
    from smtp_emailer.app_tags import SampleTags
    assert issubclass(SampleTags, Tags)


def test_ui():
    from smtp_emailer.app_ui import SmtpEmailerUI
    assert issubclass(SmtpEmailerUI, UI)


def test_state_machine():
    from smtp_emailer.app_state import SmtpEmailerState
    state = SmtpEmailerState()
    assert state.state == "off"


def test_config_export(tmp_path):
    from smtp_emailer.app_config import SmtpEmailerConfig

    fp = tmp_path / "doover_config.json"
    SmtpEmailerConfig.export(fp, "smtp_emailer")

    data = json.loads(fp.read_text())
    assert "smtp_emailer" in data
    assert "config_schema" in data["smtp_emailer"]
    assert "properties" in data["smtp_emailer"]["config_schema"]


def test_ui_export(tmp_path):
    from smtp_emailer.app_ui import SmtpEmailerUI

    fp = tmp_path / "doover_config.json"
    SmtpEmailerUI(None, None, None).export(fp, "smtp_emailer")

    data = json.loads(fp.read_text())
    assert "ui_schema" in data["smtp_emailer"]
    assert data["smtp_emailer"]["ui_schema"]["type"] == "uiApplication"
    assert "is_working" in data["smtp_emailer"]["ui_schema"]["children"]
