# Docker Image

The Manim Slides image contains Python, Manim Community Edition, Manim Slides,
system rendering libraries, fonts, and a minimal TeX Live installation. Use it to
render ordinary Python scene definitions and export presentations without
installing those dependencies on the host.

The image runs as a non-root user and treats `/workspace` as the project directory.
Its default entrypoint is the `manim-slides` CLI, while installed commands such as
`bash`, `python`, `manim`, and `jupyter` remain directly accessible.

<!-- start docker usage -->

## Render and export a portable presentation

Only Docker and a scene file are required on the host. For example, save this as
`slides.py` in an otherwise empty directory:

```python
from manim import BLUE, Circle, Create, Dot, MoveAlongPath
from manim_slides import Slide


class Demo(Slide):
    def construct(self):
        circle = Circle(color=BLUE)
        dot = Dot()
        self.play(Create(circle))
        self.next_slide()
        self.play(MoveAlongPath(dot, circle), run_time=2)
```

Pull the published image once:

```console
docker pull ghcr.io/jeertmans/manim-slides:latest
```

From PowerShell on Windows, render the scene and create a self-contained HTML
presentation in the current directory:

```powershell
$image = "ghcr.io/jeertmans/manim-slides:latest"
$mount = "type=bind,source=$PWD,target=/workspace"
docker run --rm --mount $mount $image render -qm slides.py Demo
docker run --rm --mount $mount $image convert Demo demo.html --to=html-player --one-file
```

From Bash or Zsh on macOS and Linux, use the same container commands:

```bash
image="ghcr.io/jeertmans/manim-slides:latest"
mount="type=bind,source=$PWD,target=/workspace"
docker run --rm --mount "$mount" "$image" render -qm slides.py Demo
docker run --rm --mount "$mount" "$image" \
  convert Demo demo.html --to=html-player --one-file
```

The render step writes its reusable `media` and `slides` directories to the
mounted project. The conversion step writes `demo.html` beside `slides.py`. The
HTML file contains the player and all generated media, opens directly through
`file://`, and does not need Docker or network access when presented.

On Linux, use the host user and group IDs if the default container user cannot
write to the bind mount:

```bash
docker run --rm --user "$(id -u):$(id -g)" --mount "$mount" "$image" \
  render -qm slides.py Demo
```

After the image has been pulled, `--network none` can be added to either
`docker run` command for network-isolated rendering and conversion.

Containerized rendering does not support Manim preview flags such as `-p`, or the
desktop-only `present` and `wizard` commands. The portable HTML output is intended
to be opened on the host instead.

<!-- end docker usage -->

## Build the image from source

From the repository root:

```console
docker build --tag manim-slides:local --file docker/Dockerfile .
```

Replace the published image name in the commands above with
`manim-slides:local`.

The build context must be the repository root because the image installs the
checked-out Manim Slides package and copies files from `docker/`.

## Run another installed command

The entrypoint passes installed executables through unchanged. For example:

```console
docker run --rm --interactive --tty --mount "type=bind,source=$PWD,target=/workspace" ghcr.io/jeertmans/manim-slides:latest bash
```

An explicit `manim-slides` command also works and bypasses the entrypoint's
automatic offline version-check suppression.
