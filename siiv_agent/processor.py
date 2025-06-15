import subprocess
import sys
import logging
from typing import List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_tool(tool: str, file_path: str) -> Tuple[int, str, str]:
    """Run a specified tool on the given file and return the result."""
    logging.info(f"Running {tool} on {file_path}")
    result = subprocess.run([tool, file_path], capture_output=True, text=True)
    
    if result.returncode != 0:
        logging.error(f"{tool} failed with code {result.returncode}")
        logging.error(result.stderr)
    
    return result.returncode, result.stdout, result.stderr

def run_black(file_path: str) -> Tuple[int, str, str]:
    return run_tool("black", file_path)

def run_isort(file_path: str) -> Tuple[int, str, str]:
    return run_tool("isort", file_path)

def run_mypy(file_path: str) -> Tuple[int, str, str]:
    return run_tool("mypy", file_path)

def run_ruff(file_path: str) -> Tuple[int, str, str]:
    return run_tool("ruff", "check", file_path)

def run_pytest(file_path: str) -> Tuple[int, str, str]:
    return run_tool("pytest", file_path)

def run_all(file_paths: List[str]) -> None:
    """Run all configured tools on the provided list of file paths."""
    for file_path in file_paths:
        results = {
            "black": run_black(file_path),
            "isort": run_isort(file_path),
            "mypy": run_mypy(file_path),
            "ruff": run_ruff(file_path),
            "pytest": run_pytest(file_path)
        }
        for tool, result in results.items():
            logging.info(f"{tool} result for {file_path}: {result}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Please provide at least one file or directory to process.")
        sys.exit(1)

    file_paths = sys.argv[1:]
    run_all(file_paths)
