start:
	docker-compose up --build

restart:
	docker-compose down
	docker-compose up --build
