import subprocess

from .console import error
from .settings import RED, YELLOW, RESET
from .yesno import YES_LIST

# Download types
DOWNLOAD = {
    "VIDEO_ONLY": "Download video",
    "AUDIO_ONLY": "Download audio (MP3)",
    "AUDIO_VIDEO": "Download video + audio",
}


def download(option):
    command = ["yt-dlp"]

    """
    Since yt-dlp handles invalid and unsupported URLs, I am not gonna waste
    time implementing a custom URL validator myself. I will just feed yt-dlp
    the whitespace-stripped version of the URL, it'll take care of the rest.
    """
    url = input("Enter URL: ").strip()

    if option != DOWNLOAD["AUDIO_ONLY"]:
        subtitles = input("Do you want subtitles? (Y/n): ")
        if not subtitles or subtitles in YES_LIST:
            command.extend(
                [
                    "--embed-subs",
                    "--sub-langs",
                    "en.*,-live_chat",
                    "--sub-format",
                    "srt",
                ]
            )
        else:
            error(f"{YELLOW}Moving on with no subtitles{RESET}\n")

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
        result = subprocess.run(command, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        error(f"{RED}Error: subprocess (yt-dlp): {e}{RESET}")
        return 1
