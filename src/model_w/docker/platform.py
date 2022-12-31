from psutil import disk_partitions


def in_docker():
    """
    Checks if we are running in a Docker container (well, not 100% sure but
    let's say it's a good enough guess).

    Notes
    -----
    We assume here that if the root partition is an overlay filesystem, we are
    running in a Docker container. This seems reasonable as few people would
    run their desktop on an overlay filesystem while this is the base of
    Docker.
    """

    for partition in disk_partitions(all=True):
        if partition.mountpoint == "/":
            return partition.fstype == "overlay"

    return False
