from pathlib import Path

CONFIG = Path("~/.config/yt-dlp/config").expanduser()
DEFAULT_DIR = Path("~/downloads").expanduser()


def initialize_config():
    if not CONFIG.is_file():
        CONFIG.parent.mkdir(parents=True, exist_ok=True)
        with open(str(CONFIG), "w") as file:
            file.write(f"-o {DEFAULT_DIR}/%(title)s.%(ext)s")
    elif not config_option_exists():
        with open(str(CONFIG), "a") as file:
            file.write(f"-o {DEFAULT_DIR}/%(title)s.%(ext)s")


def config_option_exists():
    with open(str(CONFIG), "r") as file:
        for line in file:
            if line.startswith("-o "):
                return True

    return False


def get_download_dir():
    extracted_download_path = None

    if CONFIG.is_file() and config_option_exists():
        with open(str(CONFIG), "r") as file:
            for line in file:
                if line.startswith("-o "):
                    path_part = line[len("-o ") :].strip()

                    if "%(title)s" in path_part:
                        path_part = path_part.split("%(title)s")[0]

                    extracted_download_path = path_part.strip()
                    break

        return (
            Path(extracted_download_path)
            if extracted_download_path is not None
            else extracted_download_path
        )


def set_download_dir():
    new_dir = input("Enter new directory path (relative to HOME directory): ")
    new_download_dir = Path(f"~/{new_dir}").expanduser()

    new_download_dir.mkdir(parents=True, exist_ok=True)

    if CONFIG.is_file() and config_option_exists():
        with open(str(CONFIG), "r") as file:
            updated_lines = []
            new_line = f"-o {new_download_dir}/%(title)s.%(ext)s"
            for line in file:
                if line.startswith("-o"):
                    line = f"{new_line}\n"
                updated_lines.append(line)

        with open(str(CONFIG), "w") as file:
            file.write("".join(updated_lines))
