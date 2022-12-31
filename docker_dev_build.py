#!/usr/bin/env python
import shlex
import socket
import subprocess
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread


def get_ip():
    """
    Guesses the "public" IP of the current machine so that the Docker container
    can connect to it.
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)

    try:
        s.connect(("10.254.254.254", 1))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def server_run(server: HTTPServer):
    """
    We're running a custom package server in order to serve to the pip running
    in Docker the package that we've just built without having to publish it.

    Let's note that the Pypi repo protocol is to parse links to packages in a
    HTML page, so the default simple HTTP server does the job perfectly.

    The goal of this function is just to start the server in a parallel thread.

    Parameters
    ----------
    server
        Already created and listening
    """

    server.serve_forever()


def build_run(server: HTTPServer, process: subprocess.Popen):
    """
    Waits for the Docker process to complete and then shuts down the HTTP
    server. The server thread is polling for shutdown every 0.5s. In a
    nutshell, the signal for the whole thing to shutdown is when the Docker
    process is done (including if the user does CTRL+C, we'll just kill the
    Docker process and then this thread will pick it up and shutdown the HTTP
    server).

    Parameters
    ----------
    server
        HTTP server to kill in the end
    process
        Docker build process
    """

    try:
        process.wait()
    finally:
        server.shutdown()


def main():
    """
    Starting a HTTP server to serve the modelw-docker package and then starting
    a docker build process. Waiting for both to complete before dying.
    """

    server = HTTPServer(
        ("0.0.0.0", 0),
        partial(
            SimpleHTTPRequestHandler,
            directory=Path(__file__).parent / "repo",
        ),
    )

    ip = get_ip()
    port = server.server_address[1]
    url = f"http://{ip}:{port}"
    extra = f"--extra-index-url {url} --trusted-host {ip}"

    print(f"Server running at {url}")

    args = [
        "docker",
        "build",
        *["--build-arg", f"MODEL_W_PIP_EXTRA={extra}"],
        *["-t", "modelw-base-test"],
        ".",
    ]

    print(" ".join(shlex.quote(arg) for arg in args))

    p = subprocess.Popen(
        args=args,
        cwd=Path(__file__).parent / "image",
    )

    server_thread = Thread(target=server_run, args=(server,))
    build_thread = Thread(target=build_run, args=(server, p))

    server_thread.start()
    build_thread.start()

    try:
        server_thread.join()
        build_thread.join()
    except KeyboardInterrupt:
        p.kill()
    finally:
        return p.returncode


if __name__ == "__main__":
    main()
