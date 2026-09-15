# Send email from Doover

SMTP Emailer turns a channel message into a real email. Publish a small JSON message — recipients, a subject and a body — to a watched channel, and this processor builds the email and delivers it through your own SMTP account. Your apps get alerts, reports and notifications into inboxes without any of them carrying mail code or credentials.

It runs in the Doover cloud, so there is nothing to install on a Doovit and nothing to build. It has no device page of its own: it works entirely off the channel it listens to, and reports what it did through its tags.

---

<p align="left">
  <img src="https://raw.githubusercontent.com/getdoover/smtp-emailer/main/assets/app-types/app-type-cloud-monochrome.png?v=27dc0b69626d" alt="App Type: Cloud — Processes in the cloud" align="left" width="180" height="180">
  <img src="https://raw.githubusercontent.com/getdoover/smtp-emailer/main/assets/app-types/ui-backend-monochrome.png?v=a3e66ef41381" alt="UI: Backend — Does not have a User Interface" align="left" width="180" height="180">
</p>
<br clear="all">

---

- **Send on a channel message.** Each new message published to a watched channel, carrying the fields below, becomes one email.
- **Plain text or HTML.** Set `"html": true` in the message to send the body as HTML.
- **Several recipients, plus CC.** `to` and `cc` each take a single address or a list of addresses.
- **File attachments.** Carry files base64-encoded inside the message and they arrive as normal email attachments.
- **Your own mail account.** It submits through any SMTP server that accepts an authenticated login — your provider's mail server or one you run yourself.
- **One sender identity, set once.** Configure the From address and display name in the app, not in every message.

## What you need

- **An SMTP account you can log in to** — hostname, port, username and password. The app authenticates on every send, so an open relay that accepts unauthenticated mail will not work. If your provider issues app-specific passwords, or leaves SMTP authentication switched off on a mailbox until you enable it, sort that out on the mail account first.
- **A mail account you are happy to dedicate to this.** The username and password are entered as ordinary configuration fields on the install, so use a service mailbox or an app-specific password rather than a person's everyday credentials.
- **A submission port that takes a plain connection, optionally upgraded with STARTTLS** — port 587 on most providers. Point it at a port that expects TLS from the first byte (implicit TLS, usually 465) and the connection never completes; it hangs until the app's 30-second timeout and the send is recorded as an error.
- **A device to install it against.** The install listens on that device's channel. A device app can only write to its own device's channels, so install it on any device whose own apps send mail; cloud processors, widgets and API callers name the target device explicitly, so a single install can serve all of them. Install it more than once when you want separate sender identities or SMTP accounts.
- **Something to publish the request** — another app, processor, widget or API caller writing a JSON message to the watched channel.

## Set it up

1. **Add SMTP Emailer** to the device that needs to send mail.
2. **Enter the server details.** **SMTP Host** — your provider's submission hostname — **SMTP Port** (587 by default) and your **SMTP Username** and **SMTP Password**.
3. **Leave Use STARTTLS on** for a submission port such as 587. Turn it off only for a server that accepts unencrypted SMTP on the configured port; the app still logs in either way, so the credentials would go over the wire in the clear.
4. **Set the sender.** **From Address** is the address mail is sent from. **From Name** is an optional display name shown beside it.
5. **Check the channel.** **Subscription** is pre-filled with `send-email`. Change it, or add more entries, if you would rather listen on a differently named channel, or on several.

Save the configuration and the processor is live. The next message on the watched channel goes out as email.

## The message to publish

| Field | Type | Required | Description |
|---|---|---|---|
| `to` | string or list of strings | Yes | Recipient address or addresses |
| `subject` | string | No | Subject line; defaults to `(no subject)` |
| `body` | string | No | The email body, plain text or HTML |
| `html` | boolean | No | `true` sends `body` as HTML |
| `cc` | string or list of strings | No | CC address or addresses |
| `attachments` | list of objects | No | Files to attach, described below |

A message whose data is empty is ignored, so publish the whole object in one message rather than building it up over several.

```json
{
  "to": ["alice@example.com", "bob@example.com"],
  "cc": "manager@example.com",
  "subject": "Monthly sensor report",
  "html": true,
  "body": "<h1>Report</h1><p>See attached.</p>"
}
```

### Attachments

Each entry in `attachments` takes a `filename`, the file's base64-encoded bytes in `content`, and its `mime_type`. Leave any of them out and you get `attachment`, an empty file and `application/octet-stream` respectively, so set all three.

```json
"attachments": [
  {
    "filename": "report.pdf",
    "content": "JVBERi0xLjQK...",
    "mime_type": "application/pdf"
  }
]
```

The encoded file travels inside the channel message, so keep attachments to modest documents — reports, CSVs, small images — rather than large media.

## Sending from your apps

From a device app on the same device, write to the channel directly:

```python
await self.create_message(
    "send-email",
    {
        "to": ["ops@example.com", "admin@example.com"],
        "subject": "Device offline",
        "body": "<p>Pump <b>pump-03</b> has gone offline.</p>",
        "html": True,
    },
)
```

From a cloud processor or integration, name the device whose install should send the mail:

```python
await self.api.create_message(
    "send-email",
    {
        "to": "recipient@example.com",
        "subject": "Sensor alert",
        "body": "Temperature exceeded threshold.",
    },
    agent_id=agent_id,
)
```

From a widget, publish to the same channel on the device's agent:

```javascript
import { useSendMessage } from "doover-js/react";

const sendEmail = useSendMessage({ agentId, channelName: "send-email" });

sendEmail.mutate({
  to: "user@example.com",
  subject: "Manual report request",
  body: "A user requested the weekly report.",
});
```

## Checking that mail went out

After each attempt the processor records the result as tags:

| Tag | Meaning |
|---|---|
| `send_count` | Running count of emails sent successfully |
| `last_send_status` | `success` or `error` for the most recent attempt |
| `last_send_time` | When that attempt happened, as an ISO 8601 timestamp |
| `last_error` | The error text from the most recent failure; cleared when a send succeeds |

These are written to the `tag_values` channel on the device the app is installed against, under the install's app key, so you can read them from the channel view or the API.

A failed send is recorded and not retried, and nothing is raised back to the platform — so when an expected email does not arrive, read `last_send_status` and `last_error` to find out why. If `last_send_time` has not moved at all, the trigger message never reached the watched channel in a usable shape; check the channel name and that the message carried data.
