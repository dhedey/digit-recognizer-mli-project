# Use a uv Python image as a base
# NOTE: PyArrow (a dependency of streamlit) doesn't provide pre-built wheels for alpine
# and has complex dependencies for building from source, so we use a bookworm base image instead
# https://github.com/apache/arrow/issues/39846#issuecomment-1916269760
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

#####################################################
# ================= APP CONTAINER ================= #
#####################################################
FROM base AS app

# Set the working directory in the container
WORKDIR /app

# Copy just the files relevant to syncing to leverage the Docker cache
COPY uv.lock pyproject.toml .python-version /app/
COPY packages/app/pyproject.toml /app/packages/app/pyproject.toml

# Install just the dependencies for the app package
RUN uv sync --frozen --no-dev --package app

# Expose the port that Streamlit runs on
EXPOSE 8501

# Add a healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Copy the rest of current directory contents across
# Note that importantly the .venv directory is excluded in the .dockerignore file
COPY . /app

# Command to run the Streamlit app
ENTRYPOINT ["uv", "run", "--package", "app", "streamlit", "run", "packages/app/src/app/streamlit_app.py", "--server.port=8501"]

#####################################################
# ================= API CONTAINER ================= #
#####################################################
FROM base AS model-api

# Set the working directory in the container
WORKDIR /app

# Expose the port that fast api runs on
EXPOSE 8000

# Add a healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8000/health

# Copy the code across
# Note that importantly the .venv directory is excluded in the .dockerignore file
# <SIDENOTE>
# Ideally we'd download the dependencies into a docker cache layer before adding the code,
# (e.g. via copying the pyproject.yml and lock files, then syncing first - like with the app container)
# but this errors now that I've added a workspace dependency on the model package, so we'll go back to this.
# </SIDENOTE>
COPY . /app

# Install just the dependencies for the model-api package
RUN uv sync --frozen --no-dev --package model-api

# Command to run the FastAPI app
ENTRYPOINT ["uv", "run", "--package", "model-api", "fastapi", "run", "packages/model-api/src/model_api/main.py"]

################################################
# ================= DATABASE ================= #
################################################
FROM postgres:17-bookworm AS postgres-db
COPY ./deployment/init_db.sql /docker-entrypoint-initdb.d/
