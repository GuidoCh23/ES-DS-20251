#!/bin/bash
echo "Ejecutando linter flake8 en src/"
flake8 src/

echo "Ejecutando pytest en tests/ con cobertura en src/"
if ! pytest --maxfail=1 --disable-warnings --cov=src --cov-report=xml | tee pytest_results.log; then
    exit 1
fi

if [ ! -f "coverage.xml" ]; then
    echo "Error: No se genero reporte de cobertura"
    exit 1
fi