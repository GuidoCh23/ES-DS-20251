import os
import zlib
import json
import heapq
from collections import defaultdict, deque


class GitGraphAnalyzer:
    """
    Clase Analizador del grafo de commits de Git
    """

    def __init__(self, repo_path: str = "."):
        # Rutas principales del repositorio
        self.repo_path = repo_path
        self.git_dir = os.path.join(repo_path, ".git")
        self.objects_dir = os.path.join(self.git_dir, "objects")

        # Estructuras de datos principales
        self.commits = {}  # SHA => info del commit
        self.graph = defaultdict(list)  # SHA => lista de padres
        self.reverse_graph = defaultdict(list)  # SHA => lista de hijos

    def read_object(self, sha: str):
        """
        Lee y descomprime un objeto Git desde .git/objects
        """
        # Los objetos se guardan como .git/objects/xx/yyyy
        # donde xx son los primeros 2 chars del SHA
        obj_path = os.path.join(self.objects_dir, sha[:2], sha[2:])
        if not os.path.exists(obj_path):
            raise FileNotFoundError(f"Objeto {sha} no encontrado")

        # Leer archivo comprimido
        with open(obj_path, 'rb') as f:
            compressed_data = f.read()

        # Descomprimir con zlib
        decompressed_data = zlib.decompress(compressed_data)

        # Separar header del contenido
        header_end = decompressed_data.find(b'\0')
        header = decompressed_data[:header_end].decode('ascii')
        content = decompressed_data[header_end + 1:]

        obj_type = header.split()[0]  # Tipo: 'commit', 'tree', 'blob', etc.
        return obj_type, content

    def parse_commit(self, content: bytes):
        """
        Parsea el contenido de un objeto commit
        """
        lines = content.decode('utf-8').split('\n')
        commit_data = {
            'parents': [],  # Lista de SHAs de commits padre
            'tree': '',
            'author': '',
            'committer': '',
            'message': ''
        }

        # Parsear lineas del commit
        message_start = False
        for line in lines:
            if message_start:
                commit_data['message'] += line + '\n'
            elif line.startswith('tree '):
                commit_data['tree'] = line[5:]
            elif line.startswith('parent '):
                # Cada linea "parent" es un commit padre
                commit_data['parents'].append(line[7:])
            elif line.startswith('author '):
                commit_data['author'] = line[7:]
            elif line.startswith('committer '):
                commit_data['committer'] = line[10:]
            elif line == '':
                # Linea vacia marca el inicio del mensaje
                message_start = True

        return commit_data

    def get_head_sha(self) -> str:
        """
        Obtiene el SHA del commit actual (HEAD)
        """
        head_path = os.path.join(self.git_dir, "HEAD")
        with open(head_path, 'r') as f:
            head_content = f.read().strip()

        # HEAD puede ser una referencia a una rama o un SHA directo
        if head_content.startswith('ref: '):
            # Es una referencia
            ref_path = os.path.join(self.git_dir, head_content[5:])
            with open(ref_path, 'r') as f:
                return f.read().strip()
        else:
            # Es un SHA directo
            return head_content

    def discover_all_commits(self):
        """
        Descubre todos los commits explorando .git/objects
        """
        # Recorrer todos los subdirectorios de objetos
        for subdir in os.listdir(self.objects_dir):
            if len(subdir) == 2 and subdir not in ['info', 'pack']:
                subdir_path = os.path.join(self.objects_dir, subdir)
                if os.path.isdir(subdir_path):
                    # Cada archivo en el subdirectorio es un objeto Git
                    for obj_file in os.listdir(subdir_path):
                        sha = subdir + obj_file  # Reconstruir SHA completo
                        try:
                            obj_type, content = self.read_object(sha)
                            # Solo nos interesan los commits
                            if obj_type == 'commit':
                                commit_data = self.parse_commit(content)
                                self.commits[sha] = commit_data
                        except:
                            continue

    def build_graph(self):
        """
        Construye el DAG desde las relaciones padre-hijo de commits
        """
        for sha, commit_data in self.commits.items():
            # Para cada commit, conectar con sus padres
            for parent_sha in commit_data['parents']:
                if parent_sha in self.commits:
                    # Grafo normal: commit => padres
                    self.graph[sha].append(parent_sha)
                    # Grafo inverso: padre => hijos (para calcular indegree)
                    self.reverse_graph[parent_sha].append(sha)

    def calculate_branch_density(self) -> float:
        """
        Calcula la densidad de ramas según el README
        """
        head_sha = self.get_head_sha()
        if head_sha not in self.commits:
            return 0.0

        # BFS para calcular distancias desde HEAD
        distances = {}
        queue = deque([(head_sha, 0)])
        distances[head_sha] = 0

        while queue:
            current_sha, dist = queue.popleft()
            # Visitar todos los padres
            for parent_sha in self.graph.get(current_sha, []):
                if parent_sha not in distances:
                    distances[parent_sha] = dist + 1
                    queue.append((parent_sha, dist + 1))

        # Agrupar commits por nivel de profundidad
        levels = defaultdict(int)
        for sha, dist in distances.items():
            levels[dist] += 1

        if not levels:
            return 0.0

        # Fórmula: para cada nivel i
        # calcular nodes_i / i, sumar y dividir por total de niveles
        density_sum = 0.0
        for level, count in levels.items():
            if level > 0:  # No dividir por 0 en el nivel HEAD
                density_sum += count / level

        return density_sum / len(levels) if levels else 0.0

    def calculate_merge_debt(self, sha: str) -> int:
        """
        Calcula la deuda de merge: 1 si es merge (>1 padre), 0 si no
        """
        return 1 if len(self.commits[sha]['parents']) > 1 else 0

    def find_critical_path(self):
        """
        Encuentra el camino critico usando Dijkstra para minimizar deuda de merges
        """
        head_sha = self.get_head_sha()
        if head_sha not in self.commits:
            return []

        # Dijkstra, encontrar camino con menor deuda de merges
        distances = {sha: float('inf') for sha in self.commits}
        distances[head_sha] = 0
        previous = {}
        heap = [(0, head_sha)]

        while heap:
            current_dist, current_sha = heapq.heappop(heap)

            if current_dist > distances[current_sha]:
                continue

            # Explorar padres
            for parent_sha in self.graph.get(current_sha, []):
                merge_debt = self.calculate_merge_debt(current_sha)
                new_dist = current_dist + merge_debt

                if new_dist < distances[parent_sha]:
                    distances[parent_sha] = new_dist
                    previous[parent_sha] = current_sha
                    heapq.heappush(heap, (new_dist, parent_sha))

        # Buscar el commit raiz con menor distancia
        target_sha = None
        min_dist = float('inf')
        for sha in self.commits:
            # Commits sin padres son raices
            if distances[sha] < min_dist and not self.graph.get(sha, []):
                min_dist = distances[sha]
                target_sha = sha

        if target_sha is None:
            return []

        # Reconstruir camino
        path = []
        current = target_sha
        while current is not None:
            path.append(current)
            current = previous.get(current)

        return path[::-1]  # Invertir para ir de HEAD a raiz

    def find_bottleneck_commits(self, k: int = 5):
        """
        Encuentra los k commits con mayor indegree (>2)
        """
        indegrees = []
        for sha in self.commits:
            # Indegree = cantidad de hijos
            indegree = len(self.reverse_graph.get(sha, []))
            if indegree > 2:  # Solo bottlenecks significativos
                indegrees.append((indegree, sha))

        # Ordenar por indegree descendente y tomar top-k
        indegrees.sort(reverse=True)
        return [sha for _, sha in indegrees[:k]]

    def generate_analysis(self):
        """
        Genera el análisis completo del repositorio
        """
        # Descubrir todos los commits
        self.discover_all_commits()
        # Construir el grafo
        self.build_graph()

        # Calcular metricas
        density = self.calculate_branch_density()
        critical_path = self.find_critical_path()
        bottlenecks = self.find_bottleneck_commits()

        return {
            'density': density,
            'critical_path': critical_path,
            'bottlenecks': bottlenecks
        }

    def generate_dot_file(self, filename: str = "git_graph.dot"):
        """
        Genera archivo DOT para visualizacion con Graphviz
        """
        with open(filename, 'w') as f:
            f.write("digraph GitGraph {\n")
            f.write("  rankdir=TB;\n")  # Top-Bottom
            f.write("  node [shape=circle, style=filled];\n")

            # Escribir nodos (commits)
            for sha in self.commits:
                label = sha[:7]  # Solo primeros 7 caracteres del SHA
                if len(self.commits[sha]['parents']) > 1:
                    # Merges en rojo
                    f.write(f'  "{sha}" [label="{label}", fillcolor=red];\n')
                else:
                    # Commits normales en azul
                    f.write(f'  "{sha}" [label="{label}", fillcolor=lightblue];\n')

            # Escribir aristas (relaciones padre-hijo)
            for sha, parents in self.graph.items():
                for parent in parents:
                    f.write(f'  "{sha}" -> "{parent}";\n')

            f.write("}\n")


def main():
    print("Analizando repositorio Git...")

    # Crear analizador y ejecutamos
    analyzer = GitGraphAnalyzer()
    analysis = analyzer.generate_analysis()

    # Guardamos resultados
    with open('git_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)

    analyzer.generate_dot_file('git_graph.dot')

    # Mostramos resultados
    print(f"Analisis completado:")
    print(f"  Densidad de ramas: {analysis['density']:.4f}")
    print(f"  Camino critico: {len(analysis['critical_path'])} commits")
    print(f"  Bottlenecks encontrados: {len(analysis['bottlenecks'])}")


if __name__ == "__main__":
    main()
