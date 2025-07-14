# Examen Sustitutorio del curso de Desarrollo de Software del ciclo 20251
Nombre: Guido Anthony Chipana Calderon
Codigo: 20224128H

## Descripcion del examen 3
Crear una plataforma que simule una plataforma interna de analisis y ejecucion de tareas criticas donde:
- Se requiere extraer informacion profunda de la estructura del repositorio Git, mas alla de comandos de alto nivel como git log, trabajando directamente con los objetos internos para obtener metricas avanzadas como la densidad de ramas, caminos criticos, analisis de merges, etc.
- Se requiere diseñar un "mesh" de microservicios ligero que coordine flujos de trabajo entre 3 servicios independientes, aplicando un patron Mediator para centralizar la logica de enrutamiento, gestionar reintentos y controlar la presion de peticion sin aclopar los servicios entre si

## Requisitos
- Python 3.12+
- Bash 5.1+
- Docker 25+
- Minikube 1.30+
- kubectl 1.26+

## Instrucciones

### Configuración del Proyecto

#### Paso 1: Clonar o descargar el proyecto
Clonamos el repositorio con el siguiente comando

```bash
git clone https://github.com/GuidoCh23/ES-DS-20251.git
cd ES-DS-20251
```
#### Paso 2: Inicializar el proyecto
Inicializacion ejecutando el Makefile con el siguiente comando

```bash
make
```

o

```bash
make all
```

### Ejecutar el analizador de grafos de commit de Git
Ejecutando el siguiente comando

```bash
python3 src/git_graph.py
```

Salidas generadas:
- `git_analysis.json` - Metricas calculadas (densidad, camino critico, bottlenecks)
- `git_graph.dot` - Visualizacion del grafo en formato DOT

### Visualizacion del grafo
Ejecutando el siguiente comando, nos generara la imagen del grafo en png:

```bash
dot -Tpng git_graph.dot -o git_graph.png
```

### Ejecucion de mini-pipeline
Primero hay que darle permisos ejecutando el siguiente comando

```bash
chmod +x scripts/ci.sh
```

Y para ejecutar el bash, hay que ejecutar el siguiente comando

```bash
./scripts/ci.sh
```

