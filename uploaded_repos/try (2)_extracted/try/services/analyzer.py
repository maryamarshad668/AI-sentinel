import os
import subprocess
from radon.complexity import cc_visit, cc_rank
from radon.metrics import mi_visit, h_visit
from radon.raw import analyze
from typing import List, Dict


def get_python_files(folder_path: str) -> List[str]:
    """Walk a folder and return all .py file paths."""
    py_files = []
    for root, dirs, files in os.walk(folder_path):
        # Skip virtual environments and hidden folders
        dirs[:] = [d for d in dirs if d not in ('venv', '.venv', '__pycache__', '.git', 'node_modules')]
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    return py_files


def get_churn_rate(filepath: str, repo_path: str) -> float:
    """Count how many times a file was modified in the last 90 days via git log."""
    try:
        result = subprocess.run(
            ['git', 'log', '--oneline', '--since=90 days ago', '--', filepath],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        lines = result.stdout.strip().split('\n')
        count = len([l for l in lines if l.strip()])
        return float(count)
    except Exception:
        return 0.0


def analyze_file(filepath: str, repo_path: str) -> Dict:
    """Extract all code metrics from a single Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()

        if not source.strip():
            return None

        # --- Lines of Code ---
        raw = analyze(source)
        loc = raw.lloc  # logical lines of code

        # --- Cyclomatic Complexity ---
        try:
            cc_results = cc_visit(source)
            if cc_results:
                cc_scores = [block.complexity for block in cc_results]
                cc_avg = sum(cc_scores) / len(cc_scores)
                cc_max = max(cc_scores)
            else:
                cc_avg = 1.0
                cc_max = 1.0
        except Exception:
            cc_avg = 1.0
            cc_max = 1.0

        # --- Halstead Metrics ---
        try:
            h_results = h_visit(source)
            if h_results:
                halstead_effort = h_results[0].effort
            else:
                halstead_effort = 0.0
        except Exception:
            halstead_effort = 0.0

        # --- Maintainability Index ---
        try:
            mi = mi_visit(source, multi=True)
            maintainability_index = mi if isinstance(mi, float) else 50.0
        except Exception:
            maintainability_index = 50.0

        # --- Code Churn ---
        churn_rate = get_churn_rate(filepath, repo_path)

        return {
            "filepath": filepath,
            "filename": os.path.basename(filepath),
            "loc": loc,
            "cc_avg": round(cc_avg, 2),
            "cc_max": round(cc_max, 2),
            "halstead_effort": round(halstead_effort, 2),
            "maintainability_index": round(maintainability_index, 2),
            "churn_rate": churn_rate,
        }

    except Exception as e:
        print(f"⚠️  Could not analyze {filepath}: {e}")
        return None


def analyze_codebase(folder_path: str) -> List[Dict]:
    """Analyze all Python files in a folder and return metrics for each."""
    py_files = get_python_files(folder_path)

    if not py_files:
        return []

    results = []
    for filepath in py_files:
        metrics = analyze_file(filepath, folder_path)
        if metrics:
            results.append(metrics)

    print(f"✅ Analyzed {len(results)} Python files")
    return results