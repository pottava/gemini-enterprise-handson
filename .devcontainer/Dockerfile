FROM python:3.13-slim

# Install related packages
RUN apt-get update && apt-get install -y build-essential vim curl wget jq git gnupg lsb-release
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PATH "/.venv/bin:${PATH}"

# gcloud
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
    | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
RUN apt-get update && apt-get install -y google-cloud-cli

# Node.js and package managers
ENV NPM_VERSION=11.16.0 \
    PNPM_VERSION=11.5.0
RUN curl -fsSL https://deb.nodesource.com/setup_current.x | bash - \
    && apt-get install -y nodejs
RUN --mount=type=cache,target=/root/.npm \
    npm install -g "npm@${NPM_VERSION}" --force && \
    npm install -g "pnpm@${PNPM_VERSION}" && \
    npm cache clean --force
# RUN npx --yes skills add google/skills

# Environment variables
ENV PYTHONUNBUFFERED 1

# Resolve dependencies for apps
COPY pyproject.toml .
COPY uv.lock .
RUN uv sync

# Working directory
WORKDIR /workspace
