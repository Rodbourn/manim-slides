import runpy
import unittest
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import cast

ROOT = Path(__file__).parents[1]
ENTRYPOINT = ROOT / "docker" / "entrypoint.py"
ResolveCommand = Callable[[Sequence[str], Callable[[str], str | None]], list[str]]
resolve_command = cast(
    ResolveCommand, runpy.run_path(str(ENTRYPOINT))["resolve_command"]
)


def find_executable(name: str) -> str | None:
    if name in {"bash", "python"}:
        return f"/usr/bin/{name}"
    return None


class ContainerEntrypointTest(unittest.TestCase):
    def test_defaults_to_cli_help(self) -> None:
        self.assertEqual(
            resolve_command([], find_executable),
            ["manim-slides", "--silent", "--help"],
        )

    def test_dispatches_arguments_to_manim_slides(self) -> None:
        arguments = [
            "convert",
            "Demo",
            "demo.html",
            "--to=html-player",
            "--one-file",
        ]
        self.assertEqual(
            resolve_command(arguments, find_executable),
            ["manim-slides", "--silent", *arguments],
        )

    def test_passes_installed_commands_through(self) -> None:
        arguments = ["bash", "-lc", "manim-slides --version"]
        self.assertEqual(resolve_command(arguments, find_executable), arguments)


class DockerImageContractTest(unittest.TestCase):
    def test_dockerfile_exposes_workspace_cli(self) -> None:
        dockerfile = (ROOT / "docker" / "Dockerfile").read_text()
        self.assertIn("WORKDIR /workspace", dockerfile)
        self.assertIn("--home ${HOME}", dockerfile)
        self.assertIn(
            'ENTRYPOINT ["python", "/usr/local/lib/manim-slides/entrypoint.py"]',
            dockerfile,
        )

    def test_build_context_excludes_local_coordination_files(self) -> None:
        ignored = (ROOT / ".dockerignore").read_text().splitlines()
        self.assertIn("AGENTS.md", ignored)
        self.assertIn("PORTABLE_HTML_EXPORT_TASK.md", ignored)
