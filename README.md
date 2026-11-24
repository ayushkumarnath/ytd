# YTD — yt-dlp wrapper

YTD is a Python command-line wrapper for `yt-dlp`. It provides an interactive menu for downloading video, audio as MP3, or video with audio.

## Requirements

- Linux
- Python 3.14.4 or newer
- `yt-dlp`
- `ffmpeg`
- `node`
- `fzf`

YTD checks for these external tools when it starts.

## Run

For development, install [uv](https://docs.astral.sh/uv/) and run from the project directory:

```sh
uv run python ytd.py
```

Choose a download type, then enter the media URL. Choose **Exit** to quit.

The project pins Python 3.15.1 for local development in `.python-version`; the declared minimum supported version is Python 3.14.4.

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

Run the test suite with uv:

```sh
uv run python -m unittest discover -s tests -v
```

The tests mock external commands and use temporary directories.

## Releases

To publish a release, update `VERSION` in `ytd_cli/version.py` and push the change to `main`, or push a matching `vVERSION` tag. After the test job passes, GitHub Actions creates or updates the release and attaches an archive containing the launcher and `ytd_cli/` package. A tag whose version does not match `VERSION` fails validation.

