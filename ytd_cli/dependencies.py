import shutil

from .console import error
from .exceptions import CLIError
from .settings import RED, RESET


# Dependency checks
def check_dependencies():
    missing = [
        name
        for name in ("yt-dlp", "ffmpeg", "node", "fzf")
        if shutil.which(name) is None
    ]
    if missing:
        for dependency in missing:
            error(f"{RED}Error: dependency '{dependency}' not found{RESET}\n")
        error("Please install the required dependencies\n\n")
        raise CLIError("missing dependencies")
