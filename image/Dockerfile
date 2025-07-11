FROM debian:bullseye-slim as debian-base

ADD https://www.debian.org/security/dsa /var/cache/debian-cve-check/dsa

RUN apt-get update && apt-get install -y debootstrap

RUN mkdir /rootfs

RUN debootstrap --arch=amd64 bullseye /rootfs http://deb.debian.org/debian

# ---

FROM scratch as debian-model-w

COPY --from=debian-base /rootfs /

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update  \
    && apt-get install -y curl ca-certificates gnupg apt-transport-https lsb-release \
    && curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor --output /etc/apt/trusted.gpg.d/apt.postgresql.org.gpg \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | sh

COPY ./sources.list /etc/apt/sources.list

RUN apt-get update  \
    && apt-get install -y \
    # Common project dependencies
    libpcre3 \
    libpcre3-dev \
    mime-support \
    postgresql-client \
    libpq-dev \
    gdal-bin \
    gdal-data \
    # Things required to build Python
    build-essential \
    gcc \
    g++ \
    make \
    libssl-dev  \
    zlib1g-dev \
    libbz2-dev  \
    libreadline-dev  \
    libsqlite3-dev  \
    llvm \
    libncursesw5-dev \
    xz-utils  \
    tk-dev  \
    libxml2-dev  \
    libxmlsec1-dev  \
    libffi-dev  \
    liblzma-dev \
    # Things required to build Pillow
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
    # NodeJS
    nodejs \
    # Things required to use Weasyprint
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    # Stuff to allow configuration afterwards
    sudo \
    && apt-get upgrade -y \
    && rm -fr \
    /var/log/alternatives.log \
    /var/log/apt/history.log \
    /var/log/apt/term.log \
    /var/log/bootstrap.log \
    /var/log/dpkg.log \
    /var/cache/man \
    /var/cache/ldconfig/aux-cache \
    /etc/machine-id \
    /var/cache/apt

ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8
ENV GPG_KEY 7169605F62C751356D054A26A821E680E5FA6305
ENV PYTHON_MAJOR_VERSION 3.13

COPY install_python.sh /tmp/install_python.sh

RUN chmod a+x /tmp/install_python.sh \
    && /tmp/install_python.sh \
    && rm -fr /tmp/install_python.sh

RUN curl -sSL https://install.python-poetry.org | env POETRY_HOME=/opt/poetry python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

ARG MODEL_W_PIP_EXTRA=""


RUN python -m venv /opt/model-w \
    && /opt/model-w/bin/python -m pip install --no-cache-dir $MODEL_W_PIP_EXTRA 'modelw-docker==2025.7.0' \
    && ln -s /opt/model-w/bin/modelw-docker /usr/local/bin/modelw-docker

RUN mkdir /code \
    && useradd -d /code -s /bin/bash user \
    && chown -R user:user /code

RUN echo "user ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/model-w \
    && chmod 0440 /etc/sudoers.d/model-w

# ---

FROM scratch

COPY --from=debian-model-w / /

WORKDIR /code

USER user

CMD ["/bin/bash"]
