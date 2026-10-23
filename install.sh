#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SRC_SCRIPT="$SCRIPT_DIR/ytd.py"
SRC_PACKAGE="$SCRIPT_DIR/ytd_cli"
TARGET_DIR="$HOME/.local/bin"
SHELL_CONFIG="$HOME/.bashrc"

# Colors
YELLOW='\033[0;33m'
RESET='\033[0m'

if [[ ! -f "$SRC_SCRIPT" ]]; then
  printf "Error: %s does not exist\n" "$SRC_SCRIPT" >&2
  exit 1
fi

if [[ ! -d "$SRC_PACKAGE" ]]; then
  printf "Error: %s does not exist\n" "$SRC_PACKAGE" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  printf "Error: dependency 'python3' not found\n" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"

# Add the install directory to PATH if it is not already configured.
PATH_STRING="export PATH=\"$TARGET_DIR:\$PATH\""
if [[ ! -f "$SHELL_CONFIG" ]] || ! grep -Fqx "$PATH_STRING" "$SHELL_CONFIG"; then
  printf "\n# Add YTD to PATH\n%s\n" "$PATH_STRING" >> "$SHELL_CONFIG"
  printf "Added %s to PATH in %s\n" "$TARGET_DIR" "$SHELL_CONFIG"
fi

install -m 755 "$SRC_SCRIPT" "$TARGET_DIR/ytd"
cp -R "$SRC_PACKAGE" "$TARGET_DIR/"

# Check runtime tools. The app reports missing tools when it is run.
missing_deps=()
for dep in yt-dlp ffmpeg node fzf; do
  if ! command -v "$dep" >/dev/null 2>&1; then
    missing_deps+=("$dep")
  fi
done

if [[ ${#missing_deps[@]} -gt 0 ]]; then
  for dep in "${missing_deps[@]}"; do
    printf "${YELLOW}Warning:${RESET} dependency '%s' not found\n" "$dep" >&2
  done
  printf "Install the missing tools before using YTD.\n" >&2
fi

printf "Installed YTD to '%s'\n" "$TARGET_DIR"
if [[ ":$PATH:" != *":$TARGET_DIR:"* ]]; then
  printf "Run 'source %s' or restart your shell to update PATH.\n" "$SHELL_CONFIG"
fi
