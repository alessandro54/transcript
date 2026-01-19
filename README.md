# 🎙️ Audio Transcription Bot

A powerful Telegram bot that transcribes voice messages and audio files using OpenAI's Whisper API or local Whisper model, with intelligent summarization features.

## ✨ Features

- 🎤 **Transcribe voice messages and audio files** - Support for all major audio formats
- 🌍 **Multi-language support** - Spanish & English with more languages planned
- 📝 **Smart Summarization** - Automatic summaries for audio > 3 minutes
- 📄 **Export to Text File** - Download full transcriptions as .txt files
- 🔄 **Retry failed transcriptions** - One-click retry with file kept for 5 minutes
- 🔇 **Noise reduction** - Better accuracy with audio cleanup
- 📊 **Transcription History** - View past transcriptions with `/history`
- 🚦 **Processing Lock** - One transcription at a time to prevent overload
- 📱 **Multiple format support** - MP3, WAV, OGG, OPUS, M4A, AAC, FLAC, voice messages, video notes
- 🎛️ **Environment switching** - Development (local) or Production (OpenAI) modes

## 📋 Commands

- `/start` - Show welcome message and bot info
- `/setlang` - Change transcription language
- `/command` - Show all available commands
- `/history` - View your transcription history and statistics

## 🎯 Smart Features

### Intelligent Summarization

- **< 1 minute**: Just transcription
- **1-3 minutes**: Transcription with "📝 Summarize" button
- **3+ minutes**: Auto-generated summary + "📄 Full Transcript" button
- **10+ minutes**: Summary with downloadable text file

### Audio Duration Support

- **Maximum**: 30 minutes per audio file
- **Recommended**: < 10 minutes for best performance
- **Processing time**: Varies by model and device

## 🛠️ Setup

### Requirements

- Python 3.8 or higher
- Telegram Bot Token
- OpenAI API Key (for summarization and production mode)

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
# Environment
ENVIRONMENT=development  # or production

# Telegram Bot Token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# OpenAI API Key (for transcription and summarization)
OPENAI_API_KEY=your_openai_api_key_here

# Whisper Model (optional, defaults to base)
WHISPER_MODEL=large  # tiny, base, small, medium, large-v3

# Whisper Device (optional, defaults to auto)
WHISPER_DEVICE=cpu  # cpu, cuda, auto
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

## ⚙️ Configuration

### Development Mode (Free)

- Uses local Whisper model
- No transcription costs
- Requires model download (~300MB for base model)
- Slower processing (2-3 minutes for 10-min audio)
- Set `ENVIRONMENT=development`

### Production Mode (Paid)

- Uses OpenAI Whisper API
- $0.006 per minute of audio
- Best accuracy (large-v3 model)
- Fast processing (10-20 seconds for 10-min audio)
- Set `ENVIRONMENT=production`

### Whisper Models

| Model   | Size   | Speed   | Accuracy   | VRAM   |
|---------|--------|---------|------------|--------|
| tiny    | 39MB   | Fastest | Basic      | ~1GB   |
| base    | 74MB   | Fast    | Good       | ~1GB   |
| small   | 244MB  | Medium  | Better     | ~2GB   |
| medium  | 769MB  | Slow    | Very Good  | ~5GB   |
| large-v3| 1550MB | Slowest | Best       | ~10GB  |

## 📱 Supported Formats

- Voice messages (OGG/OPUS)
- MP3, WAV, OGG, OPUS, M4A, AAC, FLAC
- Video notes (circular videos, MP4)

## 🏗️ Project Structure

```text
transcript/
├── transcript_bot/              # Main package
│   ├── __init__.py             # Package initialization
│   ├── bot.py                  # Main bot entry point
│   ├── handlers.py             # Message handlers
│   ├── callbacks.py            # Callback handlers
│   ├── language_callbacks.py   # Language selection handlers
│   ├── summary_callbacks.py    # Summary & transcript handlers
│   ├── utils.py                # Utility functions
│   ├── transcriber.py          # Transcription module
│   ├── transcriber_local.py    # Local Whisper
│   ├── transcriber_openai.py   # OpenAI Whisper
│   ├── summarizer.py           # OpenAI summarization
│   ├── database.py             # SQLite database
│   └── logger.py               # Colored logging
├── setup.py                    # Package setup script
├── MANIFEST.in                 # Package manifest
├── requirements.txt            # Dependencies
├── .env.example               # Example configuration
├── .gitignore                 # Git ignore file
└── README.md                  # This file
```

## 📊 Database

The bot uses SQLite to store:

- Transcription history
- User language preferences
- Usage statistics

Database file: `bot.db` (created automatically)

## 💡 Usage Examples

### Basic Transcription

```text
User: Sends voice message
Bot: ⏳ Processing...
Bot: "Transcribed text here"
```

### With Summarization

```text
User: Sends 5-minute audio
Bot: ⏳ Processing...
Bot: 📝 Generating summary...
Bot:
📝 **Summary:**
• Discussed quarterly results
• Budget approved for Q4
• Next meeting Friday

[📄 Full Transcript]
```

### File Export

```text
User: Clicks "📄 Full Transcript"
Bot: Sends transcription.txt file
Bot: Button changes to [✅ Transcript Sent]
```

## 🎯 Tips for Best Results

### Audio Quality

- Speak clearly and close to the microphone
- Use voice messages when possible for best quality
- Avoid background noise or music
- Ensure good internet connection for voice messages

### Performance

- Use OpenAI in production for faster processing
- Choose appropriate model size for your hardware
- Break very long audio (>30 min) into segments
- Use CPU if you have limited GPU memory

### Summarization

- Summaries work best for structured content (meetings, lectures)
- English summaries tend to be more detailed
- Cost: ~$0.001 per summary with OpenAI GPT-3.5

## 🔧 Troubleshooting

### Common Issues

#### Bot doesn't respond

- Check `TELEGRAM_BOT_TOKEN` is correct
- Ensure bot is running and has internet access

#### Transcription fails

- Check audio format is supported
- Verify audio duration < 30 minutes
- Try the retry button

#### Summarization not working

- Verify `OPENAI_API_KEY` is set
- Check OpenAI API credits
- Ensure `ENVIRONMENT` is set correctly

#### Slow processing

- Switch to smaller Whisper model
- Use OpenAI in production mode
- Check CPU/GPU usage

### Logs

Enable debug logging:

```bash
transcription-bot run --log-level DEBUG
```

## 🚀 Deployment

### Free/Cheap Options

1. **Render.com** - Free tier with 512MB RAM
2. **Hetzner VPS** - €4.99/month, good performance
3. **Railway.app** - $5/month hobby plan
4. **Fly.io** - Free allowance, pay-per-use

### Production Tips

- Use PostgreSQL instead of SQLite for scaling
- Add Redis for caching transcripts
- Use webhook instead of polling for better performance
- Monitor OpenAI API usage and costs

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.
