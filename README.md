# YTD — yt-dlp wrapper

YTD is a Python command-line wrapper for `yt-dlp`. It provides an interactive menu for downloading video, audio as MP3, or video with audio.

## Requirements

- Linux
- Python 3
- `yt-dlp`
- `ffmpeg`
- `node`
- `fzf`

YTD checks for these external tools when it starts.

## Run

From the project directory, run:

```sh
python3 ytd.py
```

Choose a download type, then enter the media URL. Choose **Exit** to quit.

## Install

From the project directory, run:

```sh
./install.sh
source ~/.bashrc
```

The installer installs the launcher as `~/.local/bin/ytd` (the command name is `ytd`, without a `.py` suffix) and installs the `ytd_cli/` Python package alongside it. It adds `~/.local/bin` to `~/.bashrc` if needed. Start a new shell or source `~/.bashrc`, then run the installed program with:

```sh
ytd
```

### Options

```sh
python3 ytd.py --help
python3 ytd.py --get-dir
python3 ytd.py --set-dir
```

`--get-dir` displays the current download directory. `--set-dir` prompts for a directory path relative to your home directory.

## Download directory

YTD reads its yt-dlp config from `~/.config/yt-dlp/config`. If the config does not exist or has no output option, YTD initializes it to save media under `~/downloads`.

## Tests

Run the test suite with Python's built-in unittest runner:

```sh
python3 -m unittest discover -s tests -v
```

The tests mock external commands and use temporary directories.

## Releases

To publish a release, make sure `VERSION` in `ytd_cli/cli.py` matches the version tag, such as `2.0.0` and `v2.0.0`. Push the tag to GitHub:

```sh
git tag v2.0.0
git push origin v2.0.0
```

The release workflow must check the version in `ytd_cli/cli.py` and include the `ytd_cli/` package in its archive along with `ytd.py`, `install.sh`, and this README. The current workflow still needs to be updated for the new package layout before tagged releases will work.

