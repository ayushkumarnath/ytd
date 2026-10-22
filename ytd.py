#!/usr/bin/env python3

import signal, sys, shutil, subprocess
from pathlib import Path

write = sys.stdout.write
error = sys.stderr.write


class CLIError(Exception):
    pass


CONFIG = Path("~/.config/yt-dlp/config").expanduser()
DEFAULT_DIR = Path("~/downloads").expanduser()
YT_DLP_STATUS = 0

# Global constants
ESC = "\033"

# Colors
RED = f"{ESC}[0;31m"
RESET = f"{ESC}[0m"

# Download types
DOWNLOAD = {
    "VIDEO_ONLY": "Download video",
    "AUDIO_ONLY": "Download audio (MP3)",
    "AUDIO_VIDEO": "Download video + audio",
}

# Options presented to the user
options = (
    f"{DOWNLOAD['VIDEO_ONLY']}",
    f"{DOWNLOAD['AUDIO_ONLY']}",
    f"{DOWNLOAD['AUDIO_VIDEO']}",
    "Exit",
)


def cleanup(signum, frame):
    write("\n\nInterrupted. Exiting...\n")
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)


def config_option_exists():
    with open(str(CONFIG), "r") as file:
        for line in file:
            if line.startswith("-o "):
                return True

    return False


def initialize_config():
    if not CONFIG.is_file():
        CONFIG.parent.mkdir(parents=True, exist_ok=True)
        with open(str(CONFIG), "w") as file:
            file.write(f"-o {DEFAULT_DIR}/%(title)s.%(ext)s")
    elif not config_option_exists():
        with open(str(CONFIG), "a") as file:
            file.write(f"-o {DEFAULT_DIR}/%(title)s.%(ext)s")


initialize_config()


def get_download_dir():
    extracted_download_path = None

    if CONFIG.is_file() and config_option_exists():
        with open(str(CONFIG), "r") as file:
            for line in file:
                if line.startswith("-o "):
                    path_part = line[len("-o ") :].strip()

                    if "%(title)s" in path_part:
                        path_part = path_part.split("%(title)s")[0]

                    extracted_download_path = path_part.strip()
                    break

        return (
            Path(extracted_download_path)
            if extracted_download_path is not None
            else extracted_download_path
        )


def set_download_dir():
    new_dir = input("Enter new directory path (relative to HOME directory): ")
    new_download_dir = Path(f"~/{new_dir}").expanduser()

    new_download_dir.mkdir(parents=True, exist_ok=True)

    if CONFIG.is_file() and config_option_exists():
        with open(str(CONFIG), "r") as file:
            updated_lines = []
            new_line = f"-o {new_download_dir}/%(title)s.%(ext)s"
            for line in file:
                if line.startswith("-o"):
                    line = f"{new_line}\n"
                updated_lines.append(line)

        with open(str(CONFIG), "w") as file:
            file.write("".join(updated_lines))


def download(option):
    global YT_DLP_STATUS

    url = input("Enter URL: ")

    command = ["yt-dlp"]

    if option == f"{DOWNLOAD['VIDEO_ONLY']}":
        command.extend(
            [
                "-f",
                "bv*[ext=mp4]",
                "--merge-output-format",
                "mp4",
            ]
        )
    elif option == f"{DOWNLOAD['AUDIO_ONLY']}":
        command.extend(
            [
                "-x",
                "--audio-format",
                "mp3",
            ]
        )
    elif option == f"{DOWNLOAD['AUDIO_VIDEO']}":
        command.extend(
            [
                "-f",
                "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b",
                "--merge-output-format",
                "mp4",
            ]
        )

    command.append(url)

    try:
        result = subprocess.run(command)
        YT_DLP_STATUS = result.returncode
    except subprocess.CalledProcessError as e:
        error(f"{RED}Error: subprocess (yt-dlp): {e}{RESET}")


def print_help():
    write("ytd - yt-dlp wrapper\n\n")

    write("Usage: ytd [OPTION]\n\n")

    write("Options:\n")
    write("%-24s %s\n" % ("-h, --help", "Display this help menu"))
    write(
        "%-24s %s\n" % ("-gd, --get-dir", "Display the current download directory path")
    )
    write("%-24s %s\n" % ("-sd, --set-dir", "Set/Change the download directory path"))


def print_error(err_msg):
    error(f"Error: {err_msg}\n")
    error("See --help for more info\n")


# ====== Argument parsing ===== #
# This program is supposed to accept only single argument
def parse_arguments(args):
    if len(args) > 1:
        error("this program accepts only single option")
        sys.exit(1)
    elif len(args) == 1:
        argument = args[0]

        if argument in ("-h", "--help"):
            print_help()
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


# fzf process
def fzf_process():
    choices = "\n".join(options)

    try:
        result = subprocess.run(
            ["fzf", "--prompt=Select option > ", "--layout=reverse"],
            input=choices,
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


# Program starts
def main(args):
    try:
        parse_arguments(args)
        check_dependencies()
    except CLIError as e:
        if str(e) != "missing dependencies":
            error(str(e))
        return 1

    DOWNLOAD_DIR = get_download_dir()

    if DOWNLOAD_DIR is None:
        error("Error: cannot resolve download directory")
        return 1

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    choice = fzf_process()

    if choice == options[0]:
        write("Video only\n")
        download(options[0])
    elif choice == options[1]:
        write("Audio only\n")
        download(options[1])
    elif choice == options[2]:
        write("Video + Audio\n")
        download(options[2])
    elif choice == options[3]:
        sys.exit(0)

    if YT_DLP_STATUS == 0:
        write(f"Saved to {DOWNLOAD_DIR}\n")
        return 0
    else:
        error("Error occurred\n")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
