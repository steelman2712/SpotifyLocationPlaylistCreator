start:
	docker-compose up --build

restart:
	docker-compose down
	docker-compose up --build

lint:
	black .
	flake8