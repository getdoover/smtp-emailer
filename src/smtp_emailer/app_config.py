from pathlib import Path

from pydoover import config
from pydoover.processor import ManySubscriptionConfig


class SmtpEmailerConfig(config.Schema):
    subscription = ManySubscriptionConfig(default=["send-email"])

    smtp_host = config.String(
        "SMTP Host",
        description="SMTP server hostname",
    )
    smtp_port = config.Integer(
        "SMTP Port",
        description="SMTP server port",
        default=587,
    )
    smtp_username = config.String(
        "SMTP Username",
        description="SMTP authentication username",
    )
    smtp_password = config.String(
        "SMTP Password",
        description="SMTP authentication password",
    )
    use_starttls = config.Boolean(
        "Use STARTTLS",
        description="Use STARTTLS for the connection",
        default=True,
    )
    from_address = config.String(
        "From Address",
        description="Sender email address (the From field)",
    )
    from_name = config.String(
        "From Name",
        description="Sender display name",
        default="",
    )


def export():
    """Export configuration schema to doover_config.json."""
    SmtpEmailerConfig.export(
        Path(__file__).parents[2] / "doover_config.json",
        "smtp_emailer",
    )


if __name__ == "__main__":
    export()
