.PHONY: deps lint test all

all: deps lint test
	@echo "Secuencia completa ejecutada"

deps:
	@echo "Instalando dependencias..."
	pip install --upgrade pip
	pip install -r requirements.txt

lint:
	@echo "Ejecutando linters..."
	flake8 src/
	flake8 tests/

test:
	@echo "Ejecutando tests..."
	pytest -v tests/