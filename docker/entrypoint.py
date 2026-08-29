"""Dispatch container arguments to Manim Slides or an installed executable."""

import os
import shutil
import sys
from collections.abc import Callable, Sequence

ExecutableFinder = Callable[[str], str | None]


def resolve_command(
    arguments: Sequence[str], find_executable: ExecutableFinder = shutil.which
) -> list[str]:
    """Return the process command for container arguments."""
    command = list(arguments)
    if not command:
        return ["manim-slides", "--silent", "--help"]
    if find_executable(command[0]) is not None:
        return command
    return ["manim-slides", "--silent", *command]


def main() -> None:
    """Replace the entrypoint process so signals reach the invoked command."""
    command = resolve_command(sys.argv[1:])
    os.execvp(command[0], command)


if __name__ == "__main__":
    main()
