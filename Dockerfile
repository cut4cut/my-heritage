FROM python:3.10-bullseye

RUN mkdir /app
WORKDIR /app

RUN groupadd -r web && useradd -d /app -g web web \
    && chown web:web -R /app

RUN pip install "poetry==1.2.2"

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --without dev --output /app/requirements.txt

RUN pip install --upgrade pip setuptools wheel \ 
    && pip install --no-cache -r /app/requirements.txt

COPY ./heritage ./heritage
RUN poetry build && pip install dist/*.whl

EXPOSE 8000

USER web

CMD python -m heritage
