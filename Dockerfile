# Build the application in the `/app` directory.

# Use the official uv image with Python 3.13 on Debian Bookworm (slim variant).
# This image includes both Python and uv pre-installed.
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#available-images
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder
# Disable Python downloads, because use the system interpreter If 
# using a managed Python version, it needs to be copied from the 
# build image into the final image; See `standalone.Dockerfile`

LABEL org.opencontainers.image.title="Job Tracker"
LABEL org.opencontainers.image.description="Production-ready Job Tracker application"
LABEL org.opencontainers.image.url="https://github.com/alex-polo/job-tracker"
LABEL org.opencontainers.image.source="https://github.com/alex-polo/job-tracker"
LABEL org.opencontainers.image.authors="polonnikov.alexander@gmail.com"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.vendor="apolo, Inc"

# Prevent uv from downloading Python (the base image already provides it).
ENV UV_PYTHON_DOWNLOADS=0

# Disable Python output buffering to ensure logs appear immediately 
# in container logs.
ENV PYTHONUNBUFFERED=1

# Caching
# Use 'copy' link mode to avoid hard-linking issues between cache and target filesystems.
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Compiling Python source files to bytecode is typically desirable for production images
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# Use `/app` as the working directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy the entire project source into the image.
# Ensure `.venv` is excluded via `.dockerignore` to avoid platform conflicts.
COPY . /app

# Intermediate layers
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --no-dev


FROM python:3.14-slim-bookworm

# Copy the application from the builder
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uvx /usr/bin/

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Use `/app` as the working directory
WORKDIR /app

# Copy the application from the builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Install dependencies (Playwright dependencies already included in the base image)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked


# Install Playwright browser (must be done as root before switching to nonroot)
#RUN apt-get update && apt-get install -y --no-install-recommends \
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Switch to nonroot user
USER nonroot

RUN playwright install chromium

# Prestart script
RUN chmod +x ./scripts/prestart.sh
ENTRYPOINT ["./scripts/prestart.sh"]