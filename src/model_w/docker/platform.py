from psutil import disk_partitions


def in_docker():
    """
    Checks if we are running in a Docker container (well, not 100% sure but
    let's say it's a good enough guess).

    Notes
    -----
    There is no official way to check if we are running in a Docker container.
    What makes the most sense that I've found is that Docker will mount the
    DNS-related files from the host into the container. So we check if those
    files are mounted (no native system should have those mounted).

    Previously we checked if the root is an overlayfs, but that's not a good
    enough check because it's possible to run Docker with other backends
    like ZFS.
    """

    expected_mount_points = {"/etc/resolv.conf", "/etc/hosts", "/etc/hostname"}
    found_mount_points = set(x.mountpoint for x in disk_partitions(all=True))

    return expected_mount_points.issubset(found_mount_points)
