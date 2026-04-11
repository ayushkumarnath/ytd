#!/usr/bin/bash

SRC_SCRIPT_NAME="ytd"
TARGET_DIR="$HOME/.local/bin/custom"
SRC_SCRIPT="$(pwd)/$SRC_SCRIPT_NAME"

mkdir -p "$TARGET_DIR"

if [[ ! -f "$SRC_SCRIPT" ]]; then
  printf "Error: $SRC_SCRIPT does not exist\n"
  exit 1
fi

cp "$SRC_SCRIPT" "$TARGET_DIR/$SRC_SCRIPT_NAME"
chmod +x "$TARGET_DIR/$SRC_SCRIPT_NAME"

echo "Installed $SRC_SCRIPT_NAME to $TARGET_DIR successfully"
