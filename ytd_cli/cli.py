import signal
import sys

from .config import get_download_dir, initialize_config, set_download_dir
from .console import error, write
from .dependencies import check_dependencies
from .downloader import download
from .exceptions import CLIError
from .menu import fzf_process, options
from .settings import RED, RESET


VERSION = "2.0.3"


def print_error(err_msg):
    error(f"Error: {err_msg}\n")
    error("See --help for more info\n")


def print_help():
    write("ytd - yt-dlp wrapper\n\n")

    write("Usage: ytd [OPTION]\n\n")

    write("Options:\n")
    write("%-24s %s\n" % ("-h, --help", "Display this help menu"))
    write("%-24s %s\n" % ("-v, --version", "Display version information"))
    write(
        "%-24s %s\n" % ("-gd, --get-dir", "Display the current download directory path")
    )
    write("%-24s %s\n" % ("-sd, --set-dir", "Set/Change the download directory path"))


def print_version():
    write(f"ytd {VERSION}\n")


def parse_arguments(args):
    if len(args) > 1:
        error("this program accepts only single option")
        sys.exit(1)
    elif len(args) == 1:
        argument = args[0]

        if argument in ("-h", "--help"):
            print_help()
            sys.exit(0)
        elif argument in ("-v", "--version"):
            print_version()
            sys.exit(0)
        elif argument in ("-gd", "--get-dir"):
            print(f"All media is saved to: {get_download_dir()}")
            sys.exit(0)
        elif argument in ("-sd", "--set-dir"):
            set_download_dir()
            print("Download directory changed successfully")
            sys.exit(0)
        else:
            error(f"unknown option '{argument}'")
            sys.exit(1)


def cleanup(signum, frame):
    write("\n\nInterrupted. Exiting...\n")
    sys.exit(0)


def main(args):
    signal.signal(signal.SIGINT, cleanup)

    initialize_config()

    try:
        parse_arguments(args)
        check_dependencies()
    except CLIError as e:
        if str(e) != "missing dependencies":
            error(str(e))
        return 1

    DOWNLOAD_DIR = get_download_dir()

    if DOWNLOAD_DIR is None:
        error(f"{RED}Error: download directory is not set{RESET}")
        error("Use '-sd' to set download directory. For help menu use '-h'")
        return 1

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    choice = fzf_process()
    if choice is None:
        return 0

    if choice == options[0]:
        write("Video only\n")
    elif choice == options[1]:
        write("Audio only\n")
    elif choice == options[2]:
        write("Video + Audio\n")
    elif choice == options[3]:
        return 0

    yt_dlp_status = download(choice)

    if yt_dlp_status == 0:
        write(f"Saved to {DOWNLOAD_DIR}\n")
        return 0
    else:
        error("Error occurred\n")
        return 1
