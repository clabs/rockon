FROM python:3.14-trixie AS base

######################################### [build] ########################

FROM base AS build

COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/

ENV LC_ALL=C.UTF-8
ENV DOCKER_UID=1000
ENV PATH=/app/.venv/bin:/root/.local/bin:$PATH
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gettext \
        locales \
        sass \
        sudo && \
    dpkg-reconfigure locales && \
      locale-gen C.UTF-8 && \
      /usr/sbin/update-locale LANG=C.UTF-8 && \
    useradd -u $DOCKER_UID -ms /bin/bash -d /app appuser

WORKDIR /app
COPY pyproject.toml uv.lock /app/

RUN uv sync --frozen --no-install-project
COPY src /app/

RUN export DJANGO_SECRET_KEY=unused-but-must-be-present && \
    python3 /app/manage.py collectstatic --noinput && \
    python3 /app/manage.py compress && \
    python3 /app/manage.py compilemessages && \
    unset DJANGO_SECRET_KEY

######################################### [app] ########################

FROM base AS app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LC_ALL=C.UTF-8
ENV DJANGO_SETTINGS_MODULE=rockon.settings
ENV DOCKER_UID=1000
ENV PATH=/app/.venv/bin:/root/.local/bin:$PATH

ARG BUILD_DATE
ARG GITHUB_SHA
ENV BUILD_DATE=$BUILD_DATE
ENV GITHUB_SHA=$GITHUB_SHA

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        rsync \
        vim \
        sudo \
        ffmpeg \
        sass \
        libpng-dev libjpeg-dev libtiff-dev imagemagick ghostscript && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /run/rockon /static_files && \
    chown -R $DOCKER_UID:$DOCKER_UID /run/rockon /static_files && \
    useradd -u $DOCKER_UID -ms /bin/bash -d /app appuser

COPY docker/entrypoint.sh /usr/local/bin/entrypoint

COPY --from=build --chown=appuser /app /app

RUN chmod +x /usr/local/bin/entrypoint

WORKDIR /app

USER appuser

ENTRYPOINT ["/usr/local/bin/entrypoint"]
CMD [""]
