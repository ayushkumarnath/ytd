#!/usr/bin/bash

SRC_SCRIPT_NAME="ytd"
SRC_SCRIPT="$(pwd)/$SRC_SCRIPT_NAME"
TARGET_DIR="$HOME/.local/bin/custom"
SHELL_CONFIG_NAME=".bashrc"
SHELL_CONFIG="$HOME/$SHELL_CONFIG_NAME"

mkdir -p "$TARGET_DIR"

# Adds TARGET_DIR to PATH, if not already present
PATH_STRING="export PATH=\"${TARGET_DIR}:\$PATH\""
if [[ -f "$SHELL_CONFIG" ]]; then
  if ! { grep -xFq "export PATH=\"\$HOME/.local/bin/custom:\$PATH\"" "$SHELL_CONFIG" || grep -xFq "$PATH_STRING" "$SHELL_CONFIG"; }; then
    printf "\n# ADD '${TARGET_DIR}' to PATH\n${PATH_STRING}\n" >>"$SHELL_CONFIG"
  fi
else
  printf "\n# ADD '${TARGET_DIR}' to PATH\n${PATH_STRING}\n" >"$SHELL_CONFIG"
fi

if [[ ! -f "$SRC_SCRIPT" ]]; then
  printf "Error: $SRC_SCRIPT does not exist\n" >&2
  exit 1
fi

# Dependency check
require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf "Warning: dependency '%s' not found\n" "$1" >&2
    printf "Please install the required dependencies\n\n" >&2
  fi
}
deps=("yt-dlp" "ffmpeg" "node" "fzf")
for dep in "${deps[@]}"; do
  require "$dep"
done

cp "$SRC_SCRIPT" "$TARGET_DIR/$SRC_SCRIPT_NAME"
chmod +x "$TARGET_DIR/$SRC_SCRIPT_NAME"

echo "Installed $SRC_SCRIPT_NAME to $TARGET_DIR successfully"
