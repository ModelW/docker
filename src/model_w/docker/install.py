from pathlib import Path

from .config import Config
from .exceptions import UserException
from .output import Printer


def install_apt(config: Config) -> None:
    """
    Installs apt packages and repos if required
    """

    if not config.apt.packages:
        return

    printer = Printer.instance()
    printer.chapter("Installing apt packages")

    for name, spec in config.apt.repos.items():
        printer.pipe(
            f"Getting GPG key for {name}",
            ".",
            args_left=["curl", "-s", spec.key.url],
            args_right=[
                "gpg",
                "--dearmor",
                "--output",
                f"/etc/apt/trusted.gpg.d/{name}.gpg",
            ],
            become_right="root",
        )

        printer.pipe(
            f"Writing sources.list.d entry for {name}",
            ".",
            args_left=["echo", spec.source],
            args_right=["cp", "/dev/stdin", f"/etc/apt/sources.list.d/{name}.list"],
            become_right="root",
        )

    printer.exec(
        "Fetching latest apt package lists",
        ".",
        ["apt-get", "update"],
        become="root",
    )
    printer.exec(
        "Installing apt dependencies",
        ".",
        [
            "apt-get",
            "install",
            "--yes",
            "--no-install-recommends",
            *[
                (f"{name}={version}" if version != "*" else name)
                for name, version in config.apt.packages.items()
            ],
        ],
        become="root",
    )
    printer.exec(
        "Removing useless packages",
        ".",
        ["apt-get", "autoremove", "--yes"],
        become="root",
    )
    printer.exec(
        "Cleaning up apt cache",
        ".",
        ["apt-get", "clean"],
        become="root",
    )
    printer.exec(
        "Removing apt lists",
        ".",
        ["rm", "-rf", "/var/lib/apt/lists"],
        become="root",
    )


def drop_root():
    """
    The base image gives us sudo rights in case we need them to complete the
    setup. At this stage we don't want them anymore so we drop the file that
    gave us those rights.
    """

    printer = Printer.instance()
    printer.chapter("Dropping root privileges")

    printer.exec(
        "Delete sudoers file",
        ".",
        ["rm", "-f", "/etc/sudoers.d/model-w"],
        become="root",
    )


def install_system(config: Config) -> None:
    """
    The "system" part of the install (language-independent)
    """

    install_apt(config)
    drop_root()


def install_api(config: Config, path: Path, dry_run: bool = True) -> None:
    """
    Basically just installing the venv with Poetry and cleaning the cache
    """

    printer = Printer.instance()

    install_system(config)

    printer.chapter("Installing python dependencies")

    for name, content in config.project.required_files.items():
        printer.doing(f"Writing {name}")

        if not dry_run:
            full_path = path / name
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, mode="w") as f:
                f.write(content)

    printer.exec(
        "Putting virtualenv in project",
        path,
        ["poetry", "config", "virtualenvs.in-project", "true"],
    )
    printer.exec(
        "Limiting to 10 concurrent downloads",
        path,
        ["poetry", "config", "installer.max-workers", "10"],
    )
    printer.exec(
        "Installing dependencies",
        path,
        ["poetry", "install", "--only", "main"],
    )
    cache_dir = (
        (
            printer.exec(
                "Getting cache directory",
                path,
                ["poetry", "config", "cache-dir"],
                return_stdout=True,
            )
            or b"/dry/run"
        )
        .decode("utf-8")
        .rstrip("\n")
    )
    printer.exec(
        "Clearing cache",
        path,
        ["rm", "-fr", f"{cache_dir}"],
    )


def install_front(config: Config, path: Path, dry_run: bool = True) -> None:
    """
    Install front dependencies with pnpm.

    We force "verify-deps-before-run" to false because pnpm defaults it to
    "install": before running a script (e.g. "pnpm run build" during the image
    build) pnpm checks whether node_modules is up to date and, if not, runs an
    install. We've just installed from the lockfile and we want the build to
    use exactly those locked dependencies; letting pnpm reinstall implicitly
    could resolve something different from what the lockfile guarantees, which
    is precisely what CI/CD must avoid.
    """

    printer = Printer.instance()

    install_system(config)

    printer.chapter("Installing node dependencies")

    printer.env_patch["BUILD_MODE"] = "true"

    npmrc = path / ".npmrc"
    key = "verify-deps-before-run"
    line = f"{key}=false"

    original = npmrc.read_text() if npmrc.exists() else ""
    kept = [
        raw
        for raw in original.splitlines()
        if raw.lstrip().startswith(("#", ";")) or raw.split("=", 1)[0].strip() != key
    ]
    content = "\n".join([*kept, line]) + "\n"

    if content == original:
        printer.doing(f"{key} already set to false in .npmrc")
    else:
        printer.doing(f"Setting {key}=false in .npmrc")

        if not dry_run:
            npmrc.write_text(content)

    printer.exec(
        "Installing dependencies",
        path,
        ["pnpm", "install", "--frozen-lockfile", "--ignore-scripts"],
    )


def install(config: Config, path: Path, dry_run: bool = True) -> None:
    """
    The installation process is what is going to create the virtual environment
    for the code to be able to run. As long as you don't change the project's
    requirements, this process shouldn't run again and stay in build cache.
    """

    printer = Printer.instance()
    printer.chapter(f"Installing {config.project.name}")
    printer.doing(f"Detected project type: {config.project.component}")

    if config.project.component == "api":
        return install_api(config, path, dry_run)
    elif config.project.component == "front":
        return install_front(config, path, dry_run)
    else:
        raise UserException(f"Unknown component: {config.project.component}")
