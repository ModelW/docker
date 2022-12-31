from os import getenv
from pathlib import Path

from .config import Config
from .exceptions import UserException
from .output import Printer


def serve_api(config: Config, path: Path) -> None:
    """
    Depending on if we're running gunicorn (for WSGI websites) or daphne
    (for ASGI websites), generate and run the appropriate command line.

    We bind on 0.0.0.0 because we need the flow to be accessible from outside
    the container.

    Parameters
    ----------
    config
        Component config
    path
        Root path of the component
    """

    printer = Printer.instance()

    printer.chapter("Serving Django")
    port = getenv("PORT", "8000")

    if config.project.server == "gunicorn":
        if not config.project.wsgi:
            raise UserException(
                "WSGI module not configured. Either set 'project.wsgi' in "
                "model-w.toml, either make sure you declare a package in "
                "pyproject.toml (and that you follow Model W conventions)"
            )

        printer.handover(
            f"Starting gunicorn (port {port})",
            path,
            [
                "poetry",
                "run",
                *["python", "-m", "gunicorn"],
                *["--bind", f"0.0.0.0:{port}"],
                *["--log-file", "-"],
                *["--worker-tmp-dir", "/dev/shm"],
                *["--threads", "10"],
                config.project.wsgi,
            ],
        )
    elif config.project.server == "daphne":
        if not config.project.asgi:
            raise UserException(
                "ASGI module not configured. Either set 'project.asgi' in "
                "model-w.toml, either make sure you declare a package in "
                "pyproject.toml (and that you follow Model W conventions)"
            )

        printer.handover(
            f"Starting daphne (port {port})",
            path,
            [
                "poetry",
                "run",
                *["python", "-m", "daphne"],
                *["--bind", f"0.0.0.0"],
                *["--port", f"{port}"],
                config.project.asgi,
            ],
        )
    else:
        raise UserException(f"Unknown server: {config.project.server}")


def serve_front(path: Path) -> None:
    """
    Simply start the Nuxt server.

    We bind on 0.0.0.0 because we need the flow to be accessible from outside
    the container.

    Parameters
    ----------
    path
        Root path of the component
    """

    printer = Printer.instance()

    printer.chapter("Serving Nuxt project")
    port = getenv("PORT", "3000")

    printer.handover(
        "Running Nuxt server",
        path,
        [
            *["npm", "run"],
            "start",
            "--",
            *["--hostname", "0.0.0.0"],
            *["--port", f"{port}"],
        ],
    )


def serve(config: Config, path: Path) -> None:
    """
    Spins up the right server for the project

    Parameters
    ----------
    config
        Component config
    path
        Root of the component
    """

    printer = Printer.instance()
    printer.chapter(f"Serving {config.project.name}")
    printer.doing(f"Detected project type: {config.project.component}")

    if config.project.component == "api":
        return serve_api(config, path)
    elif config.project.component == "front":
        return serve_front(path)
    else:
        raise UserException(f"Unknown component: {config.project.component}")
