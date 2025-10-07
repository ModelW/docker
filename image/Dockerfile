#                                ,,           ,,
#`7MMM.     ,MMF'              `7MM         `7MM      `7MMF'     A     `7MF'
#  MMMb    dPMM                  MM           MM        `MA     ,MA     ,V
#  M YM   ,M MM  ,pW"Wq.    ,M""bMM  .gP"Ya   MM         VM:   ,VVM:   ,V
#  M  Mb  M' MM 6W'   `Wb ,AP    MM ,M'   Yb  MM          MM.  M' MM.  M'
#  M  YM.P'  MM 8M     M8 8MI    MM 8M""""""  MM          `MM A'  `MM A'
#  M  `YM'   MM YA.   ,A9 `Mb    MM YM.    ,  MM           :MM;    :MM;
#.JML. `'  .JMML.`Ybmd9'   `Wbmd"MML.`Mbmmd'.JMML.          VF      VF

ARG DEBIAN_VERSION=trixie
ARG NODE_VERSION=22.x
ARG PYTHON_VERSION=3.13
ARG POSTGRESQL_VERSION=15

#   ____       _     _
#  |  _ \  ___| |__ (_) __ _ _ __
#  | | | |/ _ \ '_ \| |/ _` | '_ \
#  | |_| |  __/ |_) | | (_| | | | |
#  |____/ \___|_.__/|_|\__,_|_| |_|
#  | |__   __ _ ___  ___  (_)_ __ ___   __ _  __ _  ___
#  | '_ \ / _` / __|/ _ \ | | '_ ` _ \ / _` |/ _` |/ _ \
#  | |_) | (_| \__ \  __/ | | | | | | | (_| | (_| |  __/
#  |_.__/ \__,_|___/\___| |_|_| |_| |_|\__,_|\__, |\___|
#                                            |___/

FROM debian:${DEBIAN_VERSION}-slim AS debian-base
ARG DEBIAN_VERSION

ADD https://www.debian.org/security/dsa /var/cache/debian-cve-check/dsa

RUN apt-get update && apt-get install -y debootstrap

RUN mkdir /rootfs

RUN debootstrap --arch=amd64 $DEBIAN_VERSION /rootfs http://deb.debian.org/debian


#  ____        _ _     _   _
# | __ ) _   _(_) | __| | | | __ _ _   _  ___ _ __ ___
# |  _ \| | | | | |/ _` | | |/ _` | | | |/ _ \ '__/ __|
# | |_) | |_| | | | (_| | | | (_| | |_| |  __/ |  \__ \
# |____/ \__,_|_|_|\__,_| |_|\__,_|\__, |\___|_|  |___/
#                                  |___/

FROM scratch AS debian-model-w
ARG PYTHON_VERSION
ARG NODE_VERSION
ARG POSTGRESQL_VERSION


# ---[ Getting base OS ]---

COPY --from=debian-base /rootfs /

ENV DEBIAN_FRONTEND=noninteractive


# ---[ Basic system setup ]---

RUN apt-get update  \
    && apt-get install -y curl ca-certificates gnupg apt-transport-https lsb-release \
    && apt-get install -y sudo


# ---[ Update apt sources to new format ]---

RUN rm -f /etc/apt/sources.list && \
    mkdir -p /etc/apt/sources.list.d && \
    cat > /etc/apt/sources.list.d/debian.sources <<EOF
Types: deb
URIs: https://deb.debian.org/debian
Suites: trixie trixie-updates
Components: main non-free-firmware
Enabled: yes
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

Types: deb
URIs: https://security.debian.org/debian-security
Suites: trixie-security
Components: main non-free-firmware
Enabled: yes
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
EOF

RUN apt-get update


# ---[ Code user/folder ]---

RUN mkdir /code \
    && useradd -d /code -s /bin/bash user \
    && chown -R user:user /code

RUN echo "user ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/model-w \
    && chmod 0440 /etc/sudoers.d/model-w


# ---[ PostgreSQL ]---

RUN apt-get install -y postgresql-common \
    && /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y \
    && apt-get update \
    && apt-get install -y postgresql-client-$POSTGRESQL_VERSION


# ---[ Node ]---

RUN curl -fsSL https://deb.nodesource.com/setup_$NODE_VERSION | sh \
    && apt-get install -y nodejs

RUN curl -fsSL https://get.pnpm.io/install.sh | env SHELL=bash PNPM_HOME=/opt/pnpm bash - \
    && ln -s /opt/pnpm/.tools/pnpm-exe/*/pnpm /usr/local/bin/pnpm \
    && ln -s /opt/pnpm/.tools/pnpm-exe/*/pnpx /usr/local/bin/pnpx


# ---[ Python ]---

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get install -y \
    # Common project dependencies \
    libpcre2-dev \
    media-types \
    libpq-dev \
    gdal-bin \
    gdal-data \
    # Things required to build Pillow \
    libtiff5-dev  \
    libjpeg-dev  \
    libopenjp2-7-dev  \
    zlib1g-dev \
    libfreetype6-dev  \
    liblcms2-dev  \
    libwebp-dev  \
    tcl8.6-dev  \
    tk8.6-dev  \
    libharfbuzz-dev  \
    libfribidi-dev  \
    libxcb1-dev \
    # Things required to use Weasyprint \
    libpango-1.0-0 \
    libpangoft2-1.0-0

RUN uv python install -i /opt/python -r ${PYTHON_VERSION} \
    && uv venv -p /opt/python/cpython-*/bin/python /opt/python/global \
    && ln -s /opt/python/global/bin/python3 /usr/local/bin/python${PYTHON_VERSION} \
    && ln -s /opt/python/global/bin/python3 /usr/local/bin/python3 \
    && ln -s /opt/python/global/bin/python3 /usr/local/bin/python

RUN uv pip install -p /opt/python/global/bin/python3 poetry \
    && ln -s /opt/python/global/bin/poetry /usr/local/bin/poetry


# ---[ Model W ] ---

ARG MODEL_W_PIP_EXTRA=""

RUN uv pip install -p /opt/python/global/bin/python3 --no-cache-dir $MODEL_W_PIP_EXTRA 'modelw-docker==2025.7.0' \
    && ln -s /opt/python/global/bin/modelw-docker /usr/local/bin/modelw-docker


# ---[ Making sure all is upgraded ]---

RUN apt-get update && apt-get upgrade -y


# ---[ Cleanup ]---

RUN rm -fr \
    /var/log/alternatives.log \
    /var/log/apt/history.log \
    /var/log/apt/term.log \
    /var/log/bootstrap.log \
    /var/log/dpkg.log \
    /var/cache/man \
    /var/cache/ldconfig/aux-cache \
    /etc/machine-id \
    /var/cache/apt


#  _____ _       _     _
# |  ___| | __ _| |_  | | __ _ _   _  ___ _ __ ___
# | |_  | |/ _` | __| | |/ _` | | | |/ _ \ '__/ __|
# |  _| | | (_| | |_  | | (_| | |_| |  __/ |  \__ \
# |_|   |_|\__,_|\__| |_|\__,_|\__, |\___|_|  |___/
#                              |___/

FROM scratch

COPY --from=debian-model-w / /

WORKDIR /code

USER user

CMD ["/bin/bash"]
