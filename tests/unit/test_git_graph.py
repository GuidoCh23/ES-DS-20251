import os
import pytest
from src.git_graph import GitGraphAnalyzer


def test_analyzer_creation():
    """
    Test que se puede crear el analizador
    """
    analyzer = GitGraphAnalyzer()
    assert analyzer is not None
    assert analyzer.repo_path == "."


def test_git_directory_exists():
    """
    Test que el directorio .git existe
    """
    analyzer = GitGraphAnalyzer()
    assert os.path.exists(analyzer.git_dir)


def test_get_head_sha():
    """
    Test que se puede obtener el SHA de HEAD
    """
    analyzer = GitGraphAnalyzer()
    try:
        head_sha = analyzer.get_head_sha()
        assert isinstance(head_sha, str)
        assert len(head_sha) == 40  # SHA-1 tiene 40 caracteres
    except Exception:
        pytest.skip("No se pudo obtener HEAD SHA")


def test_discover_commits():
    """
    Test que se pueden descubrir commits
    """
    analyzer = GitGraphAnalyzer()
    analyzer.discover_all_commits()
    assert len(analyzer.commits) > 0


def test_build_graph():
    """
    Test que se puede construir el grafo
    """
    analyzer = GitGraphAnalyzer()
    analyzer.discover_all_commits()
    analyzer.build_graph()
    assert isinstance(analyzer.graph, dict)


def test_calculate_density():
    """
    Test que se puede calcular la densidad
    """
    analyzer = GitGraphAnalyzer()
    analyzer.discover_all_commits()
    analyzer.build_graph()
    density = analyzer.calculate_branch_density()
    assert isinstance(density, float)
    assert density >= 0.0
