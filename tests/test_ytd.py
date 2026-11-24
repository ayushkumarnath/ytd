"""Unit tests for the ytd command line wrapper."""

import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from ytd_cli import cli, config, dependencies, downloader, menu
from ytd_cli.exceptions import CLIError
from ytd_cli.version import VERSION


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.config_path = self.root / ".config" / "yt-dlp" / "config"
        self.download_dir = self.root / "downloads"
        self.config_path.parent.mkdir(parents=True)
        self.config_path.write_text(
            f'-o "{self.download_dir}/{config.OUTPUT_TEMPLATE}"\n'
        )
        self.config_patch = mock.patch.object(config, "CONFIG", self.config_path)
        self.default_dir_patch = mock.patch.object(config, "DEFAULT_DIR", self.download_dir)
        self.config_patch.start()
        self.default_dir_patch.start()

    def tearDown(self):
        self.default_dir_patch.stop()
        self.config_patch.stop()
        self.temp_dir.cleanup()

    def test_config_option_exists_detects_output_option(self):
        self.assertTrue(config.config_option_exists())

    def test_config_option_exists_returns_false_without_output_option(self):
        self.config_path.write_text("--no-warnings\n")
        self.assertFalse(config.config_option_exists())

    def test_initialize_config_creates_default_config(self):
        self.config_path.unlink()
        config.initialize_config()
        self.assertEqual(
            self.config_path.read_text(),
            f'-o "{config.DEFAULT_DIR}/{config.OUTPUT_TEMPLATE}"',
        )

    def test_get_download_dir_reads_output_template(self):
        self.assertEqual(config.get_download_dir(), self.download_dir)

    def test_output_template_limits_title_by_utf8_byte_length(self):
        self.assertEqual(config.BYTE_LEN, 120)
        self.assertEqual(config.OUTPUT_TITLE, "%(title).120B")
        self.assertEqual(config.OUTPUT_TEMPLATE, "%(title).120B.%(ext)s")

    def test_get_download_dir_returns_none_without_config(self):
        self.config_path.unlink()
        self.assertIsNone(config.get_download_dir())

    def test_set_download_dir_creates_directory_and_updates_config(self):
        with mock.patch("builtins.input", return_value="media/new"), mock.patch.dict(
            os.environ, {"HOME": str(self.root)}
        ):
            config.set_download_dir()

        target = self.root / "media" / "new"
        self.assertTrue(target.is_dir())
        self.assertEqual(
            self.config_path.read_text(), f"-o {target}/{config.OUTPUT_TEMPLATE}\n"
        )


class DownloaderTests(unittest.TestCase):
    def test_download_builds_video_command_and_returns_status(self):
        with mock.patch(
            "builtins.input", return_value="https://example.test/video"
        ), mock.patch.object(
            downloader.subprocess, "run", return_value=mock.Mock(returncode=0)
        ) as run:
            result = downloader.download(downloader.DOWNLOAD["VIDEO_ONLY"])

        run.assert_called_once_with(
            [
                "yt-dlp",
                "-f",
                "bv*[ext=mp4]",
                "--merge-output-format",
                "mp4",
                "https://example.test/video",
            ],
            check=True,
        )
        self.assertEqual(result, 0)

    def test_download_builds_audio_command(self):
        with mock.patch("builtins.input", return_value="url"), mock.patch.object(
            downloader.subprocess, "run", return_value=mock.Mock(returncode=0)
        ) as run:
            result = downloader.download(downloader.DOWNLOAD["AUDIO_ONLY"])

        self.assertEqual(
            run.call_args.args[0],
            ["yt-dlp", "-x", "--audio-format", "mp3", "url"],
        )
        self.assertEqual(result, 0)

    def test_download_builds_video_and_audio_command(self):
        with mock.patch("builtins.input", return_value="url"), mock.patch.object(
            downloader.subprocess, "run", return_value=mock.Mock(returncode=0)
        ) as run:
            downloader.download(downloader.DOWNLOAD["AUDIO_VIDEO"])

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

    def test_download_returns_failure_status_when_subprocess_fails(self):
        errors = io.StringIO()
        with mock.patch("builtins.input", return_value="url"), mock.patch.object(
            downloader.subprocess,
            "run",
            side_effect=downloader.subprocess.CalledProcessError(3, "yt-dlp"),
        ), mock.patch.object(downloader, "error", errors.write):
            result = downloader.download(downloader.DOWNLOAD["AUDIO_ONLY"])

        self.assertEqual(result, 1)
        self.assertIn("subprocess (yt-dlp)", errors.getvalue())


class MenuTests(unittest.TestCase):
    def test_fzf_process_returns_selected_choice(self):
        with mock.patch.object(
            menu.subprocess, "run", return_value=mock.Mock(stdout=f"{menu.options[1]}\n")
        ) as run:
            result = menu.fzf_process()

        self.assertEqual(result, menu.options[1])
        self.assertEqual(run.call_args.kwargs["input"], "\n".join(menu.options))

    def test_fzf_process_returns_none_when_cancelled(self):
        with mock.patch.object(
            menu.subprocess,
            "run",
            side_effect=menu.subprocess.CalledProcessError(130, "fzf"),
        ):
            self.assertIsNone(menu.fzf_process())


