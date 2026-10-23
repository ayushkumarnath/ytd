import subprocess

from .downloader import DOWNLOAD

# Options presented to the user
options = (
    f"{DOWNLOAD['VIDEO_ONLY']}",
    f"{DOWNLOAD['AUDIO_ONLY']}",
    f"{DOWNLOAD['AUDIO_VIDEO']}",
    "Exit",
)


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
