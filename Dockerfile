# Use a uv Python image as a base
# NOTE: PyArrow (a dependency of streamlit) doesn't provide pre-built wheels for alpine
# and has complex dependencies for building from source, so we use a bookworm base image instead
# https://github.com/apache/arrow/issues/39846#issuecomment-1916269760
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set the working directory in the container
WORKDIR /app

# Copy just the files relevant to syncing to leverage the Docker cache
COPY uv.lock pyproject.toml .python-version /app/

# Install dependencies
RUN uv sync --locked

# Copy the rest of current directory contents across
# Note that importantly the .venv directory is excluded in the .dockerignore file
COPY . /app

# Expose the port that Streamlit runs on
EXPOSE 8501

# Add a healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Command to run the Streamlit app
ENTRYPOINT ["uv", "run", "streamlit", "run", "streamlit_app.py", "--server.port=8501"]