class DependencyTests(unittest.TestCase):
    def test_dependency_check_reports_missing_tools(self):
        errors = io.StringIO()
        missing = {"fzf", "node"}
        with mock.patch.object(
            dependencies.shutil,
            "which",
            side_effect=lambda name: None if name in missing else "/bin/tool",
        ), mock.patch.object(dependencies, "error", errors.write):
            with self.assertRaises(CLIError):
                dependencies.check_dependencies()

        self.assertIn("dependency 'node' not found", errors.getvalue())
        self.assertIn("dependency 'fzf' not found", errors.getvalue())
        self.assertIn("Please install the required dependencies", errors.getvalue())

    def test_dependency_check_succeeds_when_tools_are_present(self):
        with mock.patch.object(dependencies.shutil, "which", return_value="/bin/tool"):
            dependencies.check_dependencies()


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.download_dir = Path(self.temp_dir.name) / "downloads"
        self.signal_patch = mock.patch.object(cli.signal, "signal")
        self.signal_patch.start()

    def tearDown(self):
        self.signal_patch.stop()
        self.temp_dir.cleanup()

    def test_help_prints_usage_and_options(self):
        output = io.StringIO()
        with mock.patch.object(cli, "write", output.write):
            cli.print_help()
        self.assertIn("Usage: ytd [OPTION]", output.getvalue())
        self.assertIn("--get-dir", output.getvalue())
        self.assertIn("--set-dir", output.getvalue())

    def test_print_version_includes_v_prefix(self):
        output = io.StringIO()
        with mock.patch.object(cli, "write", output.write):
            cli.print_version()
        self.assertEqual(output.getvalue(), f"ytd v{cli.VERSION}\n")
        self.assertEqual(cli.VERSION, VERSION)

    def test_parse_help_exits_successfully(self):
        with mock.patch.object(cli, "print_help") as print_help:
            with self.assertRaises(SystemExit) as raised:
                cli.parse_arguments(["--help"])
        self.assertEqual(raised.exception.code, 0)
        print_help.assert_called_once_with()

    def test_parse_unknown_argument_exits_with_error(self):
        errors = io.StringIO()
        with mock.patch.object(cli, "error", errors.write), self.assertRaises(
            SystemExit
        ) as raised:
            cli.parse_arguments(["--unknown"])
        self.assertEqual(raised.exception.code, 1)
        self.assertIn("unknown option '--unknown'", errors.getvalue())

    def test_parse_rejects_multiple_arguments(self):
        errors = io.StringIO()
        with mock.patch.object(cli, "error", errors.write), self.assertRaises(
            SystemExit
        ) as raised:
            cli.parse_arguments(["--help", "extra"])
        self.assertEqual(raised.exception.code, 1)
        self.assertIn("accepts only single option", errors.getvalue())

    def test_main_reports_missing_download_directory(self):
        errors = io.StringIO()
        with mock.patch.object(cli, "initialize_config"), mock.patch.object(
            cli, "check_dependencies"
        ), mock.patch.object(cli, "get_download_dir", return_value=None), mock.patch.object(
            cli, "error", errors.write
        ):
            self.assertEqual(cli.main([]), 1)
        self.assertIn("Error: download directory is not set", errors.getvalue())
        self.assertIn("Use '-sd' to set download directory", errors.getvalue())

    def test_main_download_flow_reports_saved_location(self):
        output = io.StringIO()
        with mock.patch.object(cli, "initialize_config"), mock.patch.object(
            cli, "check_dependencies"
        ), mock.patch.object(
            cli, "get_download_dir", return_value=self.download_dir
        ), mock.patch.object(
            cli, "fzf_process", return_value=menu.options[0]
        ), mock.patch.object(cli, "download", return_value=0) as download, mock.patch.object(
            cli, "write", output.write
        ):
            self.assertEqual(cli.main([]), 0)

        download.assert_called_once_with(menu.options[0])
        self.assertTrue(self.download_dir.is_dir())
        self.assertIn(f"Saved to {self.download_dir}", output.getvalue())

    def test_main_reports_failed_download(self):
        errors = io.StringIO()
        with mock.patch.object(cli, "initialize_config"), mock.patch.object(
            cli, "check_dependencies"
        ), mock.patch.object(
            cli, "get_download_dir", return_value=self.download_dir
        ), mock.patch.object(
            cli, "fzf_process", return_value=menu.options[1]
        ), mock.patch.object(cli, "download", return_value=1), mock.patch.object(
            cli, "error", errors.write
        ):
            self.assertEqual(cli.main([]), 1)
        self.assertIn("Error occurred", errors.getvalue())

    def test_main_does_not_download_when_menu_is_cancelled(self):
        errors = io.StringIO()
        with mock.patch.object(cli, "initialize_config"), mock.patch.object(
            cli, "check_dependencies"
        ), mock.patch.object(
            cli, "get_download_dir", return_value=self.download_dir
        ), mock.patch.object(
            cli, "fzf_process", return_value=None
        ), mock.patch.object(cli, "download") as download, mock.patch.object(
            cli, "error", errors.write
        ):
            self.assertEqual(cli.main([]), 0)
        download.assert_not_called()
        self.assertEqual(errors.getvalue(), "")

    def test_main_exits_when_user_selects_exit(self):
        with mock.patch.object(cli, "initialize_config"), mock.patch.object(
            cli, "check_dependencies"
        ), mock.patch.object(
            cli, "get_download_dir", return_value=self.download_dir
        ), mock.patch.object(
            cli, "fzf_process", return_value=menu.options[3]
        ), mock.patch.object(cli, "download") as download:
            self.assertEqual(cli.main([]), 0)
        download.assert_not_called()


if __name__ == "__main__":
    unittest.main()
