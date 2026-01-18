# 🎙️ Audio Transcription Bot

A Telegram bot that transcribes voice messages and audio files using OpenAI's Whisper API or local Whisper model.

## Features

- 🎤 Transcribe voice messages and audio files
- 🌍 Multi-language support (Spanish & English)
- ⏱️ 2-minute duration limit
- 🔄 Retry button for failed transcriptions
- 🔇 Noise reduction for better accuracy
- 📱 Support for multiple formats (MP3, WAV, OGG, OPUS, M4A, AAC, FLAC)
- 🎛️ Development/Production mode switching

## Commands

- `/start` - Show welcome message and bot info
- `/setlang` - Change transcription language
- `/command` - Show all available commands

## Setup

### Requirements

- Python 3.13.6 or higher

### Option 1: Install from Source

#### 1. Clone the repository

```bash
git clone <repository-url>
cd transcript
```

#### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 3. Install the package

```bash
pip install -e .
```

#### 4. Configure environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
ENVIRONMENT=development  # or production
OPENAI_API_KEY=your_openai_key_here  # Only for production
```

#### 5. Run the bot

```bash
# Start the bot with CLI
transcription-bot run

# Or with options
transcription-bot run --env production --log-level DEBUG

# Check configuration first
transcription-bot run --check
```

### CLI Commands

The bot includes a powerful command-line interface:

```bash
# Run the bot
transcription-bot run [OPTIONS]

Options:
  --env [development|production]  Override environment
  --token TEXT                    Override bot token
  --log-level [DEBUG|INFO|WARNING|ERROR]  Set log level
  --check                         Check config only, don't start

# Show current configuration
transcription-bot config

# Initialize .env file from template
transcription-bot init

# Show help
transcription-bot --help
```

### Option 2: Development Installation

```bash
# Clone and install in development mode
git clone <repository-url>
cd transcript
pip install -e .

# Run directly
python -m transcript_bot.bot
```

### Option 3: Traditional Installation

```bash
# Clone and install dependencies
git clone <repository-url>
cd transcript
pip install -r requirements.txt

# Run the bot
python transcript_bot/bot.py
```

## Configuration

### Development Mode (Free)

- Uses local Whisper model
- No API costs
- Requires model download
- Set `ENVIRONMENT=development`

### Production Mode (Paid)

- Uses OpenAI Whisper API
- $0.006 per minute
- Best accuracy (large-v3)
- Set `ENVIRONMENT=production`

## Supported Formats

- Voice messages (OGG)
- MP3, WAV, OGG, OPUS, M4A, AAC, FLAC
- Video notes (circular videos)

## Project Structure

```text
transcript/
├── transcript_bot/          # Main package
│   ├── __init__.py         # Package initialization
│   ├── bot.py              # Main bot entry point
│   ├── handlers.py         # Message handlers
│   ├── callbacks.py        # Callback handlers
│   ├── language_callbacks.py # Language selection handlers
│   ├── utils.py           # Utility functions
│   ├── transcriber.py     # Transcription module
│   ├── transcriber_local.py # Local Whisper
│   └── transcriber_openai.py # OpenAI Whisper
├── setup.py               # Package setup script
├── MANIFEST.in            # Package manifest
├── requirements.txt       # Dependencies
├── .env.example          # Example configuration
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## Usage

1. Send the bot a voice message or audio file
2. The bot transcribes it in your preferred language
3. If transcription fails, use the retry button
4. Change language with `/setlang`

## Tips for Better Accuracy

- Speak clearly and close to the mic
- Use voice messages when possible
- Avoid background noise
- Keep audio under 2 minutes

## License

MIT License
