"""Setup script for Audio Transcription Bot."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="audio-transcription-bot",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Telegram bot for audio transcription using Whisper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/audio-transcription-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "Topic :: Communications :: Chat",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    python_requires=">=3.13.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "transcription-bot=transcript_bot.core.cli:cli",
            "transcript-bot=transcript_bot.core.bot:main",
        ],
    },
    include_package_data=True,
    package_data={
        "transcript_bot": ["**/*.py", "i18n/translations/*.json"],
    },
)
