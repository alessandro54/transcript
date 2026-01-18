"""Command-line interface for the Audio Transcription Bot."""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

from .bot import main as run_bot

# Load environment variables
load_dotenv()


@click.group()
@click.version_option(version="1.0.0", prog_name="transcription-bot")
def cli():
    """🎙️ Audio Transcription Bot CLI

    A Telegram bot that transcribes voice messages using Whisper.
    """
    pass


@cli.command()
@click.option(
    "--env",
    type=click.Choice(["development", "production"], case_sensitive=False),
    help="Override environment setting"
)
@click.option(
    "--token",
    type=str,
    help="Override Telegram bot token"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Set logging level"
)
@click.option(
    "--check",
    is_flag=True,
    help="Check configuration without starting the bot"
)
def run(env: Optional[str], token: Optional[str], log_level: str, check: bool):
    """Run the transcription bot."""

    # Override environment if specified
    if env:
        os.environ["ENVIRONMENT"] = env.lower()

    # Override token if specified
    if token:
        os.environ["TELEGRAM_BOT_TOKEN"] = token

    # Set log level
    import logging
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))

    # Check configuration
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if not bot_token:
        click.echo("❌ TELEGRAM_BOT_TOKEN is not set!", err=True)
        click.echo("Set it in your .env file or use --token option", err=True)
        sys.exit(1)

    if environment == "production":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            click.echo("⚠️  WARNING: OPENAI_API_KEY is not set for production mode!", err=True)
            click.echo("The bot will not work without it.", err=True)

    if check:
        click.echo("✅ Configuration check passed!")
        click.echo(f"   Environment: {environment}")
        click.echo(f"   Log Level: {log_level}")
        click.echo(f"   Bot Token: {'✓ Set' if bot_token else '✗ Missing'}")
        if environment == "production":
            api_key = os.getenv("OPENAI_API_KEY")
            click.echo(f"   OpenAI API Key: {'✓ Set' if api_key else '✗ Missing'}")
        return

    click.echo(f"🚀 Starting transcription bot in {environment} mode...")
    click.echo(f"📊 Log level: {log_level}")

    try:
        run_bot()
    except KeyboardInterrupt:
        click.echo("\n👋 Bot stopped by user")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def config():
    """Show current configuration."""

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    environment = os.getenv("ENVIRONMENT", "development")
    api_key = os.getenv("OPENAI_API_KEY")
    whisper_model = os.getenv("WHISPER_MODEL", "base")
    whisper_device = os.getenv("WHISPER_DEVICE", "auto")

    click.echo("📋 Current Configuration:")
    click.echo(f"   Environment: {environment}")
    click.echo(f"   Bot Token: {'✓ Set' if bot_token else '✗ Missing'}")
    click.echo(f"   OpenAI API Key: {'✓ Set' if api_key else '✗ Missing'}")
    click.echo(f"   Whisper Model: {whisper_model}")
    click.echo(f"   Whisper Device: {whisper_device}")

    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        click.echo(f"\n📁 .env file: ✓ Found at {env_file.absolute()}")
    else:
        click.echo(f"\n📁 .env file: ✗ Not found (copy from .env.example)")


@cli.command()
def init():
    """Initialize a new .env file from template."""

    env_example = Path(".env.example")
    env_file = Path(".env")

    if env_file.exists():
        if not click.confirm("⚠️  .env file already exists. Overwrite?"):
            click.echo("Aborted.")
            return

    if not env_example.exists():
        click.echo("❌ .env.example file not found!", err=True)
        sys.exit(1)

    # Copy the example file
    content = env_example.read_text()
    env_file.write_text(content)

    click.echo("✅ Created .env file from template")
    click.echo("📝 Please edit .env with your configuration")


if __name__ == "__main__":
    cli()
