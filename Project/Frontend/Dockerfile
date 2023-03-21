FROM python:3.10

###################### Add dependencies of different DB conectors if needed and install poetry ######################
RUN apt-get update && \ 
    apt-get install -y curl && \
    python -m pip install --upgrade pip && \
    curl -sSL https://install.python-poetry.org | python3 - --version "$APP_POETRY_VERSION"

###################### Add local path ###################### 
ENV PATH=/root/.local/bin:$PATH

###################### Set workdir in docker container and copy files over ###################### 
WORKDIR /frontend
COPY pyproject.toml ./

###################### Configure poetry and install desired packages ######################
RUN poetry config virtualenvs.in-project true --local && \
    poetry install --only main

###################### Copy python files over ######################
COPY . /frontend