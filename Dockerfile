FROM python:3.10-slim-buster

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip3 install poetry

RUN poetry --without=dev install

COPY . .

CMD ["python3", "-m" , " heritage "]