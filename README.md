# Audio Transcription Bot

Telegram bot that transcribes voice messages and audio files using Whisper.

## Features

- Transcribe voice messages and audio files
- Auto-summarization for audio over 3 minutes
- Multi-language support (Spanish, English)
- Export transcriptions as text files

## Quick Start

1. Configure environment
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials
```env
TELEGRAM_BOT_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here
ENVIRONMENT=development
```

3. Run the bot
```bash
docker compose --profile dev up -d
```

4. Check logs
```bash
docker compose --profile dev logs -f
```

## Configuration

Create a `.env` file with the following variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from @BotFather |
| `OPENAI_API_KEY` | Yes | OpenAI API key for transcription and summarization |
| `ENVIRONMENT` | No | `production` (OpenAI API) or `development` (local Whisper). Default: `development` |
| `WHISPER_MODEL` | No | Local model size: `tiny`, `base`, `small`, `medium`, `large-v3`. Default: `base` |
| `WHISPER_DEVICE` | No | Device for local model: `cpu`, `cuda`, `auto`. Default: `cpu` |

## Commands

- `/start` - Welcome message
- `/command` - Show all available commands
- `/setlang` - Change language
- `/history` - View transcription history

## Deployment

See [DEPLOY.md](DEPLOY.md) for VM deployment guide.

## License

MIT
