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

The installer copies `ytd.py` as an executable named `ytd` into `~/.local/bin`. It adds that directory to `~/.bashrc` if needed. Start a new shell or source `~/.bashrc` before invoking `ytd` from anywhere.

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

To publish a release, make sure `VERSION` in `ytd.py` matches the version tag, such as `2.0.0` and `v2.0.0`. Push the tag to GitHub:

```sh
git tag v2.0.0
git push origin v2.0.0
```

GitHub Actions runs the tests, checks that the tag matches `VERSION`, packages the app files, and publishes a GitHub Release with the `.tar.gz` archive attached.

