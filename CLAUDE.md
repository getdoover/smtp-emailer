# SMTP Emailer

A Doover processor application that sends emails via SMTP when a message is published to a subscribed channel.

## Commands

```bash
uv run pytest tests -v          # Run tests
uv run export-config             # Write config_schema into doover_config.json
./build.sh                       # Build Lambda deployment package (package.zip)
```

## Project Structure

```
src/smtp_emailer/
  __init__.py        # Lambda handler entry point — handler(event, context)
  application.py     # Main app class (setup, close, on_message_create)
  app_config.py      # Config schema — class-level declarations
build.sh             # Build script for Lambda deployment zip
tests/               # pytest suite
```

## pydoover Processor Patterns

This app uses the pydoover processor (serverless/Lambda) pattern:

### Handler Entry Point (__init__.py)
- Exports `handler(event, context)` for Lambda
- Calls `run_app(SmtpEmailerApplication(), event, context)` from `pydoover.processor`
- Must call `SmtpEmailerConfig.clear_elements()` before each invocation

### Application class (application.py)
- Inherits from `pydoover.processor.Application`
- Set `config_cls` as class attribute — framework wires it up automatically
- Override `async def setup()` for init, `async def close()` for cleanup
- Override `async def on_message_create(event)` to handle channel messages
- Access config via `self.config.<field>.value`
- Tags: `self.get_tag(key, default)` (sync), `await self.set_tag(key, value)` (async)

### Config (app_config.py)
- Subclass `config.Schema` with class-level `config.Boolean`, `config.String`, etc.
- Include `ManySubscriptionConfig()` from `pydoover.processor` for channel subscriptions
- `export()` calls `SmtpEmailerConfig.export(path, name)` (classmethod)

## Doover Skills

If you have the doover-skills plugin installed, use `/doover` to see all available skills.
Key skills: `/doover-cloud-apps` for processor/integration development, `/pydoover` for API reference.
