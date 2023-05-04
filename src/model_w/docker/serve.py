from os import getenv
from pathlib import Path

from .config import Config
from .exceptions import UserException
from .output import Printer


def detect_multiprocessing_support() -> bool:
    """
    Some environments, like DigitalOcean's App Platform, do not support the
    multiprocessing module. This function detects if we're running in such an
    environment.
    """

    try:
        import multiprocessing

        with multiprocessing.Pool(1):
            pass
    except OSError as e:
        if e.errno == 38:
            return False
        else:
            raise
    else:
        return True


def serve_api_default(config: Config, path: Path) -> None:
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


def serve_api_celery(config: Config, path: Path) -> None:
    """
    Spins up the Celery worker

    Parameters
    ----------
    config
        Component config
    path
        Root of the component
    """

    printer = Printer.instance()

    pool = "prefork" if detect_multiprocessing_support() else "threads"

    printer.chapter("Serving Celery worker")
    printer.handover(
        "Running Celery worker",
        path,
        [
            "poetry",
            "run",
            *["python", "-m", "celery"],
            *["-A", config.project.celery],
            *["-c", "10"],
            *["-P", pool],
            "worker",
            "--loglevel=INFO",
        ],
    )


def serve_api_beat(config: Config, path: Path) -> None:
    """
    Spins up the Celery beat

    Parameters
    ----------
    config
        Component config
    path
        Root of the component
    """

    printer = Printer.instance()

    printer.chapter("Serving Celery beat")
    printer.handover(
        "Running Celery beat",
        path,
        [
            "poetry",
            "run",
            *["python", "-m", "celery"],
            *["-A", config.project.celery],
            "beat",
            "--loglevel=INFO",
        ],
    )


def serve_api(config: Config, path: Path, variant: str) -> None:
    """
    Spins up the right server for the API project

    Parameters
    ----------
    config
        Component config
    path
        Root of the component
    variant
        Variant of the component (server, celery, beat, etc)
    """

    if variant == "default":
        return serve_api_default(config, path)
    elif variant == "celery":
        return serve_api_celery(config, path)
    elif variant == "beat":
        return serve_api_beat(config, path)
    else:
        raise UserException(f"Unknown variant: {variant}")


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

    printer.env_patch.update({"HOST": "0.0.0.0", "PORT": f"{port}"})
    printer.handover(
        "Running Nuxt server",
        path,
        ["node", ".output/server/index.mjs"],
    )


def serve(config: Config, path: Path, variant: str) -> None:
    """
    Spins up the right server for the project

    Parameters
    ----------
    config
        Component config
    path
        Root of the component
    variant
        Variant of the component (server, celery, beat, etc)
    """

    printer = Printer.instance()
    printer.chapter(f"Serving {config.project.name}")
    printer.doing(f"Detected project type: {config.project.component}")

    if config.project.component == "api":
        return serve_api(config, path, variant)
    elif config.project.component == "front":
        return serve_front(path)
    else:
        raise UserException(f"Unknown component: {config.project.component}")
