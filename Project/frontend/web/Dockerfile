# Build argument
ARG API_PYTHON_VERSION=3.11-alpine

## Step 1: configure base
##=============================================================================
FROM python:${API_PYTHON_VERSION} as base
# PYTHONUNBUFFERED=1: stdout and stderr streams are sent straight to terminal (e.g. your container log) without
# being first buffered #and that you can see the output of your application in real time.
# PYTHONHASHSEED: https://docs.python.org/3/using/cmdline.html#envvar-PYTHONHASHSEED
# PYTHONFAULTHANDLER: https://docs.python.org/3/using/cmdline.html#envvar-PYTHONFAULTHANDLER
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1
# Alpine: add non root user and group
RUN addgroup -g 1000 apprunner && \
    adduser -u 1000 -G apprunner -h /home/apprunner -D apprunner && \
    mkdir /app && chown -R apprunner:apprunner /app
# Install required dependencies to make curl available
RUN apk add --no-cache curl
# Set the working directory in the container
WORKDIR /app

  
## Step 2:
##=============================================================================
FROM base as builder
# Build argument
ARG API_POETRY_VERSION=1.8.0
# Set environment variables
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=${API_POETRY_VERSION}
#Since you use non-root user, poetry will be installed under /home/apprunner/.local/bin/poetry
#To make sure we can use it -> lets add that into path.
ENV PATH="/home/apprunner/.local/bin:${PATH}"
#Install poetry using pip
RUN pip install "poetry==${API_POETRY_VERSION}"
COPY pyproject.toml README.md ./
#Copy our actual package source code then build the package
COPY recognition_web ./recognition_web
# Install numpy sepparately because no PEP517 support and lock the dependencies
RUN poetry lock 
# Install the dependencies
RUN poetry config virtualenvs.path {project-dir}/.venv && \
    poetry config virtualenvs.in-project true && \
#    poetry config --list && \
    poetry install --only=main --no-root --no-interaction --no-ansi && \
    poetry build


## Step 3:
##=============================================================================
FROM base as final
#Copy the dependencies and actual distribution package
COPY --from=builder /app/.venv ./.venv
COPY --from=builder /app/dist .
#Here -> we are comying some environmental config file. Your
#user-case may not need this. If you need to environmentalize your docker images -> 
#then make sure to include some ENV_NAME argument and .env file into your container build process
#COPY stack/env-${ENV_NAME}/.env .
RUN chown -R apprunner:apprunner /app
#Switch to this user 
USER apprunner
#Install our distribution package (we built python wheel in a previous step)
RUN ./.venv/bin/pip install *.whl
#This will initialize the python's virtual env (so we don't need to call source .venv/bin/activate)
ENV PATH="/app/.venv/bin:${PATH}"
ENV VIRTUAL_ENV="/app/.venv"
# Invoke the application
CMD ["python", "/app/.venv/lib/python3.11/site-packages/recognition_web/main.py"]