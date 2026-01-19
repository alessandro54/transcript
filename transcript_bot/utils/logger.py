"""Enhanced logging module with colors and detailed user tracking."""

import logging
import sys
from datetime import datetime
from typing import Optional

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    DIM_GRAY = '\033[90m'


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    FORMATS = {
        logging.DEBUG: f"{Colors.DIM_GRAY}%(asctime)s{Colors.RESET} {Colors.BG_CYAN}{Colors.BLACK} DEBUG {Colors.RESET} {Colors.CYAN}%(message)s{Colors.RESET}",
        logging.INFO: f"{Colors.DIM_GRAY}%(asctime)s{Colors.RESET} {Colors.BG_GREEN}{Colors.BLACK} INFO {Colors.RESET} {Colors.GREEN}%(message)s{Colors.RESET}",
        logging.WARNING: f"{Colors.DIM_GRAY}%(asctime)s{Colors.RESET} {Colors.BG_YELLOW}{Colors.BLACK} WARN {Colors.RESET} {Colors.YELLOW}%(message)s{Colors.RESET}",
        logging.ERROR: f"{Colors.DIM_GRAY}%(asctime)s{Colors.RESET} {Colors.BG_RED}{Colors.WHITE} ERROR {Colors.RESET} {Colors.BRIGHT_RED}%(message)s{Colors.RESET}",
        logging.CRITICAL: f"{Colors.DIM_GRAY}%(asctime)s{Colors.RESET} {Colors.BG_RED}{Colors.WHITE} FATAL {Colors.RESET} {Colors.RED}{Colors.BOLD}%(message)s{Colors.RESET}",
    }

    DATE_FORMAT = '%H:%M:%S'

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.DATE_FORMAT)
        return formatter.format(record)


def setup_logging():
    """Setup enhanced logging with colors."""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)

    # Filter out noisy telegram logs
    logging.getLogger('telegram.ext').setLevel(logging.WARNING)
    logging.getLogger('telegram.bot').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

    return logger


def log_user_action(user_id: int, username: Optional[str], action: str, details: str = ""):
    """Log user actions with style."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    user_info = f"@{username}" if username else f"ID:{user_id}"

    print(f"{Colors.DIM_GRAY}{timestamp}{Colors.RESET} {Colors.BG_BLUE}{Colors.WHITE} USER {Colors.RESET} {Colors.BLUE}{user_info}{Colors.RESET} {Colors.CYAN}→{Colors.RESET} {action}{Colors.BRIGHT_CYAN}{details}{Colors.RESET}")


def log_transcription(user_id: int, username: Optional[str], filename: str, duration: float, language: str, status: str = "processing"):
    """Log transcription with details."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    user_info = f"@{username}" if username else f"ID:{user_id}"

    # Status colors
    status_colors = {
        "processing": Colors.YELLOW,
        "success": Colors.GREEN,
        "error": Colors.RED,
    }
    status_color = status_colors.get(status, Colors.WHITE)

    # Format duration
    duration_str = f"{duration:.1f}s" if duration else "unknown"

    print(f"{Colors.DIM_GRAY}{timestamp}{Colors.RESET} {Colors.BG_MAGENTA}{Colors.BLACK} AUDIO {Colors.RESET} "
          f"{Colors.MAGENTA}{user_info}{Colors.RESET} {Colors.CYAN}→{Colors.RESET} "
          f"{Colors.WHITE}{filename}{Colors.RESET} "
          f"{Colors.DIM_GRAY}({duration_str}, {language}){Colors.RESET} "
          f"{status_color}[{status.upper()}]{Colors.RESET}")


def log_api_call(service: str, endpoint: str, status: str = "success", duration: float = None):
    """Log API calls."""
    timestamp = datetime.now().strftime('%H:%M:%S')

    # Status colors
    status_colors = {
        "success": Colors.GREEN,
        "error": Colors.RED,
    }
    status_color = status_colors.get(status, Colors.YELLOW)

    duration_str = f" {Colors.DIM_GRAY}({duration:.2f}s){Colors.RESET}" if duration else ""

    print(f"{Colors.DIM_GRAY}{timestamp}{Colors.RESET} {Colors.BG_CYAN}{Colors.BLACK} API   {Colors.RESET} "
          f"{Colors.CYAN}{service}{Colors.RESET} {Colors.WHITE}{endpoint}{Colors.RESET}"
          f"{duration_str} {status_color}●{Colors.RESET}")
