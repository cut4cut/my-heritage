APP_NAME = heritage

docker-build:
	docker build --tag $(APP_NAME):latest .

docker-run:
	docker run --env-file .env  $(APP_NAME):latest

run:
	poetry run python3 -m $(APP_NAME)