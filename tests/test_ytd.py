"""Unit tests for the ytd command line wrapper."""

import importlib.util
import io
import os
from pathlib import Path
import signal
import tempfile
import unittest
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_ytd_module():
    """Import ytd.py without letting its startup config touch the project."""
    home = tempfile.TemporaryDirectory()
    working_dir = tempfile.TemporaryDirectory()
    old_cwd = Path.cwd()
    old_handler = signal.getsignal(signal.SIGINT)
    try:
        os.chdir(working_dir.name)
        with mock.patch.dict(os.environ, {"HOME": home.name}), mock.patch(
            "signal.signal"
        ):
            spec = importlib.util.spec_from_file_location("ytd_under_test", PROJECT_ROOT / "ytd.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
    finally:
        os.chdir(old_cwd)
        signal.signal(signal.SIGINT, old_handler)
    return module, home, working_dir


ytd, _IMPORT_HOME, _IMPORT_CWD = load_ytd_module()


class YtdTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.config = self.root / ".config" / "yt-dlp" / "config"
        self.download_dir = self.root / "downloads"
        ytd.CONFIG = self.config
        ytd.DEFAULT_DIR = self.download_dir
        ytd.YT_DLP_STATUS = 0
        self.config.parent.mkdir(parents=True)
        self.config.write_text(f"-o {self.download_dir}/%(title)s.%(ext)s\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_config_option_exists_detects_output_option(self):
        self.assertTrue(ytd.config_option_exists())

    def test_config_option_exists_returns_false_without_output_option(self):
        self.config.write_text("--no-warnings\n")
        self.assertFalse(ytd.config_option_exists())

    def test_get_download_dir_reads_output_template(self):
        self.assertEqual(ytd.get_download_dir(), self.download_dir)

    def test_get_download_dir_returns_none_without_config(self):
        self.config.unlink()
        with mock.patch.object(ytd, "config_option_exists", return_value=False):
            self.assertIsNone(ytd.get_download_dir())

    def test_set_download_dir_creates_directory_and_updates_config(self):
        with mock.patch("builtins.input", return_value="media/new"), mock.patch.dict(
            os.environ, {"HOME": str(self.root)}
        ), mock.patch.object(ytd, "config_option_exists", return_value=True):
            ytd.set_download_dir()

        target = self.root / "media" / "new"
        self.assertTrue(target.is_dir())
        self.assertEqual(
            self.config.read_text(), f"-o {target}/%(title)s.%(ext)s\n"
        )

    def test_download_builds_video_command_and_saves_exit_status(self):
        with mock.patch("builtins.input", return_value="https://example.test/video"), mock.patch.object(
            ytd.subprocess, "run", return_value=mock.Mock(returncode=0)
        ) as run:
            ytd.download(ytd.DOWNLOAD["VIDEO_ONLY"])

        run.assert_called_once_with(
            [
                "yt-dlp",
                "-f",
                "bv*[ext=mp4]",
                "--merge-output-format",
                "mp4",
                "https://example.test/video",
            ]
        )
        self.assertEqual(ytd.YT_DLP_STATUS, 0)

    def test_download_builds_audio_command(self):
        with mock.patch("builtins.input", return_value="url"), mock.patch.object(
            ytd.subprocess, "run", return_value=mock.Mock(returncode=3)
        ) as run:
            ytd.download(ytd.DOWNLOAD["AUDIO_ONLY"])

        self.assertEqual(run.call_args.args[0], ["yt-dlp", "-x", "--audio-format", "mp3", "url"])
        self.assertEqual(ytd.YT_DLP_STATUS, 3)

    def test_download_builds_video_and_audio_command(self):
        with mock.patch("builtins.input", return_value="url"), mock.patch.object(
            ytd.subprocess, "run", return_value=mock.Mock(returncode=0)
        ) as run:
            ytd.download(ytd.DOWNLOAD["AUDIO_VIDEO"])

        self.assertEqual(
            run.call_args.args[0],
            [
                "yt-dlp",
                "-f",
                "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b",
                "--merge-output-format",
                "mp4",
                "url",
            ],
        )

    def test_help_prints_usage_and_options(self):
        output = io.StringIO()
        with mock.patch.object(ytd, "write", output.write):
            ytd.print_help()
        self.assertIn("Usage: ytd [OPTION]", output.getvalue())
        self.assertIn("--get-dir", output.getvalue())
        self.assertIn("--set-dir", output.getvalue())

    def test_parse_help_exits_successfully(self):
        with mock.patch.object(ytd, "print_help") as print_help:
            with self.assertRaises(SystemExit) as raised:
                ytd.parse_arguments(["--help"])
        self.assertEqual(raised.exception.code, 0)
        print_help.assert_called_once_with()

    def test_parse_unknown_argument_exits_with_error(self):
        errors = io.StringIO()
        with mock.patch.object(ytd, "error", errors.write), self.assertRaises(SystemExit) as raised:
            ytd.parse_arguments(["--unknown"])
        self.assertEqual(raised.exception.code, 1)
        self.assertIn("unknown option '--unknown'", errors.getvalue())

    def test_parse_rejects_multiple_arguments(self):
        errors = io.StringIO()
        with mock.patch.object(ytd, "error", errors.write), self.assertRaises(SystemExit) as raised:
            ytd.parse_arguments(["--help", "extra"])
        self.assertEqual(raised.exception.code, 1)
        self.assertIn("accepts only single option", errors.getvalue())

    def test_dependency_check_reports_missing_tools(self):
        errors = io.StringIO()
        with mock.patch.object(ytd.shutil, "which", side_effect=lambda name: None if name in {"fzf", "node"} else "/bin/tool"), mock.patch.object(ytd, "error", errors.write):
            with self.assertRaises(ytd.CLIError):
                ytd.check_dependencies()
        self.assertIn("dependency 'node' not found", errors.getvalue())
        self.assertIn("dependency 'fzf' not found", errors.getvalue())
        self.assertIn("Please install the required dependencies", errors.getvalue())

    def test_fzf_process_returns_selected_choice(self):
        with mock.patch.object(
            ytd.subprocess, "run", return_value=mock.Mock(stdout=f"{ytd.options[1]}\n")
        ) as run:
            result = ytd.fzf_process()
        self.assertEqual(result, ytd.options[1])
        self.assertEqual(run.call_args.kwargs["input"], "\n".join(ytd.options))

    def test_fzf_process_returns_none_when_cancelled(self):
        with mock.patch.object(
            ytd.subprocess, "run", side_effect=ytd.subprocess.CalledProcessError(130, "fzf")
        ):
            self.assertIsNone(ytd.fzf_process())

    def test_main_reports_missing_download_directory(self):
        errors = io.StringIO()
        with mock.patch.object(ytd, "check_dependencies"), mock.patch.object(
            ytd, "get_download_dir", return_value=None
        ), mock.patch.object(ytd, "error", errors.write):
            self.assertEqual(ytd.main([]), 1)
        self.assertIn("cannot resolve download directory", errors.getvalue())

    def test_main_download_flow_reports_saved_location(self):
        output = io.StringIO()
        with mock.patch.object(ytd, "check_dependencies"), mock.patch.object(
            ytd, "fzf_process", return_value=ytd.options[0]
        ), mock.patch.object(ytd, "download") as download, mock.patch.object(ytd, "write", output.write):
            self.assertEqual(ytd.main([]), 0)
        download.assert_called_once_with(ytd.options[0])
        self.assertTrue(self.download_dir.is_dir())
        self.assertIn(f"Saved to {self.download_dir}", output.getvalue())

    def test_main_reports_failed_download(self):
        errors = io.StringIO()

        def fail_download(_option):
            ytd.YT_DLP_STATUS = 1

        with mock.patch.object(ytd, "check_dependencies"), mock.patch.object(
            ytd, "fzf_process", return_value=ytd.options[1]
        ), mock.patch.object(ytd, "download", side_effect=fail_download), mock.patch.object(ytd, "error", errors.write):
            self.assertEqual(ytd.main([]), 1)
        self.assertIn("Error occurred", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
