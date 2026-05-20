import base64
import logging
import smtplib
from datetime import datetime, timezone
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from email import encoders

from pydoover.processor import Application
from pydoover.models import MessageCreateEvent

from .app_config import SmtpEmailerConfig

log = logging.getLogger(__name__)


class SmtpEmailerApplication(Application):
    config_cls = SmtpEmailerConfig
    config: SmtpEmailerConfig

    async def setup(self):
        """Called once per invocation before event processing."""
        pass

    async def close(self):
        """Called once per invocation after event processing."""
        pass

    async def on_message_create(self, event: MessageCreateEvent):
        """Handle incoming email send requests."""
        log.info("on_message_create triggered, channel: %s", event.channel.name)
        data = event.message.data
        log.info("Message data: %s", data)

        if not data:
            log.warning("Received message with no data, skipping")
            return

        try:
            log.info("Building MIME message...")
            msg = self._build_message(data)
            log.info("Sending via SMTP to %s...", data.get("to"))
            self._send_message(msg, data)

            send_count = self.get_tag("send_count", 0)
            await self.set_tag("send_count", send_count + 1)
            await self.set_tag("last_send_status", "success")
            await self.set_tag("last_send_time", datetime.now(timezone.utc).isoformat())
            await self.set_tag("last_error", None)

            log.info("Email sent successfully to %s", data.get("to"))

        except Exception as e:
            log.error("Failed to send email: %s", e, exc_info=True)
            await self.set_tag("last_send_status", "error")
            await self.set_tag("last_send_time", datetime.now(timezone.utc).isoformat())
            await self.set_tag("last_error", str(e))

    def _build_message(self, data: dict) -> MIMEMultipart:
        """Construct the MIME email message from the channel data."""
        msg = MIMEMultipart()

        # From
        from_name = self.config.from_name.value or ""
        from_address = self.config.from_address.value
        if from_name:
            msg["From"] = formataddr((from_name, from_address))
        else:
            msg["From"] = from_address

        # To
        to = data.get("to", [])
        if isinstance(to, str):
            to = [to]
        msg["To"] = ", ".join(to)

        # CC
        cc = data.get("cc")
        if cc:
            if isinstance(cc, str):
                cc = [cc]
            msg["Cc"] = ", ".join(cc)

        # Subject
        msg["Subject"] = data.get("subject", "(no subject)")

        # Body
        body = data.get("body", "")
        is_html = data.get("html", False)
        if is_html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        # Attachments
        attachments = data.get("attachments", [])
        for attachment in attachments:
            filename = attachment.get("filename", "attachment")
            content_b64 = attachment.get("content", "")
            mime_type = attachment.get("mime_type", "application/octet-stream")

            maintype, _, subtype = mime_type.partition("/")
            part = MIMEBase(maintype, subtype or "octet-stream")
            part.set_payload(base64.b64decode(content_b64))
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                "attachment",
                filename=filename,
            )
            msg.attach(part)

        return msg

    def _send_message(self, msg: MIMEMultipart, data: dict):
        """Connect to SMTP and send the email."""
        host = self.config.smtp_host.value
        port = self.config.smtp_port.value
        username = self.config.smtp_username.value
        password = self.config.smtp_password.value
        use_tls = self.config.use_starttls.value

        # Build recipient list
        to = data.get("to", [])
        if isinstance(to, str):
            to = [to]
        cc = data.get("cc", [])
        if isinstance(cc, str):
            cc = [cc]
        recipients = to + cc

        server = smtplib.SMTP(host, port, timeout=30)
        try:
            if use_tls:
                server.starttls()
            server.login(username, password)
            server.sendmail(
                self.config.from_address.value,
                recipients,
                msg.as_string(),
            )
        finally:
            server.quit()
