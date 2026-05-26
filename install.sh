#!/usr/bin/bash

SRC_SCRIPT_NAME="ytd"
SRC_SCRIPT="$(pwd)/$SRC_SCRIPT_NAME"
TARGET_DIR="$HOME/.local/bin/custom"
SHELL_CONFIG_NAME=".bashrc"
SHELL_CONFIG="$HOME/$SHELL_CONFIG_NAME"

printf "Creating target directory..."

mkdir -p "$TARGET_DIR"

printf "done\n\n"

# Adds TARGET_DIR to PATH, if not already present
PATH_STRING="export PATH=\"${TARGET_DIR}:\$PATH\""
is_target_in_path=0

if [[ -f "$SHELL_CONFIG" ]]; then
  printf "Searching PATH for target directory..."

  if ! { grep -xFq "export PATH=\"\$HOME/.local/bin/custom:\$PATH\"" "$SHELL_CONFIG" || grep -xFq "$PATH_STRING" "$SHELL_CONFIG"; }; then
    printf "done\n\n"
    printf "\tAdding target directory to PATH..."

    printf "\n# ADD '${TARGET_DIR}' to PATH\n${PATH_STRING}\n" >>"$SHELL_CONFIG"

    is_target_in_path=1

    printf "done\n\n"
  fi

  if [[ $is_target_in_path -eq 0 ]]; then
    printf "done\n\n"
  fi
else
  printf "\tAdding target directory to PATH..."

  printf "\n# ADD '${TARGET_DIR}' to PATH\n${PATH_STRING}\n" >"$SHELL_CONFIG"

  is_target_in_path=1

  printf "done\n\n"
fi

if [[ ! -f "$SRC_SCRIPT" ]]; then
  printf "Error: $SRC_SCRIPT does not exist\n" >&2
  exit 1
fi

# Dependency check
are_deps_ok=0

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    missing_deps+=("$1")
    are_deps_ok=1
  fi
}

printf "Checking dependencies..."

deps=("yt-dlp" "ffmpeg" "node" "fzf")
missing_deps=()
for dep in "${deps[@]}"; do
  require "$dep"
done

if [[ ${#missing_deps[@]} -ne 0 ]]; then
  printf "\n"
  for dep in "${missing_deps[@]}"; do
    printf "Warning: dependency '%s' not found\n" "$dep" >&2
  done
  printf "Please install the required dependencies\n\n" >&2
fi

if [[ $are_deps_ok -eq 0 ]]; then
  printf "done\n\n"
fi

printf "Beginning installation...\n"

cp "$SRC_SCRIPT" "$TARGET_DIR/$SRC_SCRIPT_NAME"
chmod +x "$TARGET_DIR/$SRC_SCRIPT_NAME"

printf "Installed $SRC_SCRIPT_NAME to '$TARGET_DIR' successfully\n"

if [[ $is_target_in_path -eq 1 ]]; then
  printf "\nPlease restart your terminal or run 'source $SHELL_CONFIG'\n"
fi
