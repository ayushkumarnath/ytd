import subprocess

from .console import error
from .settings import RED, RESET

# Download types
DOWNLOAD = {
    "VIDEO_ONLY": "Download video",
    "AUDIO_ONLY": "Download audio (MP3)",
    "AUDIO_VIDEO": "Download video + audio",
}


def download(option):
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
        result = subprocess.run(command, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        error(f"{RED}Error: subprocess (yt-dlp): {e}{RESET}")
        return 1
