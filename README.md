# SMTP Emailer

<img src="https://uxwing.com/wp-content/themes/uxwing/download/domain-hosting/smtp-server-icon.svg" alt="App Icon" style="max-width: 100px;">

**Sends emails via SMTP when a message is published to a subscribed channel. Supports recipient, subject, body, cc, and attachment fields.**

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/getdoover/smtp-emailer)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/getdoover/smtp-emailer/blob/main/LICENSE)

[Getting Started](#getting-started) | [Configuration](#configuration) | [Developer](https://github.com/getdoover/smtp-emailer/blob/main/DEVELOPMENT.md) | [Need Help?](#need-help)

<br/>

## Overview

SMTP Emailer is a Doover processor that enables any agent or application on the Doover platform to send emails by simply publishing a message to a channel. It bridges the gap between your IoT devices, automation workflows, and traditional email communication -- allowing alerts, reports, and notifications to reach inboxes without any custom email infrastructure.

The processor listens on one or more configurable channel subscriptions. When a new message arrives containing recipient addresses, a subject, and a body, the processor constructs a properly formatted MIME email and delivers it through any standard SMTP server. HTML content, CC recipients, and binary file attachments (base64-encoded) are all supported out of the box.

Because it runs as a serverless Lambda function on the Doover platform, there is no infrastructure to manage. Configure your SMTP credentials, point a channel subscription at it, and any agent or device in your deployment can send email.

### Features

- Send plain-text or HTML emails via any SMTP server
- Support for multiple recipients (To and CC fields)
- Binary file attachments via base64-encoded payloads
- Configurable STARTTLS encryption for secure connections
- Customisable sender display name and address
- Status tracking via tags (send count, last status, last error)
- Subscribe to one or more channels for flexible routing

<br/>

## Getting Started

### Prerequisites

1. An SMTP server with valid credentials (e.g., Gmail, Amazon SES, SendGrid, Mailgun, or your own mail server)
2. A Doover deployment with at least one agent
3. A channel that other apps or agents will publish email requests to

### Installation

Add the **SMTP Emailer** processor to your Doover deployment through the Doover platform UI or CLI. The processor is available as a public app (`smtp_emailer`).

### Quick Start

1. Add the SMTP Emailer processor to your deployment
2. Configure the SMTP connection settings (host, port, username, password)
3. Set the sender address and optional display name
4. Add one or more channel subscriptions to listen on
5. Publish a message to the subscribed channel with the following structure:

```json
{
  "to": "recipient@example.com",
  "subject": "Hello from Doover",
  "body": "This is a test email sent via the SMTP Emailer processor."
}
```

<br/>

## Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| **Subscription** | A list of channels to subscribe to. Each entry is the name of a channel to listen on for email send requests. | *Required* |
| **SMTP Host** | SMTP server hostname (e.g., `smtp.gmail.com`, `email-smtp.us-east-1.amazonaws.com`) | *Required* |
| **SMTP Port** | SMTP server port | `587` |
| **SMTP Username** | SMTP authentication username | *Required* |
| **SMTP Password** | SMTP authentication password | *Required* |
| **Use STARTTLS** | Use STARTTLS for the connection. Set to `true` for port 587, `false` for port 465 (implicit TLS) or port 25 (unencrypted). | `true` |
| **From Address** | Sender email address used in the From field | *Required* |
| **From Name** | Sender display name shown alongside the From address | `""` (empty) |

### Example Configuration

```json
{
  "dv_proc_subscriptions": ["send-email"],
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "myapp@gmail.com",
  "smtp_password": "app-specific-password",
  "use_starttls": true,
  "from_address": "myapp@gmail.com",
  "from_name": "My Doover App"
}
```

<br/>

## Message Payload

Messages published to the subscribed channel should follow this schema:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| **to** | `string` or `string[]` | Yes | Recipient email address(es) |
| **subject** | `string` | No | Email subject line (defaults to "(no subject)") |
| **body** | `string` | No | Email body content (plain text or HTML) |
| **html** | `boolean` | No | Set to `true` if the body contains HTML content |
| **cc** | `string` or `string[]` | No | CC recipient email address(es) |
| **attachments** | `object[]` | No | List of file attachments (see below) |

### Attachment Format

Each attachment object must contain:

| Field | Type | Description |
|-------|------|-------------|
| **filename** | `string` | The file name to display (e.g., `report.pdf`) |
| **content** | `string` | Base64-encoded file content |
| **mime_type** | `string` | MIME type (e.g., `application/pdf`, `image/png`) |

### Full Message Example

```json
{
  "to": ["alice@example.com", "bob@example.com"],
  "subject": "Monthly Sensor Report",
  "body": "<h1>Report</h1><p>See attached.</p>",
  "html": true,
  "cc": "manager@example.com",
  "attachments": [
    {
      "filename": "report.pdf",
      "content": "JVBERi0xLjQK...",
      "mime_type": "application/pdf"
    }
  ]
}
```

<br/>

## Tags

This processor exposes the following status tags:

| Tag | Description |
|-----|-------------|
| **send_count** | Running count of successfully sent emails (integer) |
| **last_send_status** | Status of the most recent send attempt: `"success"` or `"error"` |
| **last_send_time** | ISO 8601 timestamp of the most recent send attempt |
| **last_error** | Error message from the most recent failure, or `null` on success |

<br/>

## Sending Emails from Other Apps

Any Doover app can send an email by publishing a message to the channel that this processor is subscribed to (e.g. `send-email`).

### From a Processor or Integration (Python)

```python
await self.api.publish_message(
    agent_id,
    "send-email",
    {
        "to": "recipient@example.com",
        "subject": "Sensor Alert",
        "body": "Temperature exceeded threshold.",
    }
)
```

### From a Device App (Python)

```python
await self.create_message(
    "send-email",
    {
        "to": ["ops@example.com", "admin@example.com"],
        "subject": "Device Offline",
        "body": "<p>Device <b>pump-03</b> has gone offline.</p>",
        "html": True,
    }
)
```

### From a Widget (JavaScript)

```javascript
const { sendMessage } = useDoover();

sendMessage(
  { agentId, channelName: "send-email" },
  {
    to: "user@example.com",
    subject: "Manual Report Request",
    body: "A user requested the weekly report.",
  }
);
```

### With Attachments

```python
import base64
from pathlib import Path

pdf_content = base64.b64encode(Path("report.pdf").read_bytes()).decode()

await self.api.publish_message(
    agent_id,
    "send-email",
    {
        "to": "manager@example.com",
        "subject": "Monthly Report",
        "body": "<h1>Report Attached</h1>",
        "html": True,
        "attachments": [
            {
                "filename": "report.pdf",
                "content": pdf_content,
                "mime_type": "application/pdf",
            }
        ],
    }
)
```

<br/>

## How It Works

1. **Trigger**: The processor is invoked when a new message is published to any of its subscribed channels.
2. **Parse**: The `on_message_create` handler extracts the message data containing recipient, subject, body, and optional CC/attachment fields.
3. **Build**: A MIME multipart email is constructed with the configured sender address/name, the provided recipients, subject, and body (plain text or HTML). Any base64-encoded attachments are decoded and added as MIME parts.
4. **Send**: The processor connects to the configured SMTP server, optionally upgrades to TLS via STARTTLS, authenticates, and sends the email to all recipients (To + CC).
5. **Track**: On success, the `send_count` tag is incremented and `last_send_status` is set to `"success"`. On failure, the error is captured in `last_error` and `last_send_status` is set to `"error"`. The `last_send_time` tag is updated in both cases.

<br/>

## Integrations

This processor works with:

- **Any SMTP server** -- Gmail, Amazon SES, SendGrid, Mailgun, Microsoft 365, or self-hosted mail servers
- **Doover agents and device apps** -- any app that can publish a message to a channel can trigger an email
- **Doover automation workflows** -- chain this processor with other processors for alert pipelines, report generation, and notification systems

<br/>

## Need Help?

- Email: support@doover.com
- [Doover Documentation](https://docs.doover.com)
- [App Developer Documentation](https://github.com/getdoover/smtp-emailer/blob/main/DEVELOPMENT.md)

<br/>

## Version History

### v0.1.0 (Current)
- Initial release
- Send plain-text and HTML emails via SMTP
- Support for To and CC recipients
- Base64-encoded file attachments
- STARTTLS encryption support
- Status tracking via tags (send_count, last_send_status, last_send_time, last_error)
- Configurable channel subscriptions via ManySubscriptionConfig

<br/>

## License

This app is licensed under the [Apache License 2.0](https://github.com/getdoover/smtp-emailer/blob/main/LICENSE).
