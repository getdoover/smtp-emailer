from typing import Any

from pydoover.processor import run_app

from .application import SmtpEmailerApplication
from .app_config import SmtpEmailerConfig


def handler(event: dict[str, Any], context):
    """Lambda handler entry point."""
    SmtpEmailerConfig.clear_elements()
    run_app(
        SmtpEmailerApplication(),
        event,
        context,
    )
