APP_NAME = heritage

docker-build:
	docker build --tag $(APP_NAME):latest .

docker-run:
	docker run --env-file .env  $(APP_NAME):latest

docker-push:
	sudo docker image tag $(APP_NAME) cut4cut/$(APP_NAME):1.0
	sudo docker image push cut4cut/$(APP_NAME):1.0 

run:
	poetry run python3 -m $(APP_NAME)