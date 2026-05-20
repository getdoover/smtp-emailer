from pydoover.docker import run_app

from .application import SmtpEmailerApplication

def main():
    """Run the application."""
    run_app(SmtpEmailerApplication())